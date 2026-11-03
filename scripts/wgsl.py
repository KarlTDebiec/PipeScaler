#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Install pinned WGSL tools, format sources, and validate shaders without a GPU."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import tempfile
import tomllib
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from shutil import which

__all__ = [
    "ToolSettings",
    "format_sources",
    "install_tools",
    "lint_sources",
    "main",
    "source_paths",
]


@dataclass(frozen=True)
class ToolSettings:
    """Exact tool sources and compiler shared by local and CI installations."""

    rust_version: str
    """Rust toolchain used to build both tools."""
    naga_version: str
    """Published naga-cli version matching the runtime compiler."""
    wgslfmt_revision: str
    """Full upstream commit containing wgslfmt and its dependency lockfile."""


def format_sources(
    root_dir_path: Path, file_paths: Sequence[Path] = (), *, check: bool = False
) -> bool:
    """Format maintained WGSL, preserving template identifiers, or only check it.

    Arguments:
        root_dir_path: checkout containing the pinned tool installation
        file_paths: explicit WGSL files, or every existing tracked WGSL source
        check: report formatting differences without writing source files
    Returns:
        whether every selected source satisfies the formatting policy
    Raises:
        FileNotFoundError: if tools are not installed or a selected file is missing
        ValueError: if a selected file is outside the checkout or is not WGSL
    """
    paths = source_paths(root_dir_path, file_paths)
    if not paths:
        print("WGSL formatting: no sources")
        return True
    command = [
        str(_tool_path(root_dir_path, "wgslfmt")),
        "--config",
        "indent_style=spaces",
        "--config",
        "indent_width=4",
    ]
    if not check:
        result = subprocess.run([*command, *map(str, paths)], check=False)
        if result.returncode:
            return False
    # Check after writing too: upstream write mode can report parse errors with exit 0
    result = subprocess.run([*command, "--check", *map(str, paths)], check=False)
    return result.returncode == 0


def install_tools(root_dir_path: Path):
    """Install locked Cargo tools into local/wgsl-tools, reusing matching binaries.

    Arguments:
        root_dir_path: checkout containing scripts/wgsl_tools.toml
    Raises:
        RuntimeError: if rustup is unavailable
        subprocess.CalledProcessError: if toolchain or Cargo installation fails
    """
    settings = _load_settings(root_dir_path)
    tools_dir_path = root_dir_path / "local/wgsl-tools"
    stamp_file_path = tools_dir_path / "installed.json"
    stamp = _installation_stamp(settings)
    if (
        stamp_file_path.is_file()
        and json.loads(stamp_file_path.read_text(encoding="utf-8")) == stamp
        and all(
            (tools_dir_path / "bin" / _executable_name(name)).is_file()
            for name in ("naga", "wgslfmt")
        )
    ):
        print("WGSL tools: pinned installation already available")
        return
    if which("rustup") is None:
        raise RuntimeError("Install Rust/rustup from https://rustup.rs, then retry")
    subprocess.run(
        [
            "rustup",
            "toolchain",
            "install",
            settings.rust_version,
            "--profile",
            "minimal",
            "--no-self-update",
        ],
        check=True,
    )
    command = [
        "cargo",
        f"+{settings.rust_version}",
        "install",
        "--locked",
        "--force",
        "--root",
        str(tools_dir_path),
    ]
    subprocess.run(
        [*command, "naga-cli", "--version", f"={settings.naga_version}"], check=True
    )
    subprocess.run(
        [
            *command,
            "--git",
            "https://github.com/wgsl-analyzer/wgsl-analyzer",
            "--rev",
            settings.wgslfmt_revision,
            "wgslfmt",
        ],
        check=True,
    )
    stamp_file_path.write_text(json.dumps(stamp, indent=2) + "\n", encoding="utf-8")


