#!/usr/bin/env python
#   pipescaler/processors/mode_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
####################################### MODULES ########################################
from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from PIL import Image, ImageColor

from pipescaler.common import validate_str
from pipescaler.core import Processor


####################################### CLASSES ########################################
class ModeProcessor(Processor):
    modes = ["RGBA", "RGB", "L"]

    # region Builtins

    def __init__(
        self, mode: str = "RGB", background_color: str = "#000000", **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.mode = validate_str(mode, self.modes)
        self.background_color = ImageColor.getrgb(background_color)  # TODO: Validate

    def __call__(
        self, infile: str, outfile: str, verbosity: int = 1, **kwargs: Any
    ) -> None:
        self.process_file(
            infile,
            outfile,
            verbosity=verbosity,
            mode=self.mode,
            background_color=self.background_color,
            **kwargs,
        )

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Returns:
            parser (ArgumentParser): Argument parser
        """
        description = kwargs.get("description", __doc__.strip())
        parser = super().construct_argparser(description=description, **kwargs)

        # Operations
        parser.add_argument(
            "--mode",
            default="rgba",
            type=cls.str_arg(options=cls.modes),
            help="image mode ('RGBA', 'RGB', or 'L', default: %(default)s)",
        )
        parser.add_argument(
            "--background_color",
            default="#000000",
            type=str,
            help="background color (default: %(default)s)",
        )

        return parser

    @classmethod
    def process_file(
        cls, infile: str, outfile: str, verbosity: int = 1, **kwargs: Any
    ) -> None:
        mode = kwargs.get("mode", "RGB").upper()
        background_color = kwargs.get("background_color", ImageColor.getrgb("#000000"))
        input_image = Image.open(infile)

        if input_image.mode == mode:
            output_image = input_image
        else:
            output_image = Image.new("RGBA", input_image.size, background_color)
            output_image.paste(input_image)
            if mode == "RGBA":
                pass
            elif mode == "RGB":
                output_image = output_image.convert("RGB")
            elif mode == "L":
                output_image = output_image.convert("L")

        # Save image
        if verbosity >= 1:
            print(f"Saving {mode} image to '{outfile}'")
        output_image.save(outfile)

    # endregion


######################################### MAIN #########################################
if __name__ == "__main__":
    ModeProcessor.main()
