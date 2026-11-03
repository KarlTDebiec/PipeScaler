#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Exercise external CLI distributions through real metadata and root dispatch."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from pipescaler.common import package_root


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

    result = _run_extension_cli(extension_site, "--help")

    assert result.returncode != 0
    assert "sample-extension" in result.stderr
    assert "echo" in result.stderr
    assert "pipescaler.cli.commands" in result.stderr


def test_extension_subtree_preserves_domain_argument(extension_site: Path):
    """Keep custom container routing separate from both ancestors and leaf data.

    Arguments:
        extension_site: isolated installed extension distribution
    """
    result = _run_extension_cli(extension_site, "tools", "echo", "example.com")

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "example.com"


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

    processor = _run_extension_cli(
        extension_site,
        "image",
        "process",
        "externalmode",
        "--mode",
        "RGB",
        str(input_path),
        str(rgb_path),
    )
    assert processor.returncode == 0, processor.stderr
    with Image.open(rgb_path) as image:
        assert image.mode == "RGB"
        assert image.size == (2, 3)

    merger = _run_extension_cli(
        extension_site,
        "image",
        "merge",
        "externaldiff",
        str(rgb_path),
        str(rgb_path),
        str(diff_path),
    )
    assert merger.returncode == 0, merger.stderr
    with Image.open(diff_path) as image:
        assert not np.asarray(image).any()

    splitter = _run_extension_cli(
        extension_site,
        "image",
        "split",
        "externalalpha",
        str(input_path),
        str(color_path),
        str(alpha_path),
    )
    assert splitter.returncode == 0, splitter.stderr
    with Image.open(alpha_path) as image:
        assert image.getpixel((0, 0)) == 123


def test_root_extension_preserves_domain_argument(extension_site: Path):
    """Keep an extension's domain argument separate from root routing metadata.

    Arguments:
        extension_site: isolated installed extension distribution
    """
    result = _run_extension_cli(extension_site, "echo", "extension works")

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "extension works"


@pytest.fixture
def extension_site(tmp_path: Path) -> Path:
    """Provide an installed-layout distribution exposing all supported entry groups.

    Arguments:
        tmp_path: temporary directory for the isolated extension installation
    Returns:
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
    return site_dir_path


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
    extension_site: Path, arguments: list[str], command_name: str, builtin_name: str
):
    """Expose extensions and built-ins together at every supported command location.

    Arguments:
        extension_site: isolated installed extension distribution
        arguments: help command tokens
        command_name: extension expected in the help output
        builtin_name: existing command that remains available
    """
    result = _run_extension_cli(extension_site, *arguments)

    assert result.returncode == 0, result.stderr
    assert command_name in result.stdout
    assert builtin_name in result.stdout


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

    result = _run_extension_cli(extension_site, *arguments)

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == (
        "domain value|subcommand value|processor value|merger value|splitter value"
    )


def _run_extension_cli(
    site_dir_path: Path, *arguments: str
) -> subprocess.CompletedProcess[str]:
    """Run PipeScaler with a separate distribution installed on its search path.

    Arguments:
        site_dir_path: directory containing extension modules and installed metadata
        *arguments: command-line arguments passed through root dispatch
    Returns:
        captured command output and exit status
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([str(site_dir_path), str(package_root.parent)])
    return subprocess.run(
        [
            sys.executable,
            "-c",
            "from pipescaler.cli.pipescaler_cli import PipeScalerCli; "
            "PipeScalerCli.main()",
            *arguments,
        ],
        cwd=package_root.parent,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )
