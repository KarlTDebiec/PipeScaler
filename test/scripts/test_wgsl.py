#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Regress GPU-free WGSL formatting, validation, installation, and CI gating."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from shutil import copy2, copyfile

import pytest

from scripts.wgsl import (
    changes_require_checks,
    format_sources,
    install_tools,
    lint_sources,
    record_changes,
    source_paths,
)


@pytest.fixture
def checkout(tmp_path: Path) -> Path:
    """Create an isolated tracked-source checkout with the real installation pins.

    Arguments:
        tmp_path: temporary directory supplied by pytest
    Returns:
        initialized checkout with a tooling configuration
    """
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True)
    (tmp_path / "scripts").mkdir()
    copyfile(
        Path(__file__).resolve().parents[2] / "scripts/wgsl_tools.toml",
        tmp_path / "scripts/wgsl_tools.toml",
    )
    return tmp_path


@pytest.fixture
def tool_checkout(checkout: Path) -> Path:
    """Copy installed binaries into a fixture without downloading or needing a GPU.

    Arguments:
        checkout: temporary tracked-source checkout
    Returns:
        checkout with native shader tools and their installation stamp
    """
    source_dir_path = Path(__file__).resolve().parents[2] / "local/wgsl-tools"
    suffix = ".exe" if os.name == "nt" else ""
    names = ["installed.json", f"bin/naga{suffix}", f"bin/wgslfmt{suffix}"]
    if not all((source_dir_path / name).is_file() for name in names):
        message = "Run 'uv run python scripts/wgsl.py install' for native tool tests"
        if os.environ.get("PIPESCALER_REQUIRE_WGSL_TOOLS"):
            pytest.fail(message)
        pytest.skip(message)
    for name in names:
        dest_file_path = checkout / "local/wgsl-tools" / name
        dest_file_path.parent.mkdir(parents=True, exist_ok=True)
        copy2(source_dir_path / name, dest_file_path)
    return checkout


@pytest.mark.parametrize(
    "file_path, expected",
    [
        ("pipescaler/image/utilities/palette_match.wgsl", True),
        ("shader with spaces.wgsl", True),
        ("scripts/wgsl.py", True),
        ("scripts/wgsl_tools.toml", True),
        ("test/scripts/test_wgsl.py", True),
        ("pipescaler/image/utilities/palette_shader_matcher.py", True),
        (".github/workflows/wgsl.yml", True),
        (".gitattributes", True),
        ("pyproject.toml", True),
        ("uv.lock", True),
        ("README.md", False),
        ("pipescaler/image/utilities/palette_matcher.py", False),
    ],
)
def test_change_gate(file_path: str, expected: bool):
    """Run shader checks for sources and their tooling, skipping unrelated edits.

    Arguments:
        file_path: changed repository-relative path
        expected: whether the path affects shader checks
    """
    assert changes_require_checks([file_path]) is expected
    assert not changes_require_checks([])


@pytest.mark.parametrize("check", [False, True])
def test_formatter_rejects_invalid_source(tool_checkout: Path, check: bool):
    """Reject syntax errors even when the upstream formatter's write mode exits zero.

    Arguments:
        tool_checkout: checkout with installed native tools
        check: whether to check or write formatting
    """
    file_path = tool_checkout / "invalid.wgsl"
    file_path.write_text("fn main( {", encoding="utf-8")
    assert not format_sources(tool_checkout, [file_path], check=check)


def test_formatter_preserves_templates_and_is_idempotent(tool_checkout: Path):
    """Preserve comments and placeholders while checking without source mutations.

    Arguments:
        tool_checkout: checkout with installed native tools
    """
    file_path = tool_checkout / "shader with spaces.wgsl"
    original = (
        "// Template purpose\n@compute @workgroup_size(WGX,WGY,1)\n"
        "fn main(){let x=1u;}\n"
    )
    file_path.write_text(original, encoding="utf-8")
    original_bytes = file_path.read_bytes()

    assert not format_sources(tool_checkout, [file_path], check=True)
    assert file_path.read_bytes() == original_bytes
    assert format_sources(tool_checkout, [file_path])
    formatted = file_path.read_bytes()
    assert b"// Template purpose" in formatted
    assert b"WGX" in formatted and b"WGY" in formatted
    assert format_sources(tool_checkout, [file_path], check=True)
    assert format_sources(tool_checkout, [file_path])
    assert file_path.read_bytes() == formatted
    assert lint_sources(tool_checkout, [file_path])


