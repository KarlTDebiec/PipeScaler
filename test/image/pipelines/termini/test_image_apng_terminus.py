#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Real APNG encoding and transactional image-terminus lifecycle tests."""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from types import TracebackType
from typing import Any
from unittest.mock import Mock

import numpy as np
import pytest
from apngasm_python.apngasm import APNGAsmBinder
from PIL import Image

from pipescaler.common.file import get_temp_file_path
from pipescaler.core.exceptions import PipeScalerError
from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.pipelines.termini import ImageApngTerminus, image_apng_terminus


def test_body_failure_preserves_destination(tmp_path: Path):
    """Discard collected frames when processing fails outside the terminus.

    Arguments:
        tmp_path: temporary output directory
    Raises:
        RuntimeError: deliberately raised and caught to simulate pipeline failure
    """
    output_path = tmp_path / "existing.png"
    output_path.write_bytes(b"existing output")
    with pytest.raises(RuntimeError, match="pipeline failed"):
        with ImageApngTerminus(output_path) as terminus:
            terminus(PipeImage(image=Image.new("RGB", (8, 6)), name="frame"))
            raise RuntimeError("pipeline failed")
    assert output_path.read_bytes() == b"existing output"
    assert list(tmp_path.iterdir()) == [output_path]


def test_caught_frame_failure_cannot_publish(tmp_path: Path):
    """Invalidate the collection even when the caller catches a frame error.

    Arguments:
        tmp_path: temporary output directory
    """
    output_path = tmp_path / "existing.png"
    output_path.write_bytes(b"existing output")
    frame = PipeImage(image=Image.new("RGB", (8, 6)), name="frame")
    mismatch = PipeImage(image=Image.new("RGB", (9, 6)), name="mismatch")
    with pytest.raises(ValueError, match="Cannot publish APNG"):
        with ImageApngTerminus(output_path) as terminus:
            terminus(frame)
            with pytest.raises(ValueError, match="same size"):
                terminus(mismatch)
            with pytest.raises(ValueError, match="failed APNG terminus"):
                terminus(frame)
    assert output_path.read_bytes() == b"existing output"
    assert list(tmp_path.iterdir()) == [output_path]


