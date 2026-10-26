#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for PngquantRunner."""

from __future__ import annotations

from os.path import getsize
from pathlib import Path
from unittest.mock import Mock

import pytest
from PIL import Image

from pipescaler.common import ExecutableNotFoundError
from pipescaler.common.file import get_temp_file_path
from pipescaler.image.runners import PngquantRunner
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture
from pipescaler.testing.mark import xfail_if_platform


@parametrized_fixture(
    cls=PngquantRunner,
    params=[
        {},
    ],
)
def runner(request: pytest.FixtureRequest) -> PngquantRunner:
    """Pytest fixture that provides a PngquantRunner instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured PngquantRunner instance
    """
    return PngquantRunner(**request.param)


@pytest.mark.parametrize(
    "input_filename",
    [
        xfail_if_platform({"Windows"}, ExecutableNotFoundError)("RGB"),
    ],
)
def test(input_filename: str, runner: PngquantRunner):
    """Test PngquantRunner compressing PNG images.

    Arguments:
        input_filename: Input image filename
        runner: PngquantRunner fixture instance
    """
    input_path = get_test_input_path(input_filename)

    with get_temp_file_path(".png") as output_path:
        runner.run(input_path, output_path)

        with Image.open(input_path) as input_img:
            with Image.open(output_path) as output_img:
                assert output_img.mode in (input_img.mode, "P")
                assert output_img.size == input_img.size
                assert getsize(output_path) <= getsize(input_path)


def test_repr_round_trip():
    """Test PngquantRunner repr round-trip recreation."""
    runner = PngquantRunner(arguments=("--quality", "1-10"), timeout=1)
    recreated = eval(repr(runner))
    assert recreated.arguments == runner.arguments
    assert recreated.timeout == runner.timeout


@pytest.mark.parametrize("exitcode", [0, 98, 99])
def test_argument_paths_and_fallback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, exitcode: int
):
    """Preserve argument boundaries and copy input for pngquant fallback codes.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary test directory
        exitcode: pngquant exit code to simulate
    """
    executable_path = Path("C:/Program Files/O'Brien/{tools}/pngquant.exe")
    input_path = tmp_path / "O'Brien {input}.png"
    output_path = tmp_path / "O'Brien {output}.png"
    input_path.write_bytes(b"input image bytes")
    arguments = ("--quality", "1-10", r"C:\custom options\{value}")
    command_runner = Mock(return_value=(exitcode, "", ""))
    monkeypatch.setattr(
        "pipescaler.core.runner.val_executable", lambda *_args: executable_path
    )
    monkeypatch.setattr(
        "pipescaler.image.runners.pngquant_runner.run_command", command_runner
    )

    PngquantRunner(arguments=arguments, timeout=7)(input_path, output_path)

    command_runner.assert_called_once_with(
        [
            str(executable_path),
            *arguments,
            "--output",
            str(output_path),
            str(input_path),
        ],
        acceptable_exitcodes=[0, 98, 99],
        timeout=7,
    )
    if exitcode in (98, 99):
        assert output_path.read_bytes() == input_path.read_bytes()
    else:
        assert not output_path.exists()
