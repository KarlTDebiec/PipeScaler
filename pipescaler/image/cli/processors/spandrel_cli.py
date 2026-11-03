#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for SpandrelProcessor."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from pipescaler.common.argument_parsing import get_arg_groups_by_name, input_file_arg
from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.operators.processors import SpandrelProcessor

__all__ = ["SpandrelCli"]


class SpandrelCli(ImageProcessorCli):
    """Command-line interface for SpandrelProcessor."""

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
            "output arguments",
            optional_arguments_name="additional arguments",
        )

        arg_groups["input arguments"].add_argument(
            "--model-input-path",
            required=True,
            type=input_file_arg(),
            help="input model file",
        )

    @classmethod
    def processor(cls) -> type[SpandrelProcessor]:
        """Type of processor wrapped by command-line interface.

        Returns:
            image processor class invoked by this command
        """
        return SpandrelProcessor

    @classmethod
    def _main(cls, *, input_path: Path, output_path: Path, model_input_path: Path):
        """Execute with parsed image paths and operation settings.

        Arguments:
            input_path: input image path
            output_path: output image path
            model_input_path: input model file
        """
        processor_cls = cls.processor()
        cls.process_image(
            input_path=input_path,
            output_path=output_path,
            processor=processor_cls(model_input_path=model_input_path),
        )


if __name__ == "__main__":
    SpandrelCli.main()
