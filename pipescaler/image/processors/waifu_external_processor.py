#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Upscales and/or denoises image using Waifu2x via an external executable."""
from __future__ import annotations

from typing import Any

from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.core.image import Processor
from pipescaler.core.validation import validate_mode
from pipescaler.runners import WaifuRunner


class WaifuExternalProcessor(Processor):
    """Upscales and/or denoises image using Waifu2x via an external executable.

    See [waifu2x](https://github.com/nagadomi/waifu2x).
    """

    def __init__(self, arguments: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.waifu_runner = WaifuRunner(arguments)

    def __call__(self, input_image: Image.Image) -> Image.Image:
        input_image, output_mode = validate_mode(
            input_image, self.inputs["input"], "RGB"
        )

        with temporary_filename(".png") as temp_infile:
            with temporary_filename(".png") as temp_outfile:
                input_image.save(temp_infile)
                self.waifu_runner.run(temp_infile, temp_outfile)
                output_image = Image.open(temp_outfile)
        if output_image.mode != output_mode:
            output_image = output_image.convert(output_mode)

        return output_image

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Upscales and/or denoises image using [Waifu2x]"
            "(https://github.com/nagadomi/waifu2x) via an external executable."
        )

    @classmethod
    @property
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "input": ("L", "RGB"),
        }

    @classmethod
    @property
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        return {
            "output": ("L", "RGB"),
        }