def lint_sources(root_dir_path: Path, file_paths: Sequence[Path] = ()) -> bool:
    """Parse and validate WGSL with Naga, expanding both palette shader variants.

    Temporary sources retain line numbers; diagnostics identify the maintained
    source and workgroup variant. No GPU adapter or device is requested.

    Arguments:
        root_dir_path: checkout containing the pinned tool installation
        file_paths: explicit WGSL files, or every existing tracked WGSL source
    Returns:
        whether every selected source and template variant passes validation
    Raises:
        FileNotFoundError: if tools are not installed or a selected file is missing
        ValueError: if a selected file is outside the checkout or is not WGSL
    """
    paths = source_paths(root_dir_path, file_paths)
    if not paths:
        print("WGSL validation: no sources")
        return True
    validator_file_path = _tool_path(root_dir_path, "naga")
    passed = True
    count = 0
    with tempfile.TemporaryDirectory(prefix="pipescaler-wgsl-") as directory:
        temporary_file_path = Path(directory) / "shader.wgsl"
        for file_path in paths:
            source = file_path.read_text(encoding="utf-8")
            variants = [("source", source)]
            if "WGX" in source or "WGY" in source:
                variants = [
                    (f"{x}x{y}", source.replace("WGX", str(x)).replace("WGY", str(y)))
                    for x, y in ((8, 1), (8, 8))
                ]
            for variant, expanded_source in variants:
                temporary_file_path.write_text(expanded_source, encoding="utf-8")
                result = subprocess.run(
                    [str(validator_file_path), str(temporary_file_path)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode:
                    print(f"{file_path} [{variant}]:")
                    print(
                        (result.stdout + result.stderr).replace(
                            str(temporary_file_path), str(file_path)
                        )
                    )
                    passed = False
                count += 1
    print(f"WGSL validation: {count} variants, passed={passed}")
    return passed


def main() -> int:
    """Dispatch development commands with concise failures and process exit status.

    Returns:
        zero on success, one on failed checks or installation
    """
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("install", help="install pinned tools using Rust/rustup")
    for command in ("format", "lint"):
        child = subparsers.add_parser(command)
        child.add_argument("files", nargs="*", type=Path)
        if command == "format":
            child.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root_dir_path = Path(__file__).resolve().parents[1]
    try:
        if args.command == "install":
            install_tools(root_dir_path)
        elif args.command == "format":
            return int(not format_sources(root_dir_path, args.files, check=args.check))
        else:
            return int(not lint_sources(root_dir_path, args.files))
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"WGSL: {exc}", file=sys.stderr)
        return 1
    return 0


def source_paths(root_dir_path: Path, file_paths: Sequence[Path] = ()) -> list[Path]:
    """Select WGSL files, excluding untracked files unless explicitly requested.

    Arguments:
        root_dir_path: checkout constraining selected paths
        file_paths: explicit files relative to the checkout, or tracked sources
    Returns:
        sorted, resolved source paths that still exist in the checkout
    Raises:
        FileNotFoundError: if an explicit file does not exist
        ValueError: if a file escapes the checkout or has an unsupported suffix
        subprocess.CalledProcessError: if tracked sources cannot be enumerated
    """
    root_dir_path = root_dir_path.resolve()
    paths = list(file_paths)
    if not paths:
        tracked = subprocess.check_output(
            ["git", "ls-files", "-z", "--", "*.wgsl"], cwd=root_dir_path
        ).decode("utf-8")
        paths = [Path(name) for name in tracked.split("\0") if name]
    selected = set()
    for path in paths:
        file_path = (root_dir_path / path).resolve()
        if not file_path.is_relative_to(root_dir_path) or file_path.suffix != ".wgsl":
            raise ValueError(f"Unsupported project WGSL source: {path}")
        if not file_path.is_file():
            if file_paths:
                raise FileNotFoundError(file_path)
            continue
        selected.add(file_path)
    return sorted(selected)


def _executable_name(name: str) -> str:
    """Get the platform-specific filename of an installed tool.

    Arguments:
        name: executable stem
    Returns:
        native executable filename
    """
    return f"{name}.exe" if os.name == "nt" else name


def _installation_stamp(settings: ToolSettings) -> dict[str, str]:
    """Identify the pinned tools and native platform for cache validation.

    Arguments:
        settings: pinned compiler and tool sources
    Returns:
        installation identity saved alongside the native binaries
    """
    return {
        **asdict(settings),
        "system": platform.system(),
        "machine": platform.machine(),
    }


def _load_settings(root_dir_path: Path) -> ToolSettings:
    """Read the exact installation pins from the shared configuration.

    Arguments:
        root_dir_path: checkout containing the tooling configuration
    Returns:
        pinned compiler and tool sources
    """
    with (root_dir_path / "scripts/wgsl_tools.toml").open("rb") as config_file:
        return ToolSettings(**tomllib.load(config_file))


def _tool_path(root_dir_path: Path, name: str) -> Path:
    """Find a checkout-local tool without falling back to another installed version.

    Arguments:
        root_dir_path: checkout containing local/wgsl-tools
        name: executable stem
    Returns:
        installed executable path
    Raises:
        FileNotFoundError: if the requested tool is not installed
    """
    file_path = root_dir_path / "local/wgsl-tools/bin" / _executable_name(name)
    stamp_file_path = root_dir_path / "local/wgsl-tools/installed.json"
    if (
        not file_path.is_file()
        or not stamp_file_path.is_file()
        or json.loads(stamp_file_path.read_text(encoding="utf-8"))
        != _installation_stamp(_load_settings(root_dir_path))
    ):
        raise FileNotFoundError("Run 'uv run python scripts/wgsl.py install' first")
    return file_path


if __name__ == "__main__":
    sys.exit(main())
