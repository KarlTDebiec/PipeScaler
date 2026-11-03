#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for ModeProcessor."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from pipescaler.common.argument_parsing import get_arg_groups_by_name, str_arg
from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.operators.processors import ModeProcessor
from pipescaler.image.operators.processors.mode_processor import ModeSetting

__all__ = ["ModeCli"]


class ModeCli(ImageProcessorCli):
    """Command-line interface for ModeProcessor."""

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
            "--mode",
            required=True,
            type=str_arg(options=ModeProcessor.inputs()["input"]),
            help=f"image mode ({ModeProcessor.inputs()['input']})",
        )

        arg_groups["operation arguments"].add_argument(
            "--background-color",
            default="#000000",
            type=str,
            help="background color of output image; only relevant if input image is "
            "RGBA or LA (default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--threshold",
            default=128,
            type=int,
            help="threshold for binary conversion; only relevant if mode=1) "
            "(default: %(default)s)",
        )

    @classmethod
    def processor(cls) -> type[ModeProcessor]:
        """Type of processor wrapped by command-line interface.

        Returns:
            image processor class invoked by this command
        """
        return ModeProcessor

    @classmethod
    def _main(
        cls,
        *,
        input_path: Path,
        output_path: Path,
        mode: ModeSetting,
        background_color: str,
        threshold: int,
    ):
        """Execute with parsed image paths and operation settings.

        Arguments:
            input_path: input image path
            output_path: output image path
            mode: output image mode
            background_color: background color for transparent pixels
            threshold: threshold for binary conversion
        """
        processor_cls = cls.processor()
        cls.process_image(
            input_path=input_path,
            output_path=output_path,
            processor=processor_cls(
                mode=mode, background_color=background_color, threshold=threshold
            ),
        )


if __name__ == "__main__":
    ModeCli.main()
