#!/usr/bin/env python
#   pipescaler/processors/expand_processor.py
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
from logging import info
from typing import Any, Optional, Tuple

from PIL import Image

from pipescaler.common import validate_int, validate_ints
from pipescaler.core import Processor, expand_image


####################################### CLASSES ########################################
class ExpandProcessor(Processor):

    # region Builtins

    def __init__(self, expansion: Optional[Tuple[int]] = None, **kwargs: Any,) -> None:
        super().__init__(**kwargs)

        # Store configuration
        if expansion is None:
            expansion = (0, 0, 0, 0)
        self.expansion = validate_ints(expansion, length=4, min_value=0)

    # endregion

    # region Methods

    def __call__(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile, expansion=self.expansion)

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
            "--expansion",
            default=(0, 0, 0, 0),
            nargs=4,
            type=cls.ints_arg(length=4, min_value=0),
            help="number of pixels to add to left, top, right, and bottom "
            "(default: %(default)d)",
        )

        return parser

    @classmethod
    def process_file(cls, infile: str, outfile: str, **kwargs: Any) -> None:
        expansion = validate_ints(
            kwargs.get("expansion", (0, 0, 0, 0)), length=4, min_value=0
        )

        # Read image
        image = Image.open(infile)

        # Expand image
        expanded = expand_image(
            image, expansion[0], expansion[1], expansion[2], expansion[3]
        )

        # write image
        expanded.save(outfile)
        info(f"{cls}: '{outfile}' saved")

    # endregion


######################################### MAIN #########################################
if __name__ == "__main__":
    ExpandProcessor.main()
