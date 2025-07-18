#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for processor command-line interfaces."""

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
from pipescaler.core.cli import UtilityCli
from pipescaler.core.utility import Utility
from pipescaler.image.cli import ImageUtilitiesCli
from pipescaler.image.cli.utilities import EsrganSerializerCli, WaifuSerializerCli
from pipescaler.testing.file import get_test_model_infile_path
from pipescaler.testing.mark import skip_if_ci, skip_if_codex


@pytest.mark.parametrize(
    ("cli", "args", "infile"),
    [
        skip_if_codex(skip_if_ci())(
            EsrganSerializerCli,
            "",
            "ESRGAN/1x_BC1-smooth2",
        ),
        skip_if_codex(skip_if_ci())(
            WaifuSerializerCli,
            "upconv7",
            "WaifuUpConv7/a-2-1.json",
        ),
    ],
)
def test(cli: type[CommandLineInterface], args: str, infile: str) -> None:
    """Run image utility CLI end-to-end."""
    input_path = get_test_model_infile_path(infile)

    with get_temp_file_path(".pth") as output_path:
        run_cli_with_args(cli, f"{args} {input_path} {output_path}")


@pytest.mark.parametrize(
    "commands",
    [
        (EsrganSerializerCli,),
        (WaifuSerializerCli,),
        (ImageUtilitiesCli,),
        (ImageUtilitiesCli, EsrganSerializerCli),
        (ImageUtilitiesCli, WaifuSerializerCli),
    ],
)
def test_help(commands: tuple[type[CommandLineInterface], ...]) -> None:
    """Ensure help is displayed for utilities CLI."""
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
        (EsrganSerializerCli,),
        (WaifuSerializerCli,),
        (ImageUtilitiesCli,),
        (ImageUtilitiesCli, EsrganSerializerCli),
        (ImageUtilitiesCli, WaifuSerializerCli),
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
    """Ensure additional utilities are discovered via entry points."""

    class DummyUtility(Utility):
        pass

    class DummyCli(UtilityCli):
        @classmethod
        def utility(cls) -> type[DummyUtility]:
            return DummyUtility

    module = types.ModuleType("dummy_module")
    setattr(module, "DummyCli", DummyCli)
    sys.modules["dummy_module"] = module

    ep = importlib_metadata.EntryPoint(
        name="dummy",
        value="dummy_module:DummyCli",
        group="pipescaler.image.utilities",
    )
    dummy_eps = importlib_metadata.EntryPoints((ep,))

    def fake_entry_points(*, group: str):
        if group == "pipescaler.image.utilities":
            return dummy_eps
        return importlib_metadata.EntryPoints(())

    monkeypatch.setattr(
        "pipescaler.image.cli.image_utilities_cli.entry_points", fake_entry_points
    )

    utilities = ImageUtilitiesCli.utilities()
    assert utilities["dummy"] is DummyCli
