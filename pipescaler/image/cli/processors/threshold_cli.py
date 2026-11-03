#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for ThresholdProcessor."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from pipescaler.common.argument_parsing import get_arg_groups_by_name, int_arg
from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.operators.processors import ThresholdProcessor

__all__ = ["ThresholdCli"]


class ThresholdCli(ImageProcessorCli):
    """Command-line interface for ThresholdProcessor."""

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
            "--threshold",
            default=128,
            type=int_arg(min_value=1, max_value=244),
            help="threshold differentiating black and white (1-244, "
            "default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--denoise",
            action="store_true",
            help="Flip color of pixels bordered by less than 5 pixels of "
            "the same color",
        )

    @classmethod
    def processor(cls) -> type[ThresholdProcessor]:
        """Type of processor wrapped by command-line interface.

        Returns:
            image processor class invoked by this command
        """
        return ThresholdProcessor

    @classmethod
    def _main(
        cls, *, input_path: Path, output_path: Path, threshold: int, denoise: bool
    ):
        """Execute with parsed image paths and operation settings.

        Arguments:
            input_path: input image path
            output_path: output image path
            threshold: grayscale cutoff
            denoise: whether to remove isolated pixels
        """
        processor_cls = cls.processor()
        cls.process_image(
            input_path=input_path,
            output_path=output_path,
            processor=processor_cls(threshold=threshold, denoise=denoise),
        )


if __name__ == "__main__":
    ThresholdCli.main()
