#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for SolidColorProcessor."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from pipescaler.common.argument_parsing import float_arg, get_arg_groups_by_name
from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.operators.processors import SolidColorProcessor

__all__ = ["SolidColorCli"]


class SolidColorCli(ImageProcessorCli):
    """Command-line interface for SolidColorProcessor."""

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
            "--scale",
            default=1,
            type=float_arg(min_value=0),
            help="scaling factor (default: %(default)s)",
        )

    @classmethod
    def processor(cls) -> type[SolidColorProcessor]:
        """Type of processor wrapped by command-line interface.

        Returns:
            image processor class invoked by this command
        """
        return SolidColorProcessor

    @classmethod
    def _main(cls, *, input_path: Path, output_path: Path, scale: float):
        """Execute with parsed image paths and operation settings.

        Arguments:
            input_path: input image path
            output_path: output image path
            scale: output scale relative to the input
        """
        processor_cls = cls.processor()
        cls.process_image(
            input_path=input_path,
            output_path=output_path,
            processor=processor_cls(scale=scale),
        )


if __name__ == "__main__":
    SolidColorCli.main()