def test_cleanup_failure_preserves_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Complete native cleanup before publishing the encoded animation.

    Arguments:
        tmp_path: temporary output directory
        monkeypatch: native context cleanup override
    """
    original_exit = APNGAsmBinder.__exit__

    def fail_cleanup(
        assembler: APNGAsmBinder,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ):
        """Release frames and simulate a cleanup failure.

        Arguments:
            assembler: native frame collection
            exc_type: active exception type
            exc_value: active exception
            traceback: active traceback
        Raises:
            RuntimeError: always, to simulate native cleanup failure
        """
        original_exit(assembler, exc_type, exc_value, traceback)
        raise RuntimeError("cleanup failed")

    monkeypatch.setattr(APNGAsmBinder, "__exit__", fail_cleanup)
    output_path = tmp_path / "existing.png"
    output_path.write_bytes(b"existing output")
    with pytest.raises(RuntimeError, match="cleanup failed"):
        with ImageApngTerminus(output_path) as terminus:
            terminus(PipeImage(image=Image.new("RGB", (8, 6)), name="frame"))
    assert output_path.read_bytes() == b"existing output"
    assert list(tmp_path.iterdir()) == [output_path]


def test_context_lifecycle_and_default_delay(tmp_path: Path):
    """Require a single active context and preserve configured default timing.

    Arguments:
        tmp_path: temporary output directory
    """
    output_path = tmp_path / "nested" / "animation.png"
    terminus = ImageApngTerminus(output_path, delay=(7, 25), loops=2)
    frame = PipeImage(image=Image.new("RGB", (8, 6), "red"), name="frame")
    with pytest.raises(ValueError, match="active context"):
        terminus(frame)
    with terminus:
        assert output_path.parent.is_dir()
        assert not output_path.exists()
        with pytest.raises(ValueError, match="Cannot reenter"):
            with terminus:
                pass
        terminus(frame)
        terminus(PipeImage(image=Image.new("RGB", (8, 6), "blue"), name="frame"))
        assert not output_path.exists()
    with Image.open(output_path) as animation:
        assert animation.n_frames == 2
        assert animation.info["loop"] == 2
        for index in range(2):
            animation.seek(index)
            assert animation.info["duration"] == pytest.approx(280)
    with pytest.raises(ValueError, match="active context"):
        terminus(frame)
    with pytest.raises(ValueError, match="Cannot reenter"):
        with terminus:
            pass


def test_fallback_requires_playback_frame(tmp_path: Path):
    """Require a playback frame in addition to the static fallback image.

    Arguments:
        tmp_path: temporary output directory
    """
    output_path = tmp_path / "existing.png"
    output_path.write_bytes(b"existing output")
    with pytest.raises(ValueError, match="At least one animation frame"):
        with ImageApngTerminus(output_path, skip_first=True) as terminus:
            terminus(PipeImage(image=Image.new("RGB", (8, 6)), name="fallback"))
    assert output_path.read_bytes() == b"existing output"


def test_invalid_files_and_outputs(tmp_path: Path):
    """Report unreadable sources and invalid destinations without publishing.

    Arguments:
        tmp_path: temporary input and output directory
    """
    output_path = tmp_path / "output.png"
    with pytest.raises(FileNotFoundError):
        with ImageApngTerminus(output_path) as terminus:
            terminus(PipeImage(path=tmp_path / "missing.png"))
    corrupt_path = tmp_path / "corrupt.png"
    corrupt_path.write_bytes(b"not a PNG")
    with pytest.raises(OSError):
        with ImageApngTerminus(output_path) as terminus:
            terminus(PipeImage(path=corrupt_path))
    with pytest.raises(ValueError, match="suffix"):
        ImageApngTerminus(tmp_path / "output.jpg")
    directory_path = tmp_path / "directory.png"
    directory_path.mkdir()
    with pytest.raises(OSError):
        ImageApngTerminus(directory_path)
    assert not output_path.exists()


def test_replace_failure_preserves_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Discard temporary encoding when atomic replacement fails.

    Arguments:
        tmp_path: temporary output directory
        monkeypatch: path replacement override
    """

    def fail_replace(path: Path, target: Path):
        """Simulate a failed destination replacement.

        Arguments:
            path: completed temporary PNG
            target: destination PNG
        Raises:
            OSError: always, to simulate publication failure
        """
        raise OSError("replacement failed")

    monkeypatch.setattr(Path, "replace", fail_replace)
    output_path = tmp_path / "existing.png"
    output_path.write_bytes(b"existing output")
    with pytest.raises(OSError, match="replacement failed"):
        with ImageApngTerminus(output_path) as terminus:
            terminus(PipeImage(image=Image.new("RGB", (8, 6)), name="frame"))
    assert output_path.read_bytes() == b"existing output"
    assert list(tmp_path.iterdir()) == [output_path]


def test_snapshot_and_input_as_output(frame_paths: list[Path]):
    """Snapshot admissions before later mutation or replacement of a source file.

    Arguments:
        frame_paths: generated static frame paths
    """
    output_path = frame_paths[0]
    frame = PipeImage(path=output_path)
    expected = np.array(frame.image.convert("RGBA"))
    original_bytes = output_path.read_bytes()
    with ImageApngTerminus(output_path) as terminus:
        terminus(frame)
        frame.image.paste("black", (0, 0, 8, 6))
        terminus(PipeImage(path=frame_paths[1]))
        assert output_path.read_bytes() == original_bytes
    with Image.open(output_path) as animation:
        assert animation.n_frames == 2
        np.testing.assert_array_equal(np.array(animation.convert("RGBA")), expected)


