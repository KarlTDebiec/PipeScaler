#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for TexconvRunner."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest
from PIL import Image

from pipescaler.common import UnsupportedPlatformError
from pipescaler.common.file import get_temp_file_path
from pipescaler.image.runners import TexconvRunner
from pipescaler.testing.file import get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture

xfail_texconv_unavailable = pytest.mark.xfail(
    raises=(FileNotFoundError, UnsupportedPlatformError)
)
"""Expected failure when texconv is unavailable on the test runner."""


@parametrized_fixture(
    cls=TexconvRunner,
    params=[
        {},
    ],
)
def runner(request: pytest.FixtureRequest) -> TexconvRunner:
    """Pytest fixture that provides a TexconvRunner instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured TexconvRunner instance
    """
    return TexconvRunner(**request.param)


@pytest.mark.parametrize(
    "input_filename",
    [
        pytest.param("1", marks=xfail_texconv_unavailable),
        pytest.param("L", marks=xfail_texconv_unavailable),
        pytest.param("LA", marks=xfail_texconv_unavailable),
        pytest.param("RGB", marks=xfail_texconv_unavailable),
        pytest.param("RGBA", marks=xfail_texconv_unavailable),
        pytest.param("PL", marks=xfail_texconv_unavailable),
        pytest.param("PLA", marks=xfail_texconv_unavailable),
        pytest.param("PRGB", marks=xfail_texconv_unavailable),
        pytest.param("PRGBA", marks=xfail_texconv_unavailable),
    ],
)
def test(input_filename: str, runner: TexconvRunner):
    """Test TexconvRunner converting images to DDS format.

    Arguments:
        input_filename: Input image filename
        runner: TexconvRunner fixture instance
    """
    input_path = get_test_input_path(input_filename)

    with get_temp_file_path(".dds") as output_path:
        runner.run(input_path, output_path)

        with Image.open(input_path) as input_img:
            with Image.open(output_path) as output_img:
                assert output_img.mode == "RGBA"
                assert output_img.size == input_img.size


def test_repr_round_trip():
    """Test TexconvRunner repr round-trip recreation."""
    runner = TexconvRunner(arguments=("-y",), timeout=1)
    recreated = eval(repr(runner))
    assert recreated.arguments == runner.arguments
    assert recreated.timeout == runner.timeout


def test_argument_paths_and_output_rename(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Preserve path tokens and rename texconv's generated output to the target.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary test directory
    """
    executable_path = Path("C:/Program Files/O'Brien/{tools}/texconv.exe")
    input_path = tmp_path / "O'Brien {input}.png"
    output_dir_path = tmp_path / "output directory"
    output_dir_path.mkdir()
    output_path = output_dir_path / "{output}.dds"
    generated_path = output_path.with_stem(input_path.stem)
    generated_path.write_bytes(b"generated image")
    arguments = ("-y", "-ft", "DDS", r"C:\custom options\{value}")
    command_runner = Mock(return_value=(0, "", ""))
    monkeypatch.setattr(
        "pipescaler.core.runner.val_executable", lambda *_args: executable_path
    )
    monkeypatch.setattr(
        "pipescaler.image.runners.texconv_runner.run_command", command_runner
    )

    TexconvRunner(arguments=arguments, timeout=7).run(input_path, output_path)

    command_runner.assert_called_once_with(
        [str(executable_path), *arguments, "-o", str(output_dir_path), str(input_path)],
        timeout=7,
    )
    assert output_path.read_bytes() == b"generated image"
    assert not generated_path.exists()
