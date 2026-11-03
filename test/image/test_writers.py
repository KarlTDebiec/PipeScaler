#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for PNG size selection, exact fallback, and checkpoint integration."""

from __future__ import annotations

from pathlib import Path
from struct import pack
from typing import Any

import numpy as np
import pytest
from PIL import Image, ImageCms
from PIL.PngImagePlugin import PngInfo

from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.operators.processors import ImagequantProcessor
from pipescaler.image.pipelines import ImageCheckpointManager
from pipescaler.image.writers import ImagequantWriter


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

    ImagequantWriter()(input_path, output_path)

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

    ImagequantWriter(skip_if_larger=skip_if_larger)(input_path, output_path)

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

    ImagequantWriter(
        ImagequantProcessor(max_colors=2, min_quality=100),
        skip_if_larger=skip_if_larger,
    )(input_path, output_path)

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

    def fail(image: Image.Image, path: Path, **kwargs: Any):
        """Write a partial PNG and fail.

        Arguments:
            image: unused output image
            path: temporary encoding destination
            **kwargs: unused encoding settings
        Raises:
            OSError: always
        """
        path.write_bytes(b"partial PNG")
        raise OSError("encoding failed")

    monkeypatch.setattr(Image.Image, "save", fail)

    with pytest.raises(OSError, match="encoding failed"):
        ImagequantWriter()(input_path, output_path)

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
        ImagequantWriter()(input_path, output_path)

    assert not output_path.exists()
    assert list(tmp_path.iterdir()) == [input_path]


def test_checkpointed_writer_resumes_without_quantization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Write and reuse an image checkpoint through the existing file-callable API.

    Arguments:
        tmp_path: temporary test directory
        monkeypatch: pytest patch fixture
    """
    manager = ImageCheckpointManager(tmp_path / "checkpoints")
    segment = manager.post_runner("quantized.png")(ImagequantWriter())
    image = PipeImage(image=Image.new("RGB", (8, 8), "red"), name="source")
    output = segment(image)[0]
    assert output.path is not None
    original_bytes = output.path.read_bytes()

    def fail(processor: ImagequantProcessor, image: Image.Image) -> Image.Image:
        """Reject unexpected processing of a cached checkpoint.

        Arguments:
            processor: unused processor
            image: unused image
        Raises:
            AssertionError: always
        """
        raise AssertionError("cached checkpoint was quantized again")

    monkeypatch.setattr(ImagequantProcessor, "__call__", fail)
    resumed = segment(image)[0]

    assert resumed.path == output.path
    assert resumed.path.read_bytes() == original_bytes
    assert resumed.name == image.name
    assert resumed.parents == [image]


def test_repr_round_trip():
    """Reconstruct a writer together with its quantization and size settings."""
    writer = ImagequantWriter(
        ImagequantProcessor(max_colors=16, min_quality=0), skip_if_larger=False
    )

    assert repr(eval(repr(writer))) == repr(writer)


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

    ImagequantWriter()(input_path, output_path)

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

    ImagequantWriter(skip_if_larger=skip_if_larger)(input_path, output_path)

    assert output_path.read_bytes() == original_bytes
    with Image.open(output_path) as output:
        assert output.mode == "I;16"
        assert np.array_equal(np.array(output), pixels)