def test_unicode_temp_with_unwritable_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Explain when Windows cannot stage encoding outside a Unicode TEMP.

    Arguments:
        tmp_path: temporary output directory
        monkeypatch: temporary file creation override
    """
    cwd_path = tmp_path / "作業"
    cwd_path.mkdir()
    monkeypatch.chdir(cwd_path)
    monkeypatch.setattr(image_apng_terminus, "os_name", "nt")
    monkeypatch.setattr(image_apng_terminus, "gettempdir", lambda: str(cwd_path))

    @contextmanager
    def temporary_path(
        suffix: str | None = None, *, parent_dir_path: Path | None = None
    ) -> Generator[Path]:
        """Allow adjacent output staging while simulating an unwritable native cwd.

        Arguments:
            suffix: requested temporary suffix
            parent_dir_path: directory requested for staging
        Yields:
            writable adjacent output path
        Raises:
            PermissionError: if native encoding requests the unwritable cwd
        """
        if parent_dir_path == cwd_path:
            raise PermissionError("Current working directory is read-only")
        with get_temp_file_path(suffix, parent_dir_path=parent_dir_path) as path:
            yield path

    monkeypatch.setattr(image_apng_terminus, "get_temp_file_path", temporary_path)
    output_path = tmp_path / "existing.png"
    output_path.write_bytes(b"existing output")
    with pytest.raises(PipeScalerError, match="writable current working directory"):
        with ImageApngTerminus(output_path) as terminus:
            terminus(PipeImage(image=Image.new("RGB", (8, 6)), name="frame"))
    assert output_path.read_bytes() == b"existing output"


def test_zero_size_frame_rejected(tmp_path: Path):
    """Reject zero-sized images before passing their memory into native code.

    Arguments:
        tmp_path: temporary output directory
    """
    output_path = tmp_path / "existing.png"
    output_path.write_bytes(b"existing output")
    with pytest.raises(ValueError, match="nonzero"):
        with ImageApngTerminus(output_path) as terminus:
            terminus(PipeImage(image=Image.new("RGB", (0, 6)), name="frame"))
    assert output_path.read_bytes() == b"existing output"


@pytest.fixture
def frame_paths(tmp_path: Path) -> list[Path]:
    """Generate ordered frames with changing colors, positions, and transparency.

    Arguments:
        tmp_path: temporary directory fixture
    Returns:
        generated static frame paths in playback order
    """
    dir_path = tmp_path / "入力 O'Brien {frames}"
    dir_path.mkdir()
    paths = []
    for index, (name, color) in enumerate(
        zip(
            ("z first", "a second", "m third"),
            ((255, 0, 0, 255), (0, 255, 0, 128), (0, 0, 255, 255)),
            strict=True,
        )
    ):
        image = Image.new("RGBA", (8, 6), (0, 0, 0, 0))
        image.paste(color, (index + 1, 1, index + 5, 4))
        image.putpixel((6, 4), (255, 255, 255, 255))
        path = dir_path / f"{name}.png"
        image.save(path)
        paths.append(path)
    return paths


@pytest.mark.parametrize("file_backed", [False, True])
def test_animated_inputs_rejected(frame_paths: list[Path], file_backed: bool):
    """Reject animated files before PipeImage can strip palette animation metadata.

    Arguments:
        frame_paths: generated static frame paths
        file_backed: whether to pass a path or an in-memory animated Pillow image
    """
    animated_path = frame_paths[0].parent / "animated.png"
    with ImageApngTerminus(animated_path) as terminus:
        for path in frame_paths:
            terminus(PipeImage(path=path))
    output_path = animated_path.with_name("rejected.png")
    with Image.open(animated_path) as animation:
        with pytest.raises(ValueError, match="static"):
            with ImageApngTerminus(output_path) as terminus:
                if file_backed:
                    terminus(PipeImage(path=animated_path))
                else:
                    terminus(PipeImage(image=animation, name="animated"))
    assert not output_path.exists()


@pytest.mark.parametrize("input_kind", ["file", "memory", "mixed"])
@pytest.mark.parametrize("loops", [0, 3])
@pytest.mark.parametrize("skip_first", [False, True])
def test_collection_content_and_timing(
    frame_paths: list[Path],
    tmp_path: Path,
    input_kind: str,
    loops: int,
    skip_first: bool,
):
    """Decode published output to verify frame order, alpha, timing, and looping.

    Arguments:
        frame_paths: generated static frame paths in playback order
        tmp_path: temporary output directory
        input_kind: representation used to create the PipeImage objects
        loops: requested playback count
        skip_first: whether to keep a separate static fallback frame
    """
    images = []
    for path in frame_paths:
        with Image.open(path) as image:
            images.append(image.copy())
    output_path = tmp_path / "O'Brien {animation}.apng"
    with ImageApngTerminus(output_path, loops=loops, skip_first=skip_first) as terminus:
        for index, (path, image) in enumerate(zip(frame_paths, images, strict=True)):
            if input_kind == "file" or (input_kind == "mixed" and index == 0):
                frame = PipeImage(path=path)
            else:
                frame = PipeImage(image=image, name=path.stem)
            terminus(frame, delay=(index + 1, 10))
    with Image.open(output_path) as animation:
        assert animation.n_frames == 3
        assert animation.info["loop"] == loops
        assert animation.info.get("default_image", False) == skip_first
        for index, expected in enumerate(images):
            animation.seek(index)
            np.testing.assert_array_equal(
                np.array(animation.convert("RGBA")), np.array(expected)
            )
            if index > 0 or not skip_first:
                assert animation.info["duration"] == pytest.approx(100 * (index + 1))
    for path, image in zip(frame_paths, images, strict=True):
        with Image.open(path) as original:
            np.testing.assert_array_equal(np.array(image), np.array(original))


@pytest.mark.parametrize(
    ("duplicate_delays", "duration_ms"),
    [
        (((1, 10), (1, 5)), 300),
        (((65535, 65534), (65535, 65534)), 2000 * 65535 / 65534),
        (((40000, 65535), (40000, 65535)), 2000 * 40000 / 65535),
        (((1, 256), (1, 257), (255, 256)), 1000 * 258 / 257),
    ],
)
def test_duplicate_frames_preserve_total_duration(
    frame_paths: list[Path],
    tmp_path: Path,
    duplicate_delays: tuple[tuple[int, int], ...],
    duration_ms: float,
):
    """Combine duplicate runs exactly, including unrepresentable intermediate sums.

    Arguments:
        frame_paths: generated static frame paths
        tmp_path: temporary output directory
        duplicate_delays: delays for a run of identical input frames
        duration_ms: exact expected duration of the combined output frame
    """
    output_path = tmp_path / "duplicates.png"
    with ImageApngTerminus(output_path) as terminus:
        for delay in duplicate_delays:
            terminus(PipeImage(path=frame_paths[0]), delay=delay)
        terminus(PipeImage(path=frame_paths[1]), delay=(3, 10))
    with Image.open(output_path) as animation:
        assert animation.n_frames == 2
        for index in range(2):
            animation.seek(index)
            assert animation.info["duration"] == pytest.approx(
                duration_ms if index == 0 else 300
            )
            with Image.open(frame_paths[index]) as expected:
                np.testing.assert_array_equal(
                    np.array(animation.convert("RGBA")), np.array(expected)
                )


@pytest.mark.parametrize("skip_first", [False, True])
def test_duplicate_normalization(tmp_path: Path, skip_first: bool):
    """Normalize modes and invisible colors without merging the fallback into playback.

    Arguments:
        tmp_path: temporary output directory
        skip_first: whether the first input is a separate static fallback
    """
    rgb = np.full((6, 8, 3), 50, dtype=np.uint8)
    rgba = np.concatenate((rgb, np.full((6, 8, 1), 255, dtype=np.uint8)), axis=2)
    transparent = rgba.copy()
    transparent[0, 0] = (0, 0, 0, 0)
    hidden_color = transparent.copy()
    hidden_color[0, 0] = (20, 40, 60, 0)
    frames = [
        Image.fromarray(array) for array in (rgb, rgba, transparent, hidden_color)
    ]
    output_path = tmp_path / "duplicates.png"
    with ImageApngTerminus(output_path, skip_first=skip_first) as terminus:
        for frame in frames:
            terminus(PipeImage(image=frame, name="frame"))
    np.testing.assert_array_equal(np.array(frames[-1]), hidden_color)
    with Image.open(output_path) as animation:
        assert animation.n_frames == 2 + int(skip_first)
        assert animation.info.get("default_image", False) == skip_first
        animation.seek(int(skip_first))
        assert animation.info["duration"] == pytest.approx(100 if skip_first else 200)
        animation.seek(1 + int(skip_first))
        assert animation.info["duration"] == pytest.approx(200)


@pytest.mark.parametrize("skip_first", [False, True])
def test_empty_collection_preserves_destination(tmp_path: Path, skip_first: bool):
    """Reject empty animations while retaining an existing output.

    Arguments:
        tmp_path: temporary output directory
        skip_first: whether a static fallback is configured
    """
    output_path = tmp_path / "existing.png"
    output_path.write_bytes(b"existing output")
    with pytest.raises(ValueError, match="At least one animation frame"):
        with ImageApngTerminus(output_path, skip_first=skip_first):
            pass
    assert output_path.read_bytes() == b"existing output"
    assert list(tmp_path.iterdir()) == [output_path]


@pytest.mark.parametrize("delay", [(0, 10), (1, 0), (1.5, 10)])
def test_invalid_frame_delay_preserves_destination(tmp_path: Path, delay: Any):
    """Reject invalid per-frame overrides and invalidate the collection.

    Arguments:
        tmp_path: temporary output directory
        delay: intentionally invalid numerator/denominator pair
    """
    output_path = tmp_path / "existing.png"
    output_path.write_bytes(b"existing output")
    with pytest.raises((TypeError, ValueError), match="delay"):
        with ImageApngTerminus(output_path) as terminus:
            terminus(
                PipeImage(image=Image.new("RGB", (8, 6)), name="frame"), delay=delay
            )
    assert output_path.read_bytes() == b"existing output"


@pytest.mark.parametrize(
    ("setting", "value", "error"),
    [
        ("delay", (0, 10), ValueError),
        ("delay", (1, 0), ValueError),
        ("delay", (65536, 10), ValueError),
        ("delay", (1, 65536), ValueError),
        ("delay", (1.5, 10), TypeError),
        ("delay", (1, True), TypeError),
        ("loops", -1, ValueError),
        ("loops", 2**32, ValueError),
        ("loops", 1.5, TypeError),
        ("skip_first", 1, TypeError),
    ],
)
def test_invalid_settings(
    tmp_path: Path, setting: str, value: Any, error: type[Exception]
):
    """Validate settings without native integer truncation or unsigned overflow.

    Arguments:
        tmp_path: temporary output directory
        setting: constructor keyword to test
        value: intentionally invalid value
        error: expected exception category
    """
    with pytest.raises(error, match=setting):
        ImageApngTerminus(tmp_path / "output.png", **{setting: value})


@pytest.mark.parametrize("failure", ["false", "exception", "missing", "corrupt"])
def test_native_failure_preserves_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
):
    """Surface native failures and discard incomplete output.

    Arguments:
        tmp_path: temporary output directory
        monkeypatch: native assembly override
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
        with ImageApngTerminus(output_path) as terminus:
            terminus(PipeImage(image=Image.new("RGB", (8, 6)), name="frame"))
    if failure == "exception":
        assert caught.value.__cause__ is cause
    assert output_path.read_bytes() == b"existing output"
    assert list(tmp_path.iterdir()) == [output_path]


