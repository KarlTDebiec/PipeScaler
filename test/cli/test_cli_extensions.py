#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Exercise external CLI distributions through real metadata and root dispatch."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Iterator
from contextlib import redirect_stdout
from importlib.metadata import Distribution, EntryPoint
from importlib.util import module_from_spec, spec_from_file_location
from io import StringIO
from logging import getLogger
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

import pipescaler.common.cli.entry_points as command_entries
from pipescaler.cli.pipescaler_cli import PipeScalerCli
from pipescaler.common import package_root
from pipescaler.common.testing import run_cli_with_args


def test_broken_extension_identifies_distribution(extension_site: Path):
    """Name the distribution and command when an installed extension cannot load.

    Arguments:
        extension_site: isolated installed extension distribution
    """
    metadata_path = (
        extension_site / "sample_extension-1.0.dist-info" / "entry_points.txt"
    )
    metadata_path.write_text(
        "[pipescaler.cli.commands]\necho = missing_extension:EchoCli\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError) as raised:
        run_cli_with_args(PipeScalerCli, "--help")

    assert "sample-extension" in str(raised.value)
    assert "echo" in str(raised.value)
    assert "pipescaler.cli.commands" in str(raised.value)
    assert isinstance(raised.value.__cause__, ModuleNotFoundError)


def test_extension_subtree_preserves_domain_argument(
    extension_site: Path, capsys: pytest.CaptureFixture[str]
):
    """Keep custom container routing separate from both ancestors and leaf data.

    Arguments:
        extension_site: isolated installed extension distribution
        capsys: captured command output
    """
    run_cli_with_args(PipeScalerCli, 'tools echo "example.com"')

    assert capsys.readouterr().out.strip() == "example.com"


def test_installed_extension_starts_in_fresh_process(extension_site: Path):
    """Discover real installed metadata during fresh application startup.

    Arguments:
        extension_site: isolated installed extension distribution
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([str(extension_site), str(package_root.parent)])
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from pipescaler.cli.pipescaler_cli import PipeScalerCli; "
            "PipeScalerCli.main()",
            "echo",
            "extension works",
        ],
        cwd=package_root.parent,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "extension works"
    assert result.stderr == ""


def test_nested_extensions_execute(extension_site: Path, tmp_path: Path):
    """Run processor, merger, and splitter extensions through the root CLI.

    Arguments:
        extension_site: isolated installed extension distribution
        tmp_path: temporary directory for images
    """
    input_path = tmp_path / "input.png"
    rgb_path = tmp_path / "rgb.png"
    diff_path = tmp_path / "diff.png"
    alpha_path = tmp_path / "alpha.png"
    color_path = tmp_path / "color.png"
    Image.new("RGBA", (2, 3), (18, 52, 86, 123)).save(input_path)

    run_cli_with_args(
        PipeScalerCli,
        f'image process externalmode --mode RGB "{input_path}" "{rgb_path}"',
    )
    with Image.open(rgb_path) as image:
        assert image.mode == "RGB"
        assert image.size == (2, 3)

    run_cli_with_args(
        PipeScalerCli,
        f'image merge externaldiff "{rgb_path}" "{rgb_path}" "{diff_path}"',
    )
    with Image.open(diff_path) as image:
        assert not np.asarray(image).any()

    run_cli_with_args(
        PipeScalerCli,
        f'image split externalalpha "{input_path}" "{color_path}" "{alpha_path}"',
    )
    with Image.open(alpha_path) as image:
        assert image.getpixel((0, 0)) == 123


def test_root_extension_preserves_domain_argument(
    extension_site: Path, capsys: pytest.CaptureFixture[str]
):
    """Keep an extension's domain argument separate from root routing metadata.

    Arguments:
        extension_site: isolated installed extension distribution
        capsys: captured command output
    """
    run_cli_with_args(PipeScalerCli, 'echo "extension works"')

    assert capsys.readouterr().out.strip() == "extension works"


@pytest.fixture
def extension_site(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Provide an installed-layout distribution exposing all supported entry groups.

    Arguments:
        tmp_path: temporary directory for the isolated extension installation
        monkeypatch: fixture restoring discovery and loaded extension modules
    Yields:
        directory containing the extension and its distribution metadata
    """
    site_dir_path = tmp_path / "site-packages"
    site_dir_path.mkdir()
    (site_dir_path / "sample_extension.py").write_text(
        '''from pipescaler.common.cli import CommandLineInterface
from pipescaler.image.cli.processors import ModeCli
from pipescaler.image.cli.mergers import DiffMergerCli
from pipescaler.image.cli.splitters import AlphaSplitterCli

class EchoCli(CommandLineInterface):
    """Print a supplied value."""

    @classmethod
    def add_arguments_to_argparser(cls, parser):
        super().add_arguments_to_argparser(parser)
        parser.add_argument("domain")

    @classmethod
    def _main(cls, *, domain):
        print(domain)

class ToolsCli(CommandLineInterface):
    """Group extension commands under a custom subtree."""

    @classmethod
    def add_arguments_to_argparser(cls, parser):
        super().add_arguments_to_argparser(parser)
        subparsers = parser.add_subparsers(dest=cls.subcommand_dest(), required=True)
        EchoCli.argparser(subparsers=subparsers)

    @classmethod
    def _main(cls, **kwargs):
        command = kwargs.pop(cls.subcommand_dest())
        assert command == EchoCli.name()
        EchoCli._main(**kwargs)

class ExternalModeCli(ModeCli):
    """Convert image mode through an extension command."""

class ExternalDiffCli(DiffMergerCli):
    """Compare images through an extension command."""

class ExternalAlphaCli(AlphaSplitterCli):
    """Split alpha through an extension command."""
''',
        encoding="utf-8",
    )
    metadata_dir_path = site_dir_path / "sample_extension-1.0.dist-info"
    metadata_dir_path.mkdir()
    (metadata_dir_path / "METADATA").write_text(
        "Metadata-Version: 2.1\nName: sample-extension\nVersion: 1.0\n",
        encoding="utf-8",
    )
    (metadata_dir_path / "entry_points.txt").write_text(
        "[pipescaler.cli.commands]\necho = sample_extension:EchoCli\n"
        "tools = sample_extension:ToolsCli\n"
        "[pipescaler.cli.image.processors]\n"
        "externalmode = sample_extension:ExternalModeCli\n"
        "[pipescaler.cli.image.mergers]\n"
        "externaldiff = sample_extension:ExternalDiffCli\n"
        "[pipescaler.cli.image.splitters]\n"
        "externalalpha = sample_extension:ExternalAlphaCli\n",
        encoding="utf-8",
    )

    def installed_entry_points(*, group: str) -> list[EntryPoint]:
        """Load the current extension source and discover its real metadata.

        Arguments:
            group: requested command entry-point group
        Returns:
            installed entry points belonging to the requested group
        """
        if "sample_extension" not in sys.modules:
            spec = spec_from_file_location(
                "sample_extension", site_dir_path / "sample_extension.py"
            )
            assert spec is not None and spec.loader is not None
            module = module_from_spec(spec)
            monkeypatch.setitem(sys.modules, "sample_extension", module)
            spec.loader.exec_module(module)
        return [
            entry
            for entry in Distribution.at(metadata_dir_path).entry_points
            if entry.group == group
        ]

    monkeypatch.delitem(sys.modules, "sample_extension", raising=False)
    monkeypatch.setattr(command_entries, "entry_points", installed_entry_points)
    command_entries._load_cli_commands.cache_clear()
    root_logger = getLogger()
    handlers, level = root_logger.handlers[:], root_logger.level
    try:
        yield site_dir_path
    finally:
        command_entries._load_cli_commands.cache_clear()
        for handler in root_logger.handlers:
            if handler not in handlers:
                handler.close()
        root_logger.handlers[:] = handlers
        root_logger.setLevel(level)


@pytest.mark.parametrize(
    ("arguments", "command_name", "builtin_name"),
    [
        (["--help"], "echo", "image"),
        (["image", "process", "--help"], "externalmode", "resize"),
        (["image", "merge", "--help"], "externaldiff", "diffmerger"),
        (["image", "split", "--help"], "externalalpha", "alphasplitter"),
    ],
)
def test_extensions_appear_in_help(
    extension_site: Path,
    capsys: pytest.CaptureFixture[str],
    arguments: list[str],
    command_name: str,
    builtin_name: str,
):
    """Expose extensions and built-ins together at every supported command location.

    Arguments:
        extension_site: isolated installed extension distribution
        capsys: captured help output
        arguments: help command tokens
        command_name: extension expected in the help output
        builtin_name: existing command that remains available
    """
    with pytest.raises(SystemExit) as raised:
        run_cli_with_args(PipeScalerCli, " ".join(arguments))

    output = capsys.readouterr()
    assert raised.value.code == 0
    assert command_name in output.out
    assert builtin_name in output.out
    assert output.err == ""


@pytest.mark.parametrize(
    ("group", "base", "operation", "input_count"),
    [
        ("processors", "ModeCli", "process", 1),
        ("mergers", "DiffMergerCli", "merge", 2),
        ("splitters", "AlphaSplitterCli", "split", 1),
    ],
)
def test_nested_extension_preserves_selector_arguments(
    extension_site: Path,
    group: str,
    base: str,
    operation: str,
    input_count: int,
):
    """Pass ordinary selector-like argument names unchanged through every container.

    Arguments:
        extension_site: isolated installed extension distribution
        group: image extension group receiving the command
        base: concrete image CLI base used by the test extension
        operation: parent image command to invoke
        input_count: required input file count for the image CLI base
    """
    module_path = extension_site / "sample_extension.py"
    with module_path.open("a", encoding="utf-8") as module:
        module.write(f'''
class CollisionCli({base}):
    """Echo argument names that also describe command routing."""

    @classmethod
    def add_arguments_to_argparser(cls, parser):
        super().add_arguments_to_argparser(parser)
        for name in ("domain", "subcommand", "processor", "merger", "splitter"):
            parser.add_argument("--" + name, required=True)

    @classmethod
    def _main(cls, **kwargs):
        print("|".join(kwargs[name] for name in
              ("domain", "subcommand", "processor", "merger", "splitter")))
''')
    metadata_path = (
        extension_site / "sample_extension-1.0.dist-info" / "entry_points.txt"
    )
    metadata_path.write_text(
        f"[pipescaler.cli.image.{group}]\ncollision = sample_extension:CollisionCli\n",
        encoding="utf-8",
    )
    input_path = extension_site.parent / "input.png"
    Image.new("RGBA", (2, 3), (18, 52, 86, 123)).save(input_path)
    arguments = ["image", operation, "collision"]
    if group == "processors":
        arguments.extend(["--mode", "RGB"])
    arguments.extend([str(input_path)] * input_count)
    arguments.append(str(extension_site.parent / "output.png"))
    if group == "splitters":
        arguments.append(str(extension_site.parent / "alpha.png"))
    for name in ("domain", "subcommand", "processor", "merger", "splitter"):
        arguments.extend(["--" + name, name + " value"])

    stdout = StringIO()
    with redirect_stdout(stdout):
        run_cli_with_args(
            PipeScalerCli, " ".join(f'"{argument}"' for argument in arguments)
        )

    assert stdout.getvalue().strip() == (
        "domain value|subcommand value|processor value|merger value|splitter value"
    )
