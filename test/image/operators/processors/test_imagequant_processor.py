#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for image and PNG file processing with ImagequantProcessor."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from struct import pack
from typing import Any

import numpy as np
import pytest
from PIL import Image, ImageCms
from PIL.PngImagePlugin import PngInfo

from pipescaler.image.core import UnsupportedImageModeError
from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.core.validation import validate_image
from pipescaler.image.operators.processors import ImagequantProcessor
from pipescaler.image.pipelines import ImageCheckpointManager
from pipescaler.image.pipelines.segments import ImageProcessorSegment
from pipescaler.testing.file import get_test_input_path


@pytest.mark.parametrize(
    "input_name", ["1", "L", "LA", "RGB", "RGBA", "PL", "PLA", "PRGB", "PRGBA"]
)
def test_supported_modes(input_name: str):
    """Quantize supported image modes without modifying input pixels or metadata.

    Arguments:
        input_name: existing input fixture name
    """
    with Image.open(get_test_input_path(input_name)) as image:
        original_pixels = image.tobytes()
        original_info = image.info.copy()

        output = ImagequantProcessor(min_quality=0, skip_if_larger=False)(image)

        assert output.mode == "P"
        assert output.size == image.size
        assert len(output.getcolors() or []) <= 256
        assert image.tobytes() == original_pixels
        assert image.info == original_info


@pytest.mark.parametrize("palette_mode", ["RGB", "RGBA"])
def test_palette_transparency_survives_repeated_quantization(palette_mode: str):
    """Keep visible colors and alpha in existing palettes and subsequent operators.

    Arguments:
        palette_mode: representation of the input palette's transparency
    """
    pixels = [(0, 0, 0, 0), (255, 0, 0, 128), (0, 255, 0, 255)]
    image = Image.frombytes("P", (3, 1), b"\x00\x01\x02")
    if palette_mode == "RGBA":
        image.putpalette([channel for pixel in pixels for channel in pixel], "RGBA")
    else:
        image.putpalette([channel for pixel in pixels for channel in pixel[:3]])
        image.info["transparency"] = bytes(pixel[3] for pixel in pixels)
    processor = ImagequantProcessor(skip_if_larger=False)

    output = processor(processor(image))

    assert output.mode == "P"
    rendered = np.array(validate_image(output).convert("RGBA"))
    assert rendered[0, :, 3].tolist() == [0, 128, 255]
    assert rendered[0, 1:].tolist() == [list(pixel) for pixel in pixels[1:]]


@pytest.mark.parametrize("dithering_level", [0.0, 1.0])
def test_palette_limit(dithering_level: float):
    """Reduce a many-color image to the configured palette size.

    Arguments:
        dithering_level: requested dithering strength
    """
    pixels = np.random.default_rng(168).integers(0, 256, (32, 32, 3), dtype=np.uint8)
    output = ImagequantProcessor(
        max_colors=8,
        min_quality=0,
        dithering_level=dithering_level,
        skip_if_larger=False,
    )(Image.fromarray(pixels))

    assert output.mode == "P"
    assert 1 < len(output.getcolors() or []) <= 8


def test_quality_rejection_returns_original():
    """Return the original image when a tiny palette cannot meet perfect quality."""
    pixels = np.random.default_rng(168).integers(0, 256, (32, 32, 3), dtype=np.uint8)
    image = Image.fromarray(pixels)
    image.info["description"] = "original metadata"

    output = ImagequantProcessor(max_colors=2, min_quality=100)(image)

    assert output is image
    assert np.array_equal(np.array(output), pixels)
    assert output.info["description"] == "original metadata"


@pytest.mark.parametrize(
    "settings",
    [
        {"max_colors": 1},
        {"max_colors": 257},
        {"min_quality": -1},
        {"min_quality": 101},
        {"max_quality": -1},
        {"max_quality": 101},
        {"min_quality": 90, "max_quality": 80},
        {"dithering_level": -0.1},
        {"dithering_level": 1.1},
        {"dithering_level": float("nan")},
        {"dithering_level": float("inf")},
    ],
)
def test_invalid_settings(settings: dict[str, Any]):
    """Reject invalid settings before invoking native code.

    Arguments:
        settings: invalid quantizer settings
    """
    with pytest.raises(ValueError):
        ImagequantProcessor(**settings)


def test_other_native_errors_propagate(monkeypatch: pytest.MonkeyPatch):
    """Keep unexpected native failures distinct from minimum-quality rejection.

    Arguments:
        monkeypatch: pytest patch fixture
    """

    def fail(*args: Any, **kwargs: Any):
        """Simulate a native failure unrelated to quality.

        Arguments:
            *args: unused quantization arguments
            **kwargs: unused quantization settings
        Raises:
            RuntimeError: always
        """
        raise RuntimeError("Out of memory")

    monkeypatch.setattr("imagequant.quantize_raw_rgba_bytes", fail)

    with pytest.raises(RuntimeError, match="Out of memory"):
        ImagequantProcessor()(Image.new("RGB", (2, 2)))