@pytest.mark.parametrize("fortran_order", [False, True])
def test_numpy_backed_images(tmp_path: Path, fortran_order: bool):
    """Admit in-memory images made from strided and Fortran RGB arrays.

    Arguments:
        tmp_path: temporary output directory
        fortran_order: whether to use Fortran-contiguous rather than transposed storage
    """
    pixels = np.arange(6 * 8 * 3, dtype=np.uint8).reshape(6, 8, 3).transpose(1, 0, 2)
    if fortran_order:
        pixels = np.asfortranarray(pixels)
    output_path = tmp_path / "rgb.png"
    with ImageApngTerminus(output_path) as terminus:
        terminus(PipeImage(image=Image.fromarray(pixels), name="frame"))
    with Image.open(output_path) as result:
        np.testing.assert_array_equal(np.array(result.convert("RGB")), pixels)


@pytest.mark.parametrize("mode", ["1", "L", "LA", "P", "RGB", "RGBA"])
def test_single_frame_modes(tmp_path: Path, mode: str):
    """Encode common Pillow modes as a static PNG when there is one distinct frame.

    Arguments:
        tmp_path: temporary output directory
        mode: input image mode
    """
    frame = Image.new("RGBA", (8, 6), (20, 40, 60, 128)).convert(mode)
    if mode == "P":
        frame.info["transparency"] = 0
    output_path = tmp_path / "static.png"
    with ImageApngTerminus(output_path) as terminus:
        terminus(PipeImage(image=frame, name="frame"))
    with Image.open(output_path) as result:
        assert result.n_frames == 1
        actual = np.array(result.convert("RGBA"))
        expected = np.array(frame.convert("RGBA"))
        np.testing.assert_array_equal(actual[:, :, 3], expected[:, :, 3])
        visible = expected[:, :, 3] != 0
        np.testing.assert_array_equal(actual[visible], expected[visible])


