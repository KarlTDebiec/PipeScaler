#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Real libapngasm encoding, decoding, validation, and failure tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import Mock

import numpy as np
import pytest
from apngasm_python.apngasm import APNGAsmBinder
from PIL import Image

from pipescaler.core.exceptions import PipeScalerError
from pipescaler.video.runners import ApngasmRunner
from pipescaler.video.runners.apngasm_runner import ApngasmFrame
from test.scripts.generate_apng_frames import write_apng_frames


def test_animated_inputs_rejected(tmp_path: Path):
    """Reject animated file and Pillow inputs instead of silently expanding frames.

    Arguments:
        tmp_path: temporary directory fixture
    """
    runner = ApngasmRunner()
    animated_path = tmp_path / "animated.png"
    runner.run(write_apng_frames(tmp_path / "frames"), animated_path)
    with pytest.raises(ValueError, match="static"):
        runner.run([animated_path], tmp_path / "output.png")
    with Image.open(animated_path) as animation:
        with pytest.raises(ValueError, match="static"):
            runner.run([animation], tmp_path / "output.png")


def test_duplicate_frames_preserve_total_duration(tmp_path: Path):
    """Preserve playback time when native optimization combines identical frames.

    Arguments:
        tmp_path: temporary directory fixture
    """
    frames = write_apng_frames(tmp_path / "frames")
    output_path = tmp_path / "duplicates.png"
    ApngasmRunner().run(
        [frames[0], frames[0], frames[1]],
        output_path,
        delays=[(1, 10), (1, 5), (3, 10)],
    )
    with Image.open(output_path) as animation:
        assert animation.n_frames == 2
        for index in range(2):
            animation.seek(index)
            assert animation.info["duration"] == pytest.approx(300)
            with Image.open(frames[index]) as expected:
                np.testing.assert_array_equal(
                    np.array(animation.convert("RGBA")), np.array(expected)
                )


def test_input_can_be_output(tmp_path: Path):
    """Load frame inputs before replacing an existing destination.

    Arguments:
        tmp_path: temporary directory fixture
    """
    paths = write_apng_frames(tmp_path / "frames")
    ApngasmRunner().run(paths, paths[0])
    with Image.open(paths[0]) as result:
        assert result.n_frames == 3


def test_invalid_files_and_outputs(tmp_path: Path):
    """Report unreadable files and invalid destinations without publishing output.

    Arguments:
        tmp_path: temporary directory fixture
    """
    runner = ApngasmRunner()
    frame = Image.new("RGB", (8, 6))
    output_path = tmp_path / "output.png"
    with pytest.raises(FileNotFoundError):
        runner.run([tmp_path / "missing.png"], output_path)
    corrupt_path = tmp_path / "corrupt.png"
    corrupt_path.write_bytes(b"not a PNG")
    with pytest.raises(OSError):
        runner.run([corrupt_path], output_path)
    with pytest.raises(ValueError, match="suffix"):
        runner.run([frame], tmp_path / "output.jpg")
    directory_path = tmp_path / "directory.png"
    directory_path.mkdir()
    with pytest.raises(IsADirectoryError):
        runner.run([frame], directory_path)
    with pytest.raises(FileNotFoundError):
        runner.run([frame], tmp_path / "missing" / "output.png")
    assert not output_path.exists()


def test_rgb_arrays(tmp_path: Path):
    """Keep RGB channel order for noncontiguous arrays with no alpha channel.

    Arguments:
        tmp_path: temporary directory fixture
    """
    frame = np.arange(6 * 8 * 3, dtype=np.uint8).reshape(6, 8, 3).transpose(1, 0, 2)
    output_path = tmp_path / "rgb.png"
    ApngasmRunner().run([frame], output_path)
    with Image.open(output_path) as result:
        np.testing.assert_array_equal(np.array(result.convert("RGB")), frame)


def test_skip_first_requires_animation_frame(tmp_path: Path):
    """Require a playback frame in addition to the static fallback.

    Arguments:
        tmp_path: temporary directory fixture
    """
    with pytest.raises(ValueError, match="after skip_first"):
        ApngasmRunner(skip_first=True).run(
            [Image.new("RGB", (8, 6))], tmp_path / "output.png"
        )


