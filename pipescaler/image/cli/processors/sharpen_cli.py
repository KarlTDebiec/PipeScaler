#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for SharpenProcessor."""

from __future__ import annotations

from pathlib import Path

from pipescaler.image.core.cli import ImageProcessorCli
from pipescaler.image.operators.processors import SharpenProcessor

__all__ = ["SharpenCli"]


class SharpenCli(ImageProcessorCli):
    """Command-line interface for SharpenProcessor."""

    @classmethod
    def processor(cls) -> type[SharpenProcessor]:
        """Type of processor wrapped by command-line interface.

        Returns:
            image processor class invoked by this command
        """
        return SharpenProcessor

    @classmethod
    def _main(cls, *, input_path: Path, output_path: Path):
        """Execute with parsed image paths and operation settings.

        Arguments:
            input_path: input image path
            output_path: output image path
        """
        processor_cls = cls.processor()
        cls.process_image(
            input_path=input_path,
            output_path=output_path,
            processor=processor_cls(),
        )


if __name__ == "__main__":
    SharpenCli.main()