@pytest.mark.parametrize("unicode_temp", [False, True])
def test_unicode_paths(
    frame_paths: list[Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    unicode_temp: bool,
):
    """Publish through Unicode input, output, and system temporary paths.

    Arguments:
        frame_paths: generated static frame paths
        tmp_path: temporary output directory
        monkeypatch: system temporary directory override
        unicode_temp: whether to use a Unicode system temporary directory
    """
    output_dir_path = tmp_path / "出力"
    output_dir_path.mkdir()
    if unicode_temp:
        native_temp_dir_path = tmp_path / "一時"
        native_temp_dir_path.mkdir()
        monkeypatch.setattr(tempfile, "tempdir", str(native_temp_dir_path))
        monkeypatch.chdir(output_dir_path)
    cwd_path = Path.cwd()
    output_path = output_dir_path / "動画.png"
    with ImageApngTerminus(output_path) as terminus:
        for path in frame_paths:
            terminus(PipeImage(path=path))
    assert Path.cwd() == cwd_path
    assert list(output_dir_path.iterdir()) == [output_path]
    with Image.open(output_path) as animation:
        assert animation.n_frames == 3


@pytest.mark.parametrize(
    "duplicate_delays", [((1, 1000), (1, 1001)), ((40000, 1), (40000, 1))]
)
def test_unrepresentable_duplicate_delay_rejected(
    frame_paths: list[Path],
    tmp_path: Path,
    duplicate_delays: tuple[tuple[int, int], ...],
):
    """Reject duplicate runs whose final exact timing cannot fit APNG fields.

    Arguments:
        frame_paths: generated static frame paths
        tmp_path: temporary output directory
        duplicate_delays: individually valid delays with an unrepresentable sum
    """
    output_path = tmp_path / "existing.png"
    output_path.write_bytes(b"existing output")
    with pytest.raises(ValueError, match="Combined duplicate-frame delay"):
        with ImageApngTerminus(output_path) as terminus:
            for delay in duplicate_delays:
                terminus(PipeImage(path=frame_paths[0]), delay=delay)
            terminus(PipeImage(path=frame_paths[1]))
    assert output_path.read_bytes() == b"existing output"
