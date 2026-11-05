#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""APNG decoding, resource ownership, and image-pipeline round trips."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image
from PIL.JpegImagePlugin import JpegImageFile
from PIL.PngImagePlugin import PngImageFile

from pipescaler.image.operators.processors import ResizeProcessor
from pipescaler.image.pipelines.segments import ImageProcessorSegment
from pipescaler.image.pipelines.sources import ImageApngSource
from pipescaler.image.pipelines.termini import ImageApngTerminus


def test_frames(animation_path: Path, frames: list[Image.Image]):
    """Preserve playback order, alpha, names, locations, and detached pixels.

    Arguments:
        animation_path: generated APNG input
        frames: original full-canvas frames
    """
    source = ImageApngSource(animation_path, Path("animations"))
    assert source.length == 3
    assert source.index == 0
    outputs = list(source)
    assert source.index == 3
    assert [output.name for output in outputs] == ["000001", "000002", "000003"]
    assert all(
        output.location == Path("animations/animation_png") for output in outputs
    )
    for output, expected in zip(outputs, frames, strict=True):
        assert output.image.mode == "RGBA"
        assert output.image.size == expected.size
        assert output.image.tobytes() == expected.tobytes()
    outputs[0].image.putpixel((1, 1), (1, 2, 3, 4))
    assert outputs[1].image.tobytes() == frames[1].tobytes()
    with pytest.raises(StopIteration):
        next(source)


