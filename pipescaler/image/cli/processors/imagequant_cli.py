#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for library-based PNG quantization."""

from __future__ import annotations

from argparse import ArgumentParser, BooleanOptionalAction
from pathlib import Path

from pipescaler.common.argument_parsing import (
    float_arg,
    get_arg_groups_by_name,
    int_arg,
)
from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.operators.processors import ImagequantProcessor

__all__ = ["ImagequantCli"]


class ImagequantCli(ImageProcessorCli):
    """Quantizes static PNGs, retaining original bytes on quality or size fallback."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add PNG quantization and output-selection arguments.

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

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--max-colors",
            type=int_arg(min_value=2, max_value=256),
            default=256,
            help="maximum palette size (2-256, default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--min-quality",
            type=int_arg(min_value=0, max_value=100),
            default=10,
            help="minimum acceptable quality (0-100, default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--max-quality",
            type=int_arg(min_value=0, max_value=100),
            default=100,
            help="target quality (0-100, default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--dithering-level",
            type=float_arg(min_value=0, max_value=1, finite=True),
            default=0.0,
            help="dithering strength (0-1, default: %(default)s)",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "--skip-if-larger",
            action=BooleanOptionalAction,
            default=True,
            help="retain original bytes unless output is smaller (default: enabled)",
        )

    @classmethod
    def processor(cls) -> type[ImagequantProcessor]:
        """Identify the in-memory quantizer.

        Returns:
            image processor class invoked by this command
        """
        return ImagequantProcessor

    @classmethod
    def _main(  # noqa: PLR0913
        cls,
        *,
        input_path: Path,
        output_path: Path,
        max_colors: int,
        min_quality: int,
        max_quality: int,
        dithering_level: float,
        skip_if_larger: bool,
    ):
        """Quantize and save a PNG using the parsed settings.

        Arguments:
            input_path: static PNG input file
            output_path: PNG output file
            max_colors: maximum palette size
            min_quality: minimum acceptable quality
            max_quality: target quality
            dithering_level: dithering strength
            skip_if_larger: whether to retain original bytes unless output is smaller
        """
        processor = cls.processor()(
            max_colors=max_colors,
            min_quality=min_quality,
            max_quality=max_quality,
            dithering_level=dithering_level,
            skip_if_larger=skip_if_larger,
        )
        processor.process_file(input_path, output_path)


if __name__ == "__main__":
    ImagequantCli.main()