def test_repr_round_trip():
    """Reconstruct non-default quantization settings from their representation."""
    processor = ImagequantProcessor(
        max_colors=16,
        min_quality=20,
        max_quality=80,
        dithering_level=0.5,
        skip_if_larger=False,
    )

    assert repr(eval(repr(processor))) == repr(processor)


def test_unsupported_mode():
    """Reject unsupported modes before converting their pixel representation."""
    with pytest.raises(UnsupportedImageModeError):
        ImagequantProcessor()(Image.new("CMYK", (2, 2)))


def test_color_metadata_is_retained():
    """Retain color interpretation while replacing palette-specific transparency."""
    image = Image.new("RGB", (2, 2), (128, 128, 128))
    color_info = {
        "icc_profile": b"source RGB profile",
        "gamma": 1.0,
        "chromaticity": (0.3127, 0.329, 0.68, 0.32, 0.265, 0.69, 0.15, 0.06),
        "srgb": 0,
    }
    image.info.update(color_info)
    image.info["transparency"] = (128, 128, 128)

    output = ImagequantProcessor(skip_if_larger=False)(image)

    assert output.mode == "P"
    for key, value in color_info.items():
        assert output.info[key] == value
    assert output.convert("RGBA").getpixel((0, 0))[3] == 0


def test_sixteen_bit_grayscale_is_unsupported():
    """Reject 16-bit grayscale images outside the processor's supported modes."""
    pixels = np.array([[0, 32768, 65535]], dtype=np.uint16)
    image = Image.fromarray(pixels)
    image.info["gamma"] = 1.0

    with pytest.raises(UnsupportedImageModeError):
        ImagequantProcessor()(image)

    assert np.array_equal(np.array(image), pixels)
    assert image.info["gamma"] == 1.0


@pytest.mark.parametrize("mode", ["1", "L", "LA"])
def test_profiled_grayscale_is_retained(mode: str):
    """Avoid attaching a grayscale ICC profile to an RGB palette.

    Arguments:
        mode: grayscale input mode
    """
    image = Image.new(mode, (2, 2))
    image.info["icc_profile"] = b"source grayscale profile"

    assert ImagequantProcessor()(image) is image


@pytest.mark.parametrize("size", [(0, 1), (1, 0)])
def test_empty_image(size: tuple[int, int]):
    """Reject empty images before passing their buffers to native code.

    Arguments:
        size: image dimensions with an empty axis
    """
    with pytest.raises(ValueError, match="nonzero"):
        ImagequantProcessor()(Image.new("RGB", size))


@pytest.mark.parametrize("skip_if_larger", [False, True])
def test_image_call_selects_by_png_size(skip_if_larger: bool):
    """Apply size selection during normal in-memory processing.

    Arguments:
        skip_if_larger: whether a larger indexed PNG should retain the input
    """
    image = Image.new("RGB", (1, 1), (32, 64, 96))

    output = ImagequantProcessor(skip_if_larger=skip_if_larger)(image)

    if skip_if_larger:
        assert output is image
    else:
        assert output.mode == "P"
        assert output.convert("RGB").getpixel((0, 0)) == (32, 64, 96)


def test_image_segment_uses_processor_size_selection():
    """Produce a smaller palette image through the ordinary image processor segment."""
    colors = np.array([[32, 64, 96], [255, 0, 0], [0, 255, 0]], dtype=np.uint8)
    indices = np.random.default_rng(168).integers(0, 3, (64, 64))
    pixels = colors[indices]
    image = PipeImage(image=Image.fromarray(pixels), name="source")

    output = ImageProcessorSegment(ImagequantProcessor())(image)[0]

    assert output.image.mode == "P"
    assert np.array_equal(np.array(output.image.convert("RGB")), pixels)
    assert output.parents == [image]


