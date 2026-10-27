#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for ExpandProcessor."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from pipescaler.common.argument_parsing import get_arg_groups_by_name, int_arg
from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.operators.processors import ExpandProcessor

__all__ = ["ExpandCli"]


class ExpandCli(ImageProcessorCli):
    """Command-line interface for ExpandProcessor."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        arg_groups = get_arg_groups_by_name(
            parser,
            "input arguments",
            "operation arguments",
            "output arguments",
            optional_arguments_name="additional arguments",
        )

        arg_groups["operation arguments"].add_argument(
            "--pixels",
            default=[0, 0, 0, 0],
            metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
            nargs=4,
            type=int_arg(min_value=0),
            help="number of pixels to add to left, top, right, and bottom "
            "(default: %(default)s)",
        )

    @classmethod
    def processor(cls) -> type[ExpandProcessor]:
        """Type of processor wrapped by command-line interface.

        Returns:
            image processor class invoked by this command
        """
        return ExpandProcessor

    @classmethod
    def _main(
        cls,
        *,
        input_path: Path,
        output_path: Path,
        pixels: list[int],
    ):
        """Execute with parsed image paths and operation settings.

        Arguments:
            input_path: input image path
            output_path: output image path
            pixels: pixels to add to left, top, right, and bottom
        """
        processor_cls = cls.processor()
        cls.process_image(
            input_path=input_path,
            output_path=output_path,
            processor=processor_cls(
                pixels=(pixels[0], pixels[1], pixels[2], pixels[3])
            ),
        )


if __name__ == "__main__":
    ExpandCli.main()
