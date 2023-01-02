#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Upscales and/or denoises image using Waifu2x via an external executable."""
from __future__ import annotations

from PIL import Image

from pipescaler.common import get_temp_file_path
from pipescaler.image.core import validate_image_and_convert_mode
from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.runners import WaifuRunner


class WaifuExternalProcessor(ImageProcessor):
    """Upscales and/or denoises image using Waifu2x via an external executable.

    See [waifu2x](https://github.com/nagadomi/waifu2x).
    """

    def __init__(self, arguments: str) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            arguments: Command-line arguments to pass to waifu2x
        """
        super().__init__()

        self.waifu_runner = WaifuRunner(arguments)

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_image: Input image
        Returns:
            Processed output image
        """
        input_image, output_mode = validate_image_and_convert_mode(
            input_image, self.inputs()["input"], "RGB"
        )

        with get_temp_file_path(".png") as temp_input_path:
            with get_temp_file_path(".png") as temp_output_path:
                input_image.save(temp_input_path)
                self.waifu_runner.run(temp_input_path, temp_output_path)
                output_image = Image.open(temp_output_path)
        if output_image.mode != output_mode:
            output_image = output_image.convert(output_mode)

        return output_image

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(arguments={self.waifu_runner.arguments!r})"

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Upscales and/or denoises image using [Waifu2x]"
            "(https://github.com/nagadomi/waifu2x) via an external executable."
        )

    @classmethod
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        """Inputs to this operator."""
        return {
            "input": ("L", "RGB"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("L", "RGB"),
        }