def test_partial_file_write_preserves_existing_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Clean up an interrupted temporary write while retaining the destination.

    Arguments:
        tmp_path: temporary test directory
        monkeypatch: pytest patch fixture
    """
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    Image.new("RGB", (2, 2), "red").save(input_path)
    Image.new("RGB", (2, 2), "blue").save(output_path)
    original_bytes = output_path.read_bytes()
    write_bytes = Path.write_bytes

    def fail(path: Path, data: bytes):
        """Write incomplete encoded bytes and simulate a storage failure.

        Arguments:
            path: temporary output path
            data: encoded image bytes
        Raises:
            OSError: always
        """
        write_bytes(path, data[:8])
        raise OSError("write failed")

    monkeypatch.setattr(Path, "write_bytes", fail)

    with pytest.raises(OSError, match="write failed"):
        ImagequantProcessor(skip_if_larger=False).process_file(input_path, output_path)

    assert output_path.read_bytes() == original_bytes
    assert set(tmp_path.iterdir()) == {input_path, output_path}


@pytest.mark.parametrize("in_place", [False, True])
def test_smaller_output_preserves_transparency(tmp_path: Path, in_place: bool):
    """Publish a smaller indexed PNG while preserving its visible pixels and alpha.

    Arguments:
        tmp_path: temporary test directory
        in_place: whether to replace the input file
    """
    palette = np.array(
        [[0, 0, 0, 0], [255, 0, 0, 128], [0, 255, 0, 255]], dtype=np.uint8
    )
    indices = np.random.default_rng(168).integers(0, 3, (64, 64))
    pixels = palette[indices]
    input_path = tmp_path / "O'Brien {input}.png"
    output_path = input_path if in_place else tmp_path / "O'Brien {output}.png"
    Image.fromarray(pixels).save(input_path, compress_level=0)
    original_bytes = input_path.read_bytes()

    ImagequantProcessor().process_file(input_path, output_path)

    assert output_path.stat().st_size < len(original_bytes)
    with Image.open(output_path) as output:
        assert output.mode == "P"
        rendered = np.array(output.convert("RGBA"))
        assert np.array_equal(rendered[..., 3], pixels[..., 3])
        assert np.array_equal(rendered[pixels[..., 3] > 0], pixels[pixels[..., 3] > 0])
    if not in_place:
        assert input_path.read_bytes() == original_bytes


@pytest.mark.parametrize("skip_if_larger", [False, True])
@pytest.mark.parametrize("in_place", [False, True])
def test_larger_output_selection(tmp_path: Path, skip_if_larger: bool, in_place: bool):
    """Retain exact original bytes for tiny images unless size selection is disabled.

    Arguments:
        tmp_path: temporary test directory
        skip_if_larger: whether to reject a larger encoded result
        in_place: whether input and output use the same path
    """
    input_path = tmp_path / "input.png"
    output_path = input_path if in_place else tmp_path / "output.png"
    Image.new("RGB", (1, 1), (32, 64, 96)).save(input_path, optimize=True)
    original_bytes = input_path.read_bytes()

    ImagequantProcessor(skip_if_larger=skip_if_larger).process_file(
        input_path, output_path
    )

    if skip_if_larger:
        assert output_path.read_bytes() == original_bytes
    else:
        assert output_path.stat().st_size > len(original_bytes)
        with Image.open(output_path) as output:
            assert output.mode == "P"
            assert output.convert("RGB").getpixel((0, 0)) == (32, 64, 96)


@pytest.mark.parametrize("skip_if_larger", [False, True])
def test_quality_rejection_copies_original(tmp_path: Path, skip_if_larger: bool):
    """Keep exact input bytes on quality rejection regardless of size settings.

    Arguments:
        tmp_path: temporary test directory
        skip_if_larger: whether to reject larger output
    """
    pixels = np.random.default_rng(168).integers(0, 256, (32, 32, 3), dtype=np.uint8)
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    Image.fromarray(pixels).save(input_path)

    ImagequantProcessor(
        max_colors=2,
        min_quality=100,
        skip_if_larger=skip_if_larger,
    ).process_file(input_path, output_path)

    assert output_path.read_bytes() == input_path.read_bytes()


def test_encoding_failure_preserves_existing_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Remove partial encodings and preserve any previously published output.

    Arguments:
        tmp_path: temporary test directory
        monkeypatch: pytest patch fixture
    """
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    Image.new("RGB", (2, 2), "red").save(input_path)
    Image.new("RGB", (2, 2), "blue").save(output_path)
    original_bytes = output_path.read_bytes()

    def fail(image: Image.Image, buffer: BytesIO, **kwargs: Any):
        """Write a partial PNG and fail.

        Arguments:
            image: unused output image
            buffer: temporary encoding buffer
            **kwargs: unused encoding settings
        Raises:
            OSError: always
        """
        buffer.write(b"partial PNG")
        raise OSError("encoding failed")

    monkeypatch.setattr(Image.Image, "save", fail)

    with pytest.raises(OSError, match="encoding failed"):
        ImagequantProcessor(skip_if_larger=False).process_file(input_path, output_path)

    assert output_path.read_bytes() == original_bytes
    assert set(tmp_path.iterdir()) == {input_path, output_path}


