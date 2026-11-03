#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for SpandrelProcessor."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from pipescaler.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    str_arg,
)
from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.operators.processors import SpandrelProcessor

__all__ = ["SpandrelCli"]


class SpandrelCli(ImageProcessorCli):
    """Command-line interface for SpandrelProcessor."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        arg_groups = get_arg_groups_by_name(
            parser,
            "input arguments",
            "operation arguments",
            "output arguments",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--model-input-path",
            required=True,
            type=input_file_arg(),
            help="input model file",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--device",
            default="auto",
            help="execution device: auto, cpu, cuda, cuda:N, mps, or mps:0",
        )
        arg_groups["operation arguments"].add_argument(
            "--precision",
            type=str_arg(options=SpandrelProcessor.precision_dtypes.keys()),
            default="float32",
            help="model precision: float32, float16, or bfloat16 (model-dependent)",
        )

    @classmethod
    def processor(cls) -> type[SpandrelProcessor]:
        """Type of processor wrapped by command-line interface.

        Returns:
            image processor class invoked by this command
        """
        return SpandrelProcessor

    @classmethod
    def _main(
        cls,
        *,
        input_path: Path,
        output_path: Path,
        model_input_path: Path,
        device: str,
        precision: str,
    ):
        """Execute with parsed image paths and operation settings.

        Arguments:
            input_path: input image path
            output_path: output image path
            model_input_path: input model file
            device: requested execution device
            precision: requested model precision
        """
        processor_cls = cls.processor()
        cls.process_image(
            input_path=input_path,
            output_path=output_path,
            processor=processor_cls(
                model_input_path=model_input_path, device=device, precision=precision
            ),
        )


if __name__ == "__main__":
    SpandrelCli.main()
