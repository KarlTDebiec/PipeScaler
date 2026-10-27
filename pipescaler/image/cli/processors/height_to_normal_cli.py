#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for HeightToNormalProcessor."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from pipescaler.common.argument_parsing import float_arg, get_arg_groups_by_name
from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.operators.processors import HeightToNormalProcessor

__all__ = ["HeightToNormalCli"]


class HeightToNormalCli(ImageProcessorCli):
    """Command-line interface for HeightToNormalProcessor."""

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
            "--sigma",
            default=None,
            type=float_arg(min_value=0),
            help="Gaussian smoothing to apply to image before calculating normal map "
            "(default: %(default)s)",
        )

    @classmethod
    def processor(cls) -> type[HeightToNormalProcessor]:
        """Type of processor wrapped by command-line interface.

        Returns:
            image processor class invoked by this command
        """
        return HeightToNormalProcessor

    @classmethod
    def _main(cls, *, input_path: Path, output_path: Path, sigma: float | None):
        """Execute with parsed image paths and operation settings.

        Arguments:
            input_path: input image path
            output_path: output image path
            sigma: Gaussian smoothing before calculating normals
        """
        processor_cls = cls.processor()
        cls.process_image(
            input_path=input_path,
            output_path=output_path,
            processor=processor_cls(sigma=sigma),
        )


if __name__ == "__main__":
    HeightToNormalCli.main()