@pytest.mark.parametrize("input_kind", ["file", "pillow", "numpy", "mixed", "strided"])
@pytest.mark.parametrize("loops", [0, 3])
def test_assembly(tmp_path: Path, input_kind: str, loops: int):
    """Decode real output to verify order, alpha, exact pixels, timing, and loops.

    Arguments:
        tmp_path: temporary directory fixture
        input_kind: frame input representation
        loops: requested playback count
    """
    paths = write_apng_frames(tmp_path / "O'Brien {frames}")
    images = []
    for path in paths:
        with Image.open(path) as image:
            images.append(image.copy())
    frames: list[ApngasmFrame]
    if input_kind == "file":
        frames = list(paths)
    elif input_kind == "pillow":
        frames = list(images)
    elif input_kind == "numpy":
        frames = [np.asarray(image) for image in images]
    elif input_kind == "mixed":
        frames = [paths[0], images[1], np.asarray(images[2])]
    else:
        frames = [np.asarray(image)[:, ::-1, :] for image in images]
        images = [image.transpose(Image.Transpose.FLIP_LEFT_RIGHT) for image in images]
    original_pixels = [np.array(image) for image in images]
    output_path = tmp_path / "O'Brien {animation}.apng"
    runner = ApngasmRunner(loops=loops)
    runner(frames, output_path, delays=[(1, 10), (1, 5), (3, 10)])
    with Image.open(output_path) as animation:
        assert animation.is_animated
        assert animation.n_frames == 3
        assert animation.info["loop"] == loops
        for index, expected in enumerate(original_pixels):
            animation.seek(index)
            np.testing.assert_array_equal(np.array(animation.convert("RGBA")), expected)
            assert animation.info["duration"] == pytest.approx(100 * (index + 1))
    for frame, expected in zip(frames, original_pixels, strict=True):
        if isinstance(frame, np.ndarray):
            np.testing.assert_array_equal(frame, expected)
        elif isinstance(frame, Image.Image):
            np.testing.assert_array_equal(np.array(frame), expected)


@pytest.mark.parametrize("skip_first", [False, True])
def test_default_timing_and_reuse(tmp_path: Path, skip_first: bool):
    """Keep fallback frames out of playback and isolate repeated assembly calls.

    Arguments:
        tmp_path: temporary directory fixture
        skip_first: whether the first input is a static fallback
    """
    frames = write_apng_frames(tmp_path / "frames")
    runner = ApngasmRunner(delay_num=7, delay_den=25, loops=2, skip_first=skip_first)
    for run in range(2):
        output_path = tmp_path / f"animation{run}.png"
        runner.run(frames, output_path)
        with Image.open(output_path) as animation:
            assert animation.n_frames == 3
            assert animation.info.get("default_image", False) == skip_first
            assert animation.info["loop"] == 2
            for index in range(3):
                animation.seek(index)
                if index > 0 or not skip_first:
                    assert animation.info["duration"] == pytest.approx(280)
                with Image.open(frames[index]) as expected:
                    np.testing.assert_array_equal(
                        np.array(animation.convert("RGBA")), np.array(expected)
                    )


@pytest.mark.parametrize(
    ("frames", "delays", "error", "message"),
    [
        ([], None, ValueError, "At least one"),
        (
            [Image.new("RGB", (8, 6)), Image.new("RGB", (9, 6))],
            None,
            ValueError,
            "size",
        ),
        ([Image.new("RGB", (0, 6))], None, ValueError, "nonzero"),
        ([np.zeros((6, 8, 3), dtype=np.float32)], None, TypeError, "uint8"),
        ([np.zeros((6, 8), dtype=np.uint8)], None, ValueError, "shape"),
        ([np.zeros((6, 8, 2), dtype=np.uint8)], None, ValueError, "shape"),
        ([np.zeros((0, 8, 4), dtype=np.uint8)], None, ValueError, "nonzero"),
        ([object()], None, TypeError, "Frames must"),
        ([Image.new("RGB", (8, 6))], [], ValueError, "one pair"),
        ([Image.new("RGB", (8, 6))], [(0, 10)], ValueError, "numerator"),
        ([Image.new("RGB", (8, 6))], [(1, 0)], ValueError, "denominator"),
        ([Image.new("RGB", (8, 6))], [(65536, 10)], ValueError, "numerator"),
        ([Image.new("RGB", (8, 6))], [(1, 65536)], ValueError, "denominator"),
        ([Image.new("RGB", (8, 6))], [(1.5, 10)], TypeError, "integer"),
    ],
)
def test_invalid_frames_and_delays(
    tmp_path: Path, frames: Any, delays: Any, error: type[Exception], message: str
):
    """Reject invalid frames and delays while preserving an existing destination.

    Arguments:
        tmp_path: temporary directory fixture
        frames: intentionally invalid frame inputs
        delays: intentionally invalid per-frame delays
        error: expected exception category
        message: expected diagnostic fragment
    """
    output_path = tmp_path / "existing.png"
    output_path.write_bytes(b"existing output")
    with pytest.raises(error, match=message):
        ApngasmRunner().run(frames, output_path, delays=delays)
    assert output_path.read_bytes() == b"existing output"
    assert list(tmp_path.iterdir()) == [output_path]


