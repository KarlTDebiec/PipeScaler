#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for PotraceRunner."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest
from PIL import Image

from pipescaler.common.file import get_temp_file_path
from pipescaler.image.runners import PotraceRunner
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=PotraceRunner,
    params=[
        {},
    ],
)
def runner(request: pytest.FixtureRequest) -> PotraceRunner:
    """Pytest fixture that provides a PotraceRunner instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured PotraceRunner instance
    """
    return PotraceRunner(**request.param)


@pytest.mark.parametrize(
    "input_filename",
    [
        "L",
    ],
)
def test(input_filename: str, runner: PotraceRunner):
    """Test PotraceRunner converting bitmap images to SVG.

    Arguments:
        input_filename: Input image filename
        runner: PotraceRunner fixture instance
    """
    input_path = get_test_input_path(input_filename)

    with get_temp_file_path(".bmp") as bmp_path:
        Image.open(input_path).save(bmp_path)
        with get_temp_file_path(".svg") as output_path:
            runner.run(bmp_path, output_path)


def test_repr_round_trip():
    """Test PotraceRunner repr round-trip recreation."""
    runner = PotraceRunner(arguments=("-b", "svg"), timeout=1)
    recreated = eval(repr(runner))
    assert recreated.arguments == runner.arguments
    assert recreated.timeout == runner.timeout


def test_argument_paths_are_preserved(monkeypatch: pytest.MonkeyPatch):
    """Pass executable, input, output, and custom paths as unchanged tokens.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    executable_path = Path("C:/Program Files/O'Brien/{tools}/potrace.exe")
    input_path = Path(r"C:\input images\O'Brien\{source}.bmp")
    output_path = Path(r"C:\output images\{result}.svg")
    arguments = ("--backend", "svg", "--opaque", r"C:\custom options\{value}")
    command_runner = Mock(return_value=(0, "", ""))
    monkeypatch.setattr(
        "pipescaler.core.runner.val_executable", lambda *_args: executable_path
    )
    monkeypatch.setattr("pipescaler.core.runner.run_command", command_runner)

    PotraceRunner(arguments=arguments, timeout=7)(input_path, output_path)

    command_runner.assert_called_once_with(
        [str(executable_path), str(input_path), *arguments, "-o", str(output_path)],
        timeout=7,
    )
