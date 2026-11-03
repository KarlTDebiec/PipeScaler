#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for SpandrelProcessor."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from pipescaler.common.argument_parsing import (
    float_arg,
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    str_arg,
)
from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.core.functions import RESAMPLE_METHODS
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
        operation = arg_groups["operation arguments"]
        operation.add_argument(
            "--tile-size",
            type=int_arg(min_value=4),
            help="maximum input tile dimension in pixels; default: full frame",
        )
        operation.add_argument(
            "--tile-overlap",
            type=int_arg(min_value=0),
            default=0,
            help="overlap in input pixels; smaller than tile size (default: 0)",
        )
        target = operation.add_mutually_exclusive_group()
        target.add_argument(
            "--target-scale",
            type=float_arg(min_value=0, min_exclusive=True, finite=True),
            help="final scale relative to input, after native-scale inference",
        )
        target.add_argument(
            "--target-size",
            nargs=2,
            type=int_arg(min_value=1),
            metavar=("WIDTH", "HEIGHT"),
            help="final dimensions in pixels, after native-scale inference",
        )
        operation.add_argument(
            "--resample",
            type=str_arg(options=RESAMPLE_METHODS),
            default="lanczos",
            help="final floating-point resize filter (default: lanczos)",
        )

    @classmethod
    def processor(cls) -> type[SpandrelProcessor]:
        """Type of processor wrapped by command-line interface.

        Returns:
            image processor class invoked by this command
        """
        return SpandrelProcessor

    @classmethod
    def _main(  # noqa: PLR0913
        cls,
        *,
        input_path: Path,
        output_path: Path,
        model_input_path: Path,
        device: str,
        precision: str,
        tile_size: int | None,
        tile_overlap: int,
        target_scale: float | None,
        target_size: list[int] | None,
        resample: str,
    ):
        """Execute with parsed image paths and operation settings.

        Arguments:
            input_path: input image path
            output_path: output image path
            model_input_path: input model file
            device: requested execution device
            precision: requested model precision
            tile_size: maximum input tile dimension in pixels
            tile_overlap: overlap in input pixels
            target_scale: final scale relative to input
            target_size: explicit final width and height
            resample: final resize filter name
        """
        processor_cls = cls.processor()
        cls.process_image(
            input_path=input_path,
            output_path=output_path,
            processor=processor_cls(
                model_input_path=model_input_path,
                device=device,
                precision=precision,
                tile_size=tile_size,
                tile_overlap=tile_overlap,
                target_scale=target_scale,
                target_size=None
                if target_size is None
                else (target_size[0], target_size[1]),
                resample=resample,
            ),
        )


if __name__ == "__main__":
    SpandrelCli.main()
