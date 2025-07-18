#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for splitter command-line interfaces."""

from __future__ import annotations

import importlib.metadata as importlib_metadata
import sys
import types
from contextlib import redirect_stderr, redirect_stdout
from inspect import getfile
from io import StringIO
from pathlib import Path

import pytest

from pipescaler.common import CommandLineInterface
from pipescaler.common.file import get_temp_file_path
from pipescaler.common.testing import run_cli_with_args
from pipescaler.image.cli import ImageSplittersCli
from pipescaler.image.cli.splitters import AlphaSplitterCli
from pipescaler.image.core.cli import ImageSplitterCli
from pipescaler.image.core.operators import ImageSplitter
from pipescaler.testing.file import get_test_infile_path


@pytest.mark.parametrize(
    ("cli", "args", "infile"),
    [
        (AlphaSplitterCli, "", "RGBA"),
    ],
)
def test(cli: type[CommandLineInterface], args: str, infile: str) -> None:
    """Run splitter CLI end-to-end."""
    input_path = get_test_infile_path(infile)

    with get_temp_file_path(".png") as output_path_1:
        with get_temp_file_path(".png") as output_path_2:
            run_cli_with_args(
                cli, f"{args} {input_path} {output_path_1} {output_path_2}"
            )


@pytest.mark.parametrize(
    "commands",
    [
        (AlphaSplitterCli,),
        (ImageSplittersCli,),
        (ImageSplittersCli, AlphaSplitterCli),
    ],
)
def test_help(commands: tuple[type[CommandLineInterface], ...]) -> None:
    """Ensure help is displayed for splitters CLI."""
    subcommands = " ".join(f"{command.name()}" for command in commands[1:])

    stdout = StringIO()
    stderr = StringIO()
    try:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(commands[0], f"{subcommands} -h")
    except SystemExit as error:
        assert error.code == 0
        assert stdout.getvalue().startswith(
            f"usage: {Path(getfile(commands[0])).name} {subcommands}"
        )
        assert stderr.getvalue() == ""


@pytest.mark.parametrize(
    "commands",
    [
        (AlphaSplitterCli,),
        (ImageSplittersCli,),
        (ImageSplittersCli, AlphaSplitterCli),
    ],
)
def test_usage(commands: tuple[type[CommandLineInterface], ...]):
    """Ensure usage error is produced for missing arguments."""
    subcommands = " ".join(f"{command.name()}" for command in commands[1:])

    stdout = StringIO()
    stderr = StringIO()
    try:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(commands[0], subcommands)
    except SystemExit as error:
        assert error.code == 2
        assert stdout.getvalue() == ""
        assert stderr.getvalue().startswith(
            f"usage: {Path(getfile(commands[0])).name} {subcommands}"
        )


def test_entry_point_discovery(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure additional splitters are discovered via entry points."""

    class DummySplitter(ImageSplitter):
        pass

    class DummyCli(ImageSplitterCli):
        @classmethod
        def splitter(cls) -> type[DummySplitter]:
            return DummySplitter

    module = types.ModuleType("dummy_module")
    setattr(module, "DummyCli", DummyCli)
    sys.modules["dummy_module"] = module

    ep = importlib_metadata.EntryPoint(
        name="dummy",
        value="dummy_module:DummyCli",
        group="pipescaler.image.splitters",
    )
    dummy_eps = importlib_metadata.EntryPoints((ep,))

    def fake_entry_points(*, group: str):
        if group == "pipescaler.image.splitters":
            return dummy_eps
        return importlib_metadata.EntryPoints(())

    monkeypatch.setattr(
        "pipescaler.image.cli.image_splitters_cli.entry_points", fake_entry_points
    )

    splitters = ImageSplittersCli.splitters()
    assert splitters["dummy"] is DummyCli
