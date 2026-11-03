#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for native BC7 DDS encoding, headers, mipmaps, and atomic publication."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from struct import pack_into, unpack_from
from typing import cast

import ispc_texcomp
import numpy as np
import pytest
from PIL import Image

from pipescaler.common.file import get_temp_file_path
from pipescaler.image.core import UnsupportedImageModeError
from pipescaler.image.core.pipelines import PipeImage
from pipescaler.image.operators.processors import DdsProcessor
from pipescaler.image.operators.processors.dds_processor import DdsQuality
from pipescaler.image.pipelines import ImageCheckpointManager
from pipescaler.image.pipelines.segments import ImageProcessorSegment
from pipescaler.image.pipelines.termini import ImageDirectoryTerminus
from pipescaler.testing.file import get_test_input_path


def decode_levels(data: bytes) -> list[Image.Image]:
    """Decode every mip independently using Pillow's BC7 decoder.

    Arguments:
        data: complete DX10 DDS file
    Returns:
        decoded RGBA images, beginning with the base level
    """
    assert data[:4] == b"DDS "
    assert unpack_from("<I", data, 4)[0] == 124
    assert data[84:88] == b"DX10"
    assert unpack_from("<4I", data, 132) == (3, 0, 1, 1)
    height, width = unpack_from("<2I", data, 12)
    count = unpack_from("<I", data, 28)[0]
    offset = 148
    levels = []
    for _ in range(count):
        length = (width + 3) // 4 * ((height + 3) // 4) * 16
        header = bytearray(data[:148])
        pack_into("<4I", header, 12, height, width, length, 0)
        pack_into("<I", header, 28, 1)
        with Image.open(BytesIO(header + data[offset : offset + length])) as image:
            levels.append(image.copy())
        offset += length
        width, height = (max(1, width // 2), max(1, height // 2))
    assert offset == len(data)
    return levels


def process_image(processor: DdsProcessor, image: Image.Image) -> bytes:
    """Convert generated pixels through the processor's file interface.

    Arguments:
        processor: DDS compression settings
        image: generated or existing source pixels
    Returns:
        complete DDS bytes including the mip chain
    """
    with (
        get_temp_file_path(".png") as input_path,
        get_temp_file_path(".dds") as output_path,
    ):
        image.save(input_path)
        processor.process_file(input_path, output_path)
        return output_path.read_bytes()


def test_atomic_write_and_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Preserve existing DDS bytes and remove temporary files on encoder failure.

    Arguments:
        tmp_path: output directory
        monkeypatch: fixture for injecting a native encoder failure
    """
    output_path = tmp_path / "texture.dds"
    image = Image.new("RGBA", (8, 8), (32, 64, 96, 128))
    input_path = tmp_path / "source.png"
    image.save(input_path)
    DdsProcessor().process_file(input_path, output_path)
    original = output_path.read_bytes()
    assert len(decode_levels(original)) == 4

    def fail_encode(
        surface: ispc_texcomp.RGBASurface, settings: ispc_texcomp.BC7EncSettings
    ) -> bytes:
        """Simulate a native encoding failure.

        Arguments:
            surface: unused encoder surface
            settings: unused encoder settings
        Raises:
            OSError: always
        """
        raise OSError("encoding failed")

    monkeypatch.setattr(
        "pipescaler.image.operators.processors.dds_processor.ispc_texcomp.compress_blocks_bc7",
        fail_encode,
    )
    with pytest.raises(OSError, match="encoding failed"):
        DdsProcessor().process_file(input_path, output_path)
    assert output_path.read_bytes() == original
    assert set(tmp_path.iterdir()) == {input_path, output_path}


def test_in_place_file_conversion(tmp_path: Path):
    """Close the input before replacing it with DDS data.

    Arguments:
        tmp_path: directory for the image converted in place
    """
    path = tmp_path / "texture.dds"
    Image.new("RGBA", (8, 8), (32, 64, 96, 128)).save(path, format="PNG")
    DdsProcessor().process_file(path, path)
    assert len(decode_levels(path.read_bytes())) == 4
    assert list(tmp_path.iterdir()) == [path]


def test_invalid_configuration():
    """Reject negative mip counts and unknown quality presets."""
    with pytest.raises(ValueError):
        DdsProcessor(mipmaps=-1)
    with pytest.raises(ValueError):
        DdsProcessor(quality=cast(DdsQuality, "unknown"))


def test_invalid_image_or_mip_count():
    """Reject empty textures and chains longer than the image supports."""
    with pytest.raises(ValueError, match="positive"):
        DdsProcessor()(Image.new("RGBA", (0, 1)))
    with pytest.raises(ValueError, match="at most 3"):
        process_image(DdsProcessor(mipmaps=4), Image.new("RGBA", (4, 4)))


def test_palette_transparency():
    """Convert indexed transparency to the texture's alpha channel."""
    image = Image.frombytes("P", (2, 1), b"\x00\x01")
    image.putpalette([255, 0, 0, 0, 0, 255])
    image.info["transparency"] = bytes((0, 128))
    output = np.asarray(
        decode_levels(process_image(DdsProcessor(mipmaps=1), image))[0], dtype=int
    )
    assert np.abs(output[0] - ((255, 0, 0, 0), (0, 0, 255, 128))).max() <= 2


def test_partial_mip_chain():
    """Respect a mip count between base-only and the full chain."""
    data = process_image(DdsProcessor(mipmaps=2), Image.new("RGB", (16, 8)))
    assert [image.size for image in decode_levels(data)] == [(16, 8), (8, 4)]


def test_processor_segment():
    """Use the ordinary processor segment and retain detached decoded pixels."""
    source = PipeImage(image=Image.new("RGB", (8, 8), (32, 64, 96)), name="source")
    output = ImageProcessorSegment(DdsProcessor())(source)[0]
    assert output.path is None
    assert output.parents == [source]
    assert output.image.mode == "RGBA"
    assert output.image.size == source.image.size
    assert np.abs(np.asarray(output.image, dtype=int) - (32, 64, 96, 255)).max() <= 2


def test_repr_round_trip():
    """Recreate a processor with all nondefault options from its representation."""
    processor = DdsProcessor(mipmaps=1, quality="slow", srgb=True, separate_alpha=False)
    recreated = eval(repr(processor))
    assert repr(recreated) == repr(processor)


def test_unsupported_mode():
    """Reject unsupported image modes through the ordinary processor contract."""
    with pytest.raises(UnsupportedImageModeError):
        DdsProcessor()(Image.new("F", (4, 4)))


def test_varying_rgba_pixels():
    """Retain a varying color and alpha gradient within compression tolerance."""
    y, x = np.indices((16, 16))
    pixels = np.stack((x * 16, y * 16, (x + y) * 8, x * 16), axis=2).astype(np.uint8)
    output = decode_levels(
        process_image(DdsProcessor(mipmaps=1), Image.fromarray(pixels))
    )[0]
    assert np.abs(np.asarray(output, dtype=int) - pixels).mean() < 5


@pytest.mark.parametrize("separate_alpha", [False, True])
def test_alpha_filtering(separate_alpha: bool):
    """Control whether invisible color contributes to lower mip levels.

    Arguments:
        separate_alpha: whether to filter RGB independently of alpha
    """
    image = Image.frombytes("RGBA", (2, 1), bytes((255, 0, 0, 0, 0, 0, 255, 255)))
    data = process_image(DdsProcessor(separate_alpha=separate_alpha), image)
    output = np.asarray(decode_levels(data)[-1], dtype=int)[0, 0]
    expected = (128, 0, 128, 128) if separate_alpha else (0, 0, 255, 128)
    assert np.abs(output - expected).max() <= 2


@pytest.mark.parametrize(
    "size", [(1, 1), (1, 7), (7, 1), (3, 2), (5, 7), (8, 8), (13, 9)]
)
@pytest.mark.parametrize("mipmaps", [0, 1])
def test_dimensions_blocks_and_mip_tails(size: tuple[int, int], mipmaps: int):
    """Encode all blocks, including odd edges and mip tails smaller than 4x4.

    Arguments:
        size: base texture dimensions
        mipmaps: full chain or base-only output
    """
    color = (32, 64, 96, 128)
    image = Image.new("RGBA", size, color)
    data = process_image(DdsProcessor(mipmaps=mipmaps), image)
    levels = decode_levels(data)
    assert len(levels) == (max(size).bit_length() if mipmaps == 0 else 1)
    assert levels[0].size == size
    if mipmaps == 0:
        assert levels[-1].size == (1, 1)
    for level in levels:
        assert level.mode == "RGBA"
        assert np.abs(np.asarray(level, dtype=int) - color).max() <= 2
    assert bool(unpack_from("<I", data, 8)[0] & 131072) == (len(levels) > 1)
    assert bool(unpack_from("<I", data, 108)[0] & 4194312) == (len(levels) > 1)


@pytest.mark.parametrize("file_backed", [False, True])
def test_existing_checkpoint_path_preserves_dds_bytes(
    tmp_path: Path, file_backed: bool
):
    """Keep all mip levels through existing runner checkpoints and final output.

    Arguments:
        tmp_path: directory for source, checkpoint, and final files
        file_backed: whether the source starts from an existing file
    """
    manager = ImageCheckpointManager(tmp_path / "checkpoints")
    segment = manager.post_runner("99_dds.dds")(DdsProcessor().process_file)
    pixels = Image.new("RGBA", (8, 8), (32, 64, 96, 128))
    if file_backed:
        source_path = tmp_path / "source.one.png"
        pixels.save(source_path)
        source = PipeImage(path=source_path, location_path=Path("nested"))
    else:
        source = PipeImage(
            image=pixels, name="source.one", location_path=Path("nested")
        )
    output = segment(source)[0]
    cached = segment(source)[0]
    assert output.path is not None
    data = output.path.read_bytes()
    assert len(decode_levels(data)) == 4
    assert cached.path == output.path
    assert output.name == source.name
    assert output.location == source.location
    assert output.parents == [source]
    assert (source.location_name, "99_dds.dds") in manager.observed_checkpoints
    terminus = ImageDirectoryTerminus(tmp_path / "output")
    terminus(output)
    assert (terminus.dir_path / "nested" / "source.one.dds").read_bytes() == data


@pytest.mark.parametrize(
    "input_name", ["1", "L", "LA", "RGB", "RGBA", "PL", "PLA", "PRGB", "PRGBA"]
)
def test_input_modes_and_source_preservation(input_name: str):
    """Accept existing image modes while preserving input pixels and metadata.

    Arguments:
        input_name: existing source fixture name
    """
    with Image.open(get_test_input_path(input_name)) as image:
        pixels = image.tobytes()
        info = image.info.copy()
        output = DdsProcessor(mipmaps=1)(image)
        assert output.size == image.size
        assert output.mode == "RGBA"
        assert output.getpixel((0, 0)) is not None
        assert image.tobytes() == pixels
        assert image.info == info


@pytest.mark.parametrize("srgb", [False, True])
def test_premultiplied_mip_preserves_color_at_opaque_edges(srgb: bool):
    """Preserve constant straight RGB when Lanczos overshoots alpha at an edge.

    Arguments:
        srgb: whether RGB uses the sRGB transfer function
    """
    image = Image.new("RGBA", (8, 8), (64, 128, 192, 0))
    image.paste((64, 128, 192, 255), (4, 4, 8, 8))
    output = DdsProcessor(srgb=srgb, separate_alpha=False)._resize(image)
    assert output.getpixel((3, 3)) == (64, 128, 192, 255)


@pytest.mark.parametrize("quality", ["ultrafast", "veryfast", "fast", "basic", "slow"])
def test_quality_presets(quality: DdsQuality):
    """Use every quality preset with an alpha-bearing image.

    Arguments:
        quality: requested encoder search preset
    """
    image = Image.new("RGBA", (4, 4), (20, 80, 140, 60))
    output = decode_levels(
        process_image(DdsProcessor(quality=quality, mipmaps=1), image)
    )[0]
    assert np.abs(np.asarray(output, dtype=int) - (20, 80, 140, 60)).max() <= 2


@pytest.mark.parametrize("srgb, expected", [(False, 128), (True, 188)])
def test_srgb_metadata_and_linear_light_filtering(srgb: bool, expected: int):
    """Filter sRGB colors in linear light while keeping alpha linear.

    Arguments:
        srgb: whether source RGB uses sRGB
        expected: expected average RGB channel value after filtering
    """
    image = Image.frombytes("RGBA", (2, 1), bytes((0, 0, 0, 64, 255, 255, 255, 192)))
    data = process_image(DdsProcessor(srgb=srgb), image)
    assert unpack_from("<I", data, 128)[0] == (99 if srgb else 98)
    output = np.asarray(decode_levels(data)[-1], dtype=int)[0, 0]
    assert np.abs(output - (expected, expected, expected, 128)).max() <= 2