@pytest.mark.parametrize("invalid", ["input", "output", "animation"])
def test_invalid_formats(tmp_path: Path, invalid: str):
    """Reject incompatible formats without publishing incorrectly named PNG files.

    Arguments:
        tmp_path: temporary test directory
        invalid: format violation to exercise
    """
    input_path = tmp_path / "input.png"
    output_path = tmp_path / ("output.jpg" if invalid == "output" else "output.png")
    image = Image.new("RGB", (2, 2), "red")
    if invalid == "input":
        image.save(input_path, format="BMP")
    elif invalid == "animation":
        image.save(
            input_path,
            save_all=True,
            append_images=[Image.new("RGB", (2, 2), "blue")],
            duration=100,
        )
    else:
        image.save(input_path)

    with pytest.raises(ValueError):
        ImagequantProcessor().process_file(input_path, output_path)

    assert not output_path.exists()
    assert list(tmp_path.iterdir()) == [input_path]


@pytest.mark.parametrize("custom_settings", [False, True])
def test_checkpointed_quantization_resumes_without_processing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, custom_settings: bool
):
    """Write and reuse an image checkpoint through the existing file-callable API.

    Arguments:
        tmp_path: temporary test directory
        monkeypatch: pytest patch fixture
        custom_settings: whether to configure non-default processor settings
    """
    manager = ImageCheckpointManager(tmp_path / "checkpoints")
    if custom_settings:
        processor = ImagequantProcessor(
            max_colors=16,
            min_quality=0,
            skip_if_larger=False,
        )
    else:
        processor = ImagequantProcessor()
    segment = manager.post_runner("quantized.png")(processor.process_file)
    image = PipeImage(image=Image.new("RGB", (8, 8), "red"), name="source")
    output = segment(image)[0]
    assert output.path is not None
    original_bytes = output.path.read_bytes()
    if custom_settings:
        with Image.open(output.path) as saved_image:
            assert saved_image.mode == "P"

    def fail(processor: ImagequantProcessor, input_path: Path, output_path: Path):
        """Reject unexpected processing of a cached checkpoint.

        Arguments:
            processor: unused processor
            input_path: unused input path
            output_path: unused output path
        Raises:
            AssertionError: always
        """
        raise AssertionError("cached checkpoint was quantized again")

    monkeypatch.setattr(ImagequantProcessor, "process_file", fail)
    resumed = segment(image)[0]

    assert resumed.path == output.path
    assert resumed.path.read_bytes() == original_bytes
    assert resumed.name == image.name
    assert resumed.parents == [image]


@pytest.mark.parametrize("color_tag", ["gamma", "chromaticity", "srgb", "icc_profile"])
def test_color_metadata_survives_png_encoding(tmp_path: Path, color_tag: str):
    """Retain the color interpretation of a successfully quantized PNG.

    Arguments:
        tmp_path: temporary test directory
        color_tag: PNG color metadata to preserve
    """
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    image = Image.new("RGB", (64, 64), (128, 128, 128))
    png_info = PngInfo()
    if color_tag == "gamma":
        png_info.add(b"gAMA", pack(">I", 100000))
    elif color_tag == "chromaticity":
        png_info.add(
            b"cHRM", pack(">8I", 31270, 32900, 68000, 32000, 26500, 69000, 15000, 6000)
        )
    elif color_tag == "srgb":
        png_info.add(b"sRGB", b"\x00")
    else:
        image.info["icc_profile"] = ImageCms.ImageCmsProfile(
            ImageCms.createProfile("sRGB")
        ).tobytes()
    image.save(input_path, pnginfo=png_info, compress_level=0)
    with Image.open(input_path) as source:
        expected_metadata = source.info[color_tag]

    ImagequantProcessor().process_file(input_path, output_path)

    assert output_path.stat().st_size < input_path.stat().st_size
    with Image.open(output_path) as output:
        assert output.mode == "P"
        assert output.info[color_tag] == expected_metadata
        assert output.convert("RGB").getpixel((0, 0)) == (128, 128, 128)


@pytest.mark.parametrize("in_place", [False, True])
@pytest.mark.parametrize("skip_if_larger", [False, True])
def test_sixteen_bit_png_keeps_original_bytes(
    tmp_path: Path, in_place: bool, skip_if_larger: bool
):
    """Accept 16-bit grayscale PNGs without changing precision or original bytes.

    Arguments:
        tmp_path: temporary test directory
        in_place: whether input and output use the same path
        skip_if_larger: whether size selection is enabled
    """
    input_path = tmp_path / "input.png"
    output_path = input_path if in_place else tmp_path / "output.png"
    pixels = np.array([[0, 32768, 65535]], dtype=np.uint16)
    Image.fromarray(pixels).save(input_path)
    original_bytes = input_path.read_bytes()

    ImagequantProcessor(skip_if_larger=skip_if_larger).process_file(
        input_path, output_path
    )

    assert output_path.read_bytes() == original_bytes
    with Image.open(output_path) as output:
        assert output.mode == "I;16"
        assert np.array_equal(np.array(output), pixels)
