#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Encode two-dimensional BC7 DDS textures without an external executable."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from struct import pack
from typing import Literal, cast

import ispc_texcomp
import numpy as np
from PIL import Image
from PIL.DdsImagePlugin import D3DFMT, DDPF, DDSCAPS, DDSD, DXGI_FORMAT

from pipescaler.common.file import get_temp_file_path
from pipescaler.common.validation import val_int, val_literal, val_output_path

__all__ = ["DdsQuality", "DdsWriter"]

type DdsQuality = Literal["ultrafast", "veryfast", "fast", "basic", "slow"]
"""BC7 encoder search presets, ordered from fastest to most thorough."""


class DdsWriter:
    """Write BC7 DDS textures with straight alpha and optional mipmaps.

    Compression runs on the CPU through `ispc-texcomp`. Only ordinary 2D BC7
    textures are supported; arrays, cubemaps, and HDR formats are not supported.
    The source image is converted to RGBA without changing its pixels in place.
    Every mip level is padded by repeating edge pixels to complete 4x4 blocks;
    the DDS retains the original dimensions, including sizes smaller than 4x4.

    Mipmaps use Lanczos filtering. With `srgb=True`, RGB is filtered in linear
    light and stored as sRGB; alpha is always linear. `separate_alpha=True`
    filters RGB independently of alpha, matching the intent of texconv's
    `-sepalpha`. Otherwise RGB is premultiplied during filtering, then restored
    to straight alpha. Compressed bytes and filtering are not identical to texconv.
    """

    def __init__(
        self,
        *,
        mipmaps: int = 0,
        quality: DdsQuality = "basic",
        srgb: bool = False,
        separate_alpha: bool = True,
    ):
        """Validate and store texture encoding options.

        Arguments:
            mipmaps: total mip levels including the base; 0 generates the full
              chain through 1x1, and 1 writes only the base image
            quality: encoder search preset; slower presets search more thoroughly
            srgb: whether pixels represent sRGB and the DDS uses BC7_UNORM_SRGB;
              false stores BC7_UNORM without applying a transfer function
            separate_alpha: whether to filter RGB and alpha independently
        Raises:
            ValueError: if mipmaps is negative or quality is unknown
        """
        self.mipmaps = val_int(mipmaps, min_value=0)
        """Requested number of mip levels; zero means the full chain."""
        self.quality = val_literal(quality, DdsQuality)
        """BC7 compression search preset."""
        self.srgb = srgb
        """Whether RGB uses the sRGB transfer function and format metadata."""
        self.separate_alpha = separate_alpha
        """Whether RGB is filtered independently of alpha."""

    def __call__(self, image: Image.Image, output_path: Path | str):
        """Encode an image and atomically replace the destination file.

        Arguments:
            image: source pixels in a Pillow mode convertible to RGBA
            output_path: destination DDS file, including its extension
        Raises:
            ValueError: if the image size or mip count is invalid
            OSError: if encoding or writing fails; an existing file is preserved
        """
        output_path = val_output_path(output_path, exist_ok=True)
        with get_temp_file_path(
            output_path.suffix, parent_dir_path=output_path.parent
        ) as temp_path:
            temp_path.write_bytes(self.encode(image))
            temp_path.replace(output_path)

    def __repr__(self) -> str:
        """Describe the encoding configuration.

        Returns:
            reconstructible writer configuration
        """
        return (
            f"{self.__class__.__name__}(mipmaps={self.mipmaps!r}, "
            f"quality={self.quality!r}, srgb={self.srgb!r}, "
            f"separate_alpha={self.separate_alpha!r})"
        )

    def encode(self, image: Image.Image) -> bytes:
        """Encode a complete DDS file in memory.

        Arguments:
            image: source pixels in a Pillow mode convertible to RGBA
        Returns:
            DDS header, DX10 extension, and BC7 blocks for all mip levels
        Raises:
            ValueError: if a dimension is zero or mipmaps exceeds the full chain
            OSError: if the native encoder returns an invalid block count
        """
        if min(image.size) < 1:
            raise ValueError("DDS image dimensions must be positive.")
        full_count = max(image.size).bit_length()
        mip_count = self.mipmaps or full_count
        if mip_count > full_count:
            raise ValueError(
                f"Requested {mip_count} mip levels, but {image.size} permits "
                f"at most {full_count}."
            )

        flags = (
            DDSD.CAPS | DDSD.HEIGHT | DDSD.WIDTH | DDSD.PIXELFORMAT | DDSD.LINEARSIZE
        )
        caps = DDSCAPS.TEXTURE
        if mip_count > 1:
            flags |= DDSD.MIPMAPCOUNT
            caps |= DDSCAPS.COMPLEX | DDSCAPS.MIPMAP
        linear_size = ((image.width + 3) // 4) * ((image.height + 3) // 4) * 16
        output = BytesIO()
        output.write(b"DDS ")
        output.write(
            pack(
                "<31I",
                124,
                flags,
                image.height,
                image.width,
                linear_size,
                0,
                mip_count,
                *([0] * 11),
                32,
                DDPF.FOURCC,
                D3DFMT.DX10,
                *([0] * 5),
                caps,
                *([0] * 4),
            )
        )
        output.write(
            pack(
                "<5I",
                DXGI_FORMAT.BC7_UNORM_SRGB if self.srgb else DXGI_FORMAT.BC7_UNORM,
                3,  # 2D texture
                0,
                1,  # one texture
                1,  # straight alpha
            )
        )

        profile = cast("ispc_texcomp.BC7EncProfile", f"alpha_{self.quality}")
        settings = ispc_texcomp.BC7EncSettings.from_profile(profile)
        mip = image.convert("RGBA")
        for level in range(mip_count):
            # The native binding requires complete blocks, even for 1x1 mip tails
            pixels = np.pad(
                np.asarray(mip),
                ((0, -mip.height % 4), (0, -mip.width % 4), (0, 0)),
                mode="edge",
            )
            surface = ispc_texcomp.RGBASurface(
                pixels.tobytes(), pixels.shape[1], pixels.shape[0]
            )
            blocks = ispc_texcomp.compress_blocks_bc7(surface, settings)
            if len(blocks) != pixels.shape[0] * pixels.shape[1]:
                raise OSError("BC7 encoder returned an invalid block count.")
            output.write(blocks)
            if level + 1 < mip_count:
                mip = self._resize(mip)
        return output.getvalue()

    def _resize(self, image: Image.Image) -> Image.Image:
        """Generate the next mip level with the configured transfer and alpha rules.

        Arguments:
            image: RGBA pixels of the preceding mip level
        Returns:
            next RGBA mip level with each dimension halved, down to one
        """
        pixels = np.asarray(image, dtype=np.float32) / 255
        rgb = pixels[:, :, :3]
        if self.srgb:
            rgb = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
        if not self.separate_alpha:
            rgb = rgb * pixels[:, :, 3:4]
        pixels = np.concatenate((rgb, pixels[:, :, 3:4]), axis=2)
        size = (max(1, image.width // 2), max(1, image.height // 2))
        resized = np.stack(
            [
                np.asarray(
                    Image.fromarray(pixels[:, :, channel]).resize(
                        size, Image.Resampling.LANCZOS
                    )
                )
                for channel in range(4)
            ],
            axis=2,
        )
        alpha = resized[:, :, 3:4]
        rgb = resized[:, :, :3]
        if not self.separate_alpha:
            rgb = np.divide(rgb, alpha, out=np.zeros_like(rgb), where=alpha > 0)
        alpha = alpha.clip(0, 1)
        rgb = rgb.clip(0, 1)
        if self.srgb:
            rgb = np.where(
                rgb <= 0.0031308, rgb * 12.92, 1.055 * rgb ** (1 / 2.4) - 0.055
            )
        pixels = np.concatenate((rgb, alpha), axis=2)
        return Image.fromarray(np.rint(pixels * 255).astype(np.uint8))