def test_invalid_input(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Reject other formats and release their opened decoders.

    Arguments:
        tmp_path: temporary input directory
        monkeypatch: decoder factory override
    """
    input_path = tmp_path / "image.jpg"
    Image.new("RGB", (4, 4)).save(input_path)
    decoder = Image.open(input_path)
    assert isinstance(decoder, JpegImageFile)
    file = decoder.fp
    assert file is not None
    monkeypatch.setattr(Image, "open", lambda path: decoder)
    with pytest.raises(ValueError, match="not a PNG"):
        ImageApngSource(input_path)
    assert file.closed


def test_invalid_path_and_options(animation_path: Path, tmp_path: Path):
    """Use normal path validation and reject non-boolean fallback options.

    Arguments:
        animation_path: generated APNG input
        tmp_path: temporary input directory
    """
    with pytest.raises(FileNotFoundError):
        ImageApngSource(tmp_path / "missing.png")
    with pytest.raises(TypeError, match="include_default must be a bool"):
        ImageApngSource(animation_path, include_default=1)  # ty: ignore[invalid-argument-type]
    broken_path = tmp_path / "broken.png"
    broken_path.write_bytes(b"not a PNG")
    with pytest.raises(OSError):
        ImageApngSource(broken_path)


def test_repr(animation_path: Path):
    """Recreate source configuration, including optional default-image handling.

    Arguments:
        animation_path: generated APNG input
    """
    with ImageApngSource(
        animation_path, Path("animations"), include_default=True
    ) as source:
        with eval(repr(source)) as recreated:
            assert recreated.input_path == source.input_path
            assert recreated.location_path == source.location_path
            assert recreated.include_default is True


def test_unicode_path(animation_path: Path):
    """Decode PNG paths containing non-ASCII characters.

    Arguments:
        animation_path: generated APNG input
    """
    unicode_path = animation_path.with_name("動画.png")
    animation_path.rename(unicode_path)
    assert len(list(ImageApngSource(unicode_path))) == 3


@pytest.fixture
def animation_path(tmp_path: Path, frames: list[Image.Image]) -> Path:
    """Provide an APNG with distinct frames, variable delays, and finite looping.

    Arguments:
        tmp_path: temporary input directory
        frames: full-canvas RGBA frames to encode
    """
    input_path = tmp_path / "animation.png"
    frames[0].save(
        input_path,
        save_all=True,
        append_images=frames[1:],
        duration=[40, 80, 120],
        loop=3,
    )
    return input_path


@pytest.fixture
def frames() -> list[Image.Image]:
    """Provide distinct full-canvas RGBA frames with a transparent pixel."""
    images = [Image.new("RGBA", (4, 4), color) for color in ("red", "green", "blue")]
    for image in images:
        image.putpixel((0, 0), (0, 0, 0, 0))
    return images


@pytest.mark.parametrize("disposal", [1, 2])
@pytest.mark.parametrize(
    ("alpha", "blended"),
    [(0, (0, 255, 0, 128)), (128, (85, 170, 0, 192)), (255, (127, 128, 0, 255))],
)
def test_blending_and_disposal(
    tmp_path: Path, disposal: int, alpha: int, blended: tuple[int, int, int, int]
):
    """Yield displayed canvases after OVER blending and BACKGROUND or PREVIOUS.

    Arguments:
        tmp_path: temporary input directory
        disposal: APNG disposal operation for the middle frame
        alpha: base canvas alpha
        blended: expected green-over-red pixel in the displayed middle frame
    """
    first = Image.new("RGBA", (4, 4), (255, 0, 0, alpha))
    second = first.copy()
    second.putpixel((1, 1), (0, 255, 0, 128))
    third = first.copy()
    if disposal == 1:
        third.putpixel((1, 1), (0, 0, 0, 0))
    third.putpixel((2, 2), (0, 0, 255, 255))
    input_path = tmp_path / "blend.png"
    first.save(
        input_path,
        save_all=True,
        append_images=[second, third],
        duration=100,
        disposal=[0, disposal, 0],
        blend=[0, 1, 1],
    )
    outputs = list(ImageApngSource(input_path))
    expected_second = first.copy()
    expected_second.putpixel((1, 1), blended)
    assert outputs[0].image.tobytes() == first.tobytes()
    assert outputs[1].image.tobytes() == expected_second.tobytes()
    assert outputs[2].image.tobytes() == third.tobytes()


@pytest.mark.parametrize("error", [EOFError, OSError, SyntaxError])
def test_decode_failure(
    animation_path: Path,
    frames: list[Image.Image],
    monkeypatch: pytest.MonkeyPatch,
    error: type[Exception],
):
    """Report failed playback decoding and close without invalidating yielded images.

    Arguments:
        animation_path: generated APNG input
        frames: original frames
        monkeypatch: decoder method override
        error: decoder error to simulate
    """
    decoder = Image.open(animation_path)
    assert isinstance(decoder, PngImageFile)
    file = decoder.fp
    assert file is not None
    monkeypatch.setattr(Image, "open", lambda path: decoder)
    source = ImageApngSource(animation_path)
    output = next(source)

    def fail_seek(frame: int):
        """Simulate failure to decode a later frame.

        Arguments:
            frame: requested frame number
        Raises:
            Exception: selected decoder failure
        """
        raise error("broken frame")

    monkeypatch.setattr(decoder, "seek", fail_seek)
    with pytest.raises(OSError, match="frame 2 of 3") as caught:
        next(source)
    assert isinstance(caught.value.__cause__, error)
    assert file.closed
    assert output.image.tobytes() == frames[0].tobytes()
    with pytest.raises(StopIteration):
        next(source)


@pytest.mark.parametrize("finish", ["exhaust", "close", "context", "exception"])
def test_decoder_cleanup(
    animation_path: Path,
    frames: list[Image.Image],
    monkeypatch: pytest.MonkeyPatch,
    finish: str,
):
    """Close resources after exhaustion, early close, and normal or failed context exit.

    Arguments:
        animation_path: generated APNG input
        frames: original frames
        monkeypatch: decoder factory override
        finish: way in which source consumption ends
    Raises:
        RuntimeError: deliberately raised and caught to simulate pipeline failure
    """
    decoder = Image.open(animation_path)
    assert isinstance(decoder, PngImageFile)
    file = decoder.fp
    assert file is not None
    monkeypatch.setattr(Image, "open", lambda path: decoder)
    source = ImageApngSource(animation_path)
    output = next(source)
    if finish == "exhaust":
        for _ in range(source.length - 1):
            next(source)
    elif finish == "close":
        source.close()
    elif finish == "context":
        with source:
            pass
    else:
        with pytest.raises(RuntimeError, match="pipeline failed"):
            with source:
                raise RuntimeError("pipeline failed")
    assert file.closed
    assert output.image.tobytes() == frames[0].tobytes()
    source.close()
    with pytest.raises(StopIteration):
        next(source)
    with pytest.raises(ValueError, match="closed APNG source"):
        with source:
            pass


@pytest.mark.parametrize("include_default", [False, True])
def test_default_image(
    tmp_path: Path, frames: list[Image.Image], include_default: bool
):
    """Exclude a poster from playback unless the caller explicitly includes it.

    Arguments:
        tmp_path: temporary input directory
        frames: playback frames
        include_default: whether the source should include the separate poster
    """
    poster = Image.new("RGBA", (4, 4), "purple")
    input_path = tmp_path / "poster.png"
    poster.save(
        input_path,
        save_all=True,
        append_images=frames,
        default_image=True,
        duration=[40, 80, 120],
        blend=[1, 0, 0],
    )
    with ImageApngSource(input_path, include_default=include_default) as source:
        expected = frames
        if include_default:
            expected = [poster, *frames]
        assert source.length == len(expected)
        outputs = list(source)
    for index, (output, frame) in enumerate(
        zip(outputs, expected, strict=True), start=1
    ):
        assert output.name == f"{index:06d}"
        assert output.image.tobytes() == frame.tobytes()
    output_path = tmp_path / "output.png"
    with ImageApngTerminus(output_path, skip_first=include_default) as terminus:
        for output in outputs:
            terminus(output)
    with Image.open(output_path) as animation:
        assert bool(animation.info.get("default_image")) == include_default
    reloaded = list(ImageApngSource(output_path, include_default=include_default))
    assert [frame.image.tobytes() for frame in reloaded] == [
        frame.tobytes() for frame in expected
    ]


@pytest.mark.parametrize("scale", [1, 2])
def test_pipeline_round_trip(
    animation_path: Path, frames: list[Image.Image], tmp_path: Path, scale: int
):
    """Process frames and choose output timing and looping independently of input.

    Arguments:
        animation_path: generated APNG with varying delays and three loops
        frames: original full-canvas frames
        tmp_path: temporary output directory
        scale: whether to pass frames unchanged or resize through an image segment
    """
    output_path = tmp_path / "output.png"
    segment = ImageProcessorSegment(ResizeProcessor(scale, resample="nearest"))
    with (
        ImageApngSource(animation_path) as source,
        ImageApngTerminus(output_path, delay=(1, 5), loops=2) as terminus,
    ):
        for frame in source:
            output = frame
            if scale == 2:
                (output,) = segment(frame)
            terminus(output)
    with Image.open(output_path) as animation:
        assert isinstance(animation, PngImageFile)
        assert animation.n_frames == 3
        assert animation.info["loop"] == 2
        for index, expected in enumerate(frames):
            animation.seek(index)
            assert animation.info["duration"] == 200
            resized = expected.resize((4 * scale, 4 * scale), Image.Resampling.NEAREST)
            assert animation.convert("RGBA").tobytes() == resized.tobytes()


@pytest.mark.parametrize("mode", ["1", "L", "LA", "P", "RGB", "RGBA"])
def test_static_png(tmp_path: Path, mode: str):
    """Accept static PNGs in common modes and round-trip single-frame output.

    Arguments:
        tmp_path: temporary input and output directory
        mode: Pillow image mode of the static input
    """
    input_path = tmp_path / "static.png"
    image = Image.new(mode, (4, 4))
    image.save(input_path)
    source = ImageApngSource(input_path)
    assert source.length == 1
    (output,) = source
    assert output.image.mode == "RGBA"
    assert output.image.tobytes() == image.convert("RGBA").tobytes()
    output_path = tmp_path / "output.png"
    with ImageApngTerminus(output_path) as terminus:
        terminus(output)
    (reloaded,) = ImageApngSource(output_path)
    assert reloaded.image.tobytes() == output.image.tobytes()