@pytest.mark.parametrize(
    ("setting", "value", "error"),
    [
        ("delay_num", 0, ValueError),
        ("delay_num", 65536, ValueError),
        ("delay_den", 0, ValueError),
        ("delay_den", 65536, ValueError),
        ("delay_num", 1.5, TypeError),
        ("delay_den", True, TypeError),
        ("loops", -1, ValueError),
        ("loops", 2**32, ValueError),
        ("loops", 1.5, TypeError),
        ("skip_first", 1, TypeError),
    ],
)
def test_invalid_settings(setting: str, value: Any, error: type[Exception]):
    """Reject settings before integer truncation or unsigned overflow in native code.

    Arguments:
        setting: constructor keyword to test
        value: intentionally invalid value
        error: expected exception category
    """
    with pytest.raises(error, match=setting):
        ApngasmRunner(**{setting: value})


@pytest.mark.parametrize("failure", ["false", "exception", "missing", "corrupt"])
def test_native_failure_preserves_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
):
    """Surface native failures, release frames, and remove incomplete output.

    Arguments:
        tmp_path: temporary directory fixture
        monkeypatch: pytest monkeypatch fixture
        failure: native failure mode to simulate
    """
    cause = RuntimeError("native failure")
    assemble = Mock(return_value=False)
    if failure == "exception":
        assemble.side_effect = cause
    elif failure == "missing":
        assemble.return_value = True
    elif failure == "corrupt":
        assemble.side_effect = lambda path: Path(path).write_bytes(b"incomplete PNG")
    monkeypatch.setattr(APNGAsmBinder, "assemble", assemble)
    output_path = tmp_path / "existing.png"
    output_path.write_bytes(b"existing output")
    with pytest.raises(PipeScalerError) as caught:
        ApngasmRunner().run([Image.new("RGB", (8, 6))], output_path)
    if failure == "exception":
        assert caught.value.__cause__ is cause
    assert output_path.read_bytes() == b"existing output"
    assert list(tmp_path.iterdir()) == [output_path]


@pytest.mark.parametrize("skip_first", [False, True])
def test_repr_round_trip(skip_first: bool):
    """Recreate every assembly setting from repr.

    Arguments:
        skip_first: whether to configure a static fallback
    """
    runner = ApngasmRunner(delay_num=7, delay_den=25, loops=3, skip_first=skip_first)
    recreated = eval(repr(runner))
    assert vars(recreated) == vars(runner)


@pytest.mark.parametrize("mode", ["1", "L", "LA", "P", "RGB", "RGBA"])
def test_single_frame_modes(tmp_path: Path, mode: str):
    """Accept common Pillow modes and produce a valid static PNG for one input.

    Arguments:
        tmp_path: temporary directory fixture
        mode: input image mode
    """
    frame = Image.new("RGBA", (8, 6), (20, 40, 60, 128)).convert(mode)
    if mode == "P":
        frame.info["transparency"] = 0
    output_path = tmp_path / "static.png"
    ApngasmRunner().run([frame], output_path)
    with Image.open(output_path) as result:
        assert result.n_frames == 1
        actual = np.array(result.convert("RGBA"))
        expected = np.array(frame.convert("RGBA"))
        np.testing.assert_array_equal(actual[:, :, 3], expected[:, :, 3])
        visible = expected[:, :, 3] != 0
        np.testing.assert_array_equal(actual[visible], expected[visible])
