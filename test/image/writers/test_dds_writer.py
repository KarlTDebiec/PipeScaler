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

from pipescaler.image.writers import DdsWriter
from pipescaler.image.writers.dds_writer import DdsQuality
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
        length = ((width + 3) // 4) * ((height + 3) // 4) * 16
        header = bytearray(data[:148])
        pack_into("<4I", header, 12, height, width, length, 0)
        pack_into("<I", header, 28, 1)
        with Image.open(BytesIO(header + data[offset : offset + length])) as image:
            levels.append(image.copy())
        offset += length
        width, height = max(1, width // 2), max(1, height // 2)
    assert offset == len(data)
    return levels


def test_atomic_write_and_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Preserve existing DDS bytes and remove temporary files on encoder failure.

    Arguments:
        tmp_path: output directory
        monkeypatch: fixture for injecting a native encoder failure
    """
    output_path = tmp_path / "texture.dds"
    image = Image.new("RGBA", (8, 8), (32, 64, 96, 128))
    DdsWriter()(image, output_path)
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
        "pipescaler.image.writers.dds_writer.ispc_texcomp.compress_blocks_bc7",
        fail_encode,
    )
    with pytest.raises(OSError, match="encoding failed"):
        DdsWriter()(image, output_path)
    assert output_path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [output_path]


def test_invalid_configuration():
    """Reject negative mip counts and unknown quality presets."""
    with pytest.raises(ValueError):
        DdsWriter(mipmaps=-1)
    with pytest.raises(ValueError):
        DdsWriter(quality=cast(DdsQuality, "unknown"))


def test_invalid_image_or_mip_count():
    """Reject empty textures and chains longer than the image supports."""
    with pytest.raises(ValueError, match="positive"):
        DdsWriter().encode(Image.new("RGBA", (0, 1)))
    with pytest.raises(ValueError, match="at most 3"):
        DdsWriter(mipmaps=4).encode(Image.new("RGBA", (4, 4)))


def test_palette_transparency():
    """Convert indexed transparency to the texture's alpha channel."""
    image = Image.frombytes("P", (2, 1), b"\x00\x01")
    image.putpalette([255, 0, 0, 0, 0, 255])
    image.info["transparency"] = bytes((0, 128))
    output = np.asarray(decode_levels(DdsWriter(mipmaps=1).encode(image))[0], dtype=int)
    assert np.abs(output[0] - ((255, 0, 0, 0), (0, 0, 255, 128))).max() <= 2


def test_partial_mip_chain():
    """Respect a mip count between base-only and the full chain."""
    data = DdsWriter(mipmaps=2).encode(Image.new("RGB", (16, 8)))
    assert [image.size for image in decode_levels(data)] == [(16, 8), (8, 4)]


def test_repr_round_trip():
    """Recreate a writer with all nondefault options from its representation."""
    writer = DdsWriter(mipmaps=1, quality="slow", srgb=True, separate_alpha=False)
    recreated = eval(repr(writer))
    assert repr(recreated) == repr(writer)


def test_varying_rgba_pixels():
    """Retain a varying color and alpha gradient within compression tolerance."""
    y, x = np.indices((16, 16))
    pixels = np.stack((x * 16, y * 16, (x + y) * 8, x * 16), axis=2).astype(np.uint8)
    output = decode_levels(DdsWriter(mipmaps=1).encode(Image.fromarray(pixels)))[0]
    assert np.abs(np.asarray(output, dtype=int) - pixels).mean() < 5


@pytest.mark.parametrize("separate_alpha", [False, True])
def test_alpha_filtering(separate_alpha: bool):
    """Control whether invisible color contributes to lower mip levels.

    Arguments:
        separate_alpha: whether to filter RGB independently of alpha
    """
    image = Image.frombytes("RGBA", (2, 1), bytes((255, 0, 0, 0, 0, 0, 255, 255)))
    data = DdsWriter(separate_alpha=separate_alpha).encode(image)
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
    data = DdsWriter(mipmaps=mipmaps).encode(image)
    levels = decode_levels(data)

    assert len(levels) == (max(size).bit_length() if mipmaps == 0 else 1)
    assert levels[0].size == size
    if mipmaps == 0:
        assert levels[-1].size == (1, 1)
    for level in levels:
        assert level.mode == "RGBA"
        assert np.abs(np.asarray(level, dtype=int) - color).max() <= 2
    assert bool(unpack_from("<I", data, 8)[0] & 0x20000) == (len(levels) > 1)
    assert bool(unpack_from("<I", data, 108)[0] & 0x400008) == (len(levels) > 1)


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
        levels = decode_levels(DdsWriter(mipmaps=1).encode(image))
        assert levels[0].size == image.size
        assert image.tobytes() == pixels
        assert image.info == info


@pytest.mark.parametrize("quality", ["ultrafast", "veryfast", "fast", "basic", "slow"])
def test_quality_presets(quality: DdsQuality):
    """Use every quality preset with an alpha-bearing image.

    Arguments:
        quality: requested encoder search preset
    """
    image = Image.new("RGBA", (4, 4), (20, 80, 140, 60))
    output = decode_levels(DdsWriter(quality=quality, mipmaps=1).encode(image))[0]
    assert np.abs(np.asarray(output, dtype=int) - (20, 80, 140, 60)).max() <= 2


@pytest.mark.parametrize("srgb, expected", [(False, 128), (True, 188)])
def test_srgb_metadata_and_linear_light_filtering(srgb: bool, expected: int):
    """Filter sRGB colors in linear light while keeping alpha linear.

    Arguments:
        srgb: whether source RGB uses sRGB
        expected: expected average RGB channel value after filtering
    """
    image = Image.frombytes("RGBA", (2, 1), bytes((0, 0, 0, 64, 255, 255, 255, 192)))
    data = DdsWriter(srgb=srgb).encode(image)
    assert unpack_from("<I", data, 128)[0] == (99 if srgb else 98)
    output = np.asarray(decode_levels(data)[-1], dtype=int)[0, 0]
    assert np.abs(output - (expected, expected, expected, 128)).max() <= 2