def test_install_uses_pins_and_reuses_binaries(
    checkout: Path, monkeypatch: pytest.MonkeyPatch
):
    """Install locked versions once and reuse only complete matching installations.

    Arguments:
        checkout: temporary tracked-source checkout
        monkeypatch: fixture for intercepting installation subprocesses
    """
    commands: list[list[str]] = []

    def install(command: list[str], *, check: bool) -> subprocess.CompletedProcess[str]:
        """Capture installer commands and create native-tool stand-ins.

        Arguments:
            command: toolchain or Cargo installation command
            check: whether subprocess failures should propagate
        Returns:
            successful installer result
        """
        assert check
        commands.append(command)
        if command[0] == "cargo":
            name = "naga" if "naga-cli" in command else "wgslfmt"
            suffix = ".exe" if os.name == "nt" else ""
            file_path = checkout / "local/wgsl-tools/bin" / f"{name}{suffix}"
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("fixture", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("scripts.wgsl.which", lambda name: name)
    monkeypatch.setattr("scripts.wgsl.subprocess.run", install)
    install_tools(checkout)
    assert len(commands) == 3
    assert commands[0][:3] == ["rustup", "toolchain", "install"]
    for command in commands[1:]:
        assert "--locked" in command and "--root" in command
        assert command[1] == f"+{commands[0][3]}"
    assert commands[1][-2:] == ["--version", "=27.0.0"]
    assert commands[2][-3:] == [
        "--rev",
        "8a2e7eab99891ab9d7a405561cb1559127767897",
        "wgslfmt",
    ]
    install_tools(checkout)
    assert len(commands) == 3
    (checkout / "local/wgsl-tools/installed.json").unlink()
    install_tools(checkout)
    assert len(commands) == 6


@pytest.mark.parametrize("source", ["fn main( {", "fn main() { let x: u32 = true; }"])
def test_invalid_shaders_fail_with_source_diagnostics(
    tool_checkout: Path, source: str, capsys: pytest.CaptureFixture[str]
):
    """Report parsing and type errors against the maintained file without editing it.

    Arguments:
        tool_checkout: checkout with installed native tools
        source: malformed or type-invalid WGSL source
        capsys: fixture for inspecting checker diagnostics
    """
    file_path = tool_checkout / "invalid.wgsl"
    file_path.write_text(source, encoding="utf-8")
    assert not lint_sources(tool_checkout, [file_path])
    assert file_path.read_text(encoding="utf-8") == source
    output = capsys.readouterr().out
    assert str(file_path) in output
    assert "pipescaler-wgsl-" not in output


def test_missing_tools_are_actionable(checkout: Path):
    """Report the installation command when a shader tool is unavailable.

    Arguments:
        checkout: temporary tracked-source checkout
    """
    file_path = checkout / "shader.wgsl"
    file_path.write_text("fn main() {}", encoding="utf-8")
    with pytest.raises(FileNotFoundError, match="scripts/wgsl.py install"):
        lint_sources(checkout, [file_path])


def test_plain_and_template_shaders_validate(
    tool_checkout: Path, capsys: pytest.CaptureFixture[str]
):
    """Validate plain WGSL once and both actual palette workgroup configurations.

    Arguments:
        tool_checkout: checkout with installed native tools
        capsys: fixture for inspecting the validation summary
    """
    plain_file_path = tool_checkout / "plain.wgsl"
    plain_file_path.write_text(
        "@compute @workgroup_size(1) fn main() {}", encoding="utf-8"
    )
    template_file_path = tool_checkout / "template.wgsl"
    template_file_path.write_text(
        "@compute @workgroup_size(WGX, WGY, 1) fn main() {}", encoding="utf-8"
    )
    assert lint_sources(tool_checkout, [plain_file_path, template_file_path])
    assert "3 variants, passed=True" in capsys.readouterr().out


def test_record_changes_uses_diff_and_runs_on_missing_history(
    checkout: Path, monkeypatch: pytest.MonkeyPatch
):
    """Skip irrelevant diffs, retain deleted shader paths, and handle missing bases.

    Arguments:
        checkout: temporary tracked-source checkout
        monkeypatch: fixture for setting Actions environment values
    """
    shader_file_path = checkout / "shader.wgsl"
    shader_file_path.write_text("fn main() {}", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=checkout, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.com",
            "commit",
            "--no-gpg-sign",
            "--quiet",
            "-m",
            "fixture",
        ],
        cwd=checkout,
        check=True,
    )
    base = (
        subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=checkout)
        .decode()
        .strip()
    )
    output_file_path = checkout / "output.txt"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output_file_path))
    monkeypatch.setenv("GITHUB_EVENT_NAME", "pull_request")
    monkeypatch.setenv("BASE_SHA", base)
    monkeypatch.setenv("HEAD_SHA", "HEAD")
    record_changes(checkout)
    assert output_file_path.read_text(encoding="utf-8") == "relevant=false\n"
    shader_file_path.rename(checkout / "renamed.txt")
    subprocess.run(["git", "add", "--all"], cwd=checkout, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.com",
            "commit",
            "--no-gpg-sign",
            "--quiet",
            "-m",
            "rename",
        ],
        cwd=checkout,
        check=True,
    )
    record_changes(checkout)
    assert output_file_path.read_text(encoding="utf-8").endswith("relevant=true\n")
    monkeypatch.setenv("BASE_SHA", "0" * 40)
    record_changes(checkout)
    assert output_file_path.read_text(encoding="utf-8").endswith("relevant=true\n")
    monkeypatch.setenv("BASE_SHA", "missing-revision")
    record_changes(checkout)
    assert output_file_path.read_text(encoding="utf-8").endswith("relevant=true\n")


def test_source_selection(checkout: Path):
    """Select tracked sources with spaces, preserve untracked files, and reject escapes.

    Arguments:
        checkout: temporary tracked-source checkout
    """
    file_path = checkout / "shader with spaces.wgsl"
    file_path.write_text("fn main() {}", encoding="utf-8")
    ignored_file_path = checkout / "untracked.wgsl"
    ignored_file_path.write_text("ignored", encoding="utf-8")
    subprocess.run(["git", "add", file_path.name], cwd=checkout, check=True)
    assert source_paths(checkout) == [file_path]
    assert source_paths(checkout, [ignored_file_path]) == [ignored_file_path]
    for path in (Path("../outside.wgsl"), Path("scripts/wgsl_tools.toml")):
        with pytest.raises(ValueError, match="Unsupported project WGSL"):
            source_paths(checkout, [path])
    file_path.unlink()
    assert source_paths(checkout) == []
    assert format_sources(checkout, check=True)
    assert lint_sources(checkout)
    with pytest.raises(FileNotFoundError):
        source_paths(checkout, [file_path])
