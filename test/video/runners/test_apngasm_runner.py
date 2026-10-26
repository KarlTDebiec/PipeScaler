#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ApngasmRunner."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest
from PIL import Image

from pipescaler.common import ExecutableNotFoundError
from pipescaler.common.file import get_temp_file_path
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture
from pipescaler.testing.mark import skip_if_ci, skip_if_codex, xfail_if_platform
from pipescaler.video.runners import ApngasmRunner


@parametrized_fixture(
    cls=ApngasmRunner,
    params=[
        {},
    ],
)
def runner(request: pytest.FixtureRequest) -> ApngasmRunner:
    """Pytest fixture that provides an ApngasmRunner instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured ApngasmRunner instance
    """
    return ApngasmRunner(**request.param)


@pytest.mark.parametrize(
    "input_filenames",
    [
        skip_if_codex(
            skip_if_ci(xfail_if_platform({"Windows"}, ExecutableNotFoundError))
        )(["1", "L", "RGB", "RGBA"]),
    ],
)
def test(input_filenames: list[str], runner: ApngasmRunner):
    """Test ApngasmRunner creating animated PNG from multiple images.

    Arguments:
        input_filenames: List of input image filenames
        runner: ApngasmRunner fixture instance
    """
    input_paths = [get_test_input_path(i) for i in input_filenames]

    with get_temp_file_path(".png") as output_path:
        runner.run(input_paths, output_path)

        image = Image.open(output_path)
        assert image.is_animated
        assert image.n_frames == 4
        assert image.info["loop"] == 0
        assert image.info["duration"] == 100.0


def test_repr_round_trip():
    """Test ApngasmRunner repr round-trip recreation."""
    runner = ApngasmRunner(arguments=("1", "2", "3"), timeout=1)
    recreated = eval(repr(runner))
    assert recreated.arguments == runner.arguments
    assert recreated.timeout == runner.timeout


@pytest.mark.parametrize("multiple_inputs", [False, True])
def test_argument_paths_are_preserved(
    monkeypatch: pytest.MonkeyPatch, multiple_inputs: bool
):
    """Preserve one path or each ordered frame path as a separate argument.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        multiple_inputs: whether to provide multiple frame paths
    """
    executable_path = Path("C:/Program Files/O'Brien/{tools}/apngasm.exe")
    input_paths = [Path(r"C:\input images\O'Brien\{frame 1}.png")]
    if multiple_inputs:
        input_paths.append(Path(r"C:\input images\O'Brien\{frame 2}.png"))
    output_path = Path(r"C:\output images\{result}.png")
    arguments = ("--loops", "0", r"C:\custom options\{value}")
    command_runner = Mock(return_value=(0, "", ""))
    monkeypatch.setattr(
        "pipescaler.core.runner.val_executable", lambda *_args: executable_path
    )
    monkeypatch.setattr("pipescaler.core.runner.run_command", command_runner)

    runner = ApngasmRunner(arguments=arguments, timeout=7)
    runner(input_paths if multiple_inputs else input_paths[0], output_path)

    command_runner.assert_called_once_with(
        [
            str(executable_path),
            "-o",
            str(output_path),
            *(str(path) for path in input_paths),
            *arguments,
        ],
        timeout=7,
    )


def test_empty_input_sequence_is_rejected():
    """Reject empty frame sequences before attempting to find an executable."""
    with pytest.raises(ValueError, match="At least one input frame path"):
        ApngasmRunner().run([], Path("output.png"))
