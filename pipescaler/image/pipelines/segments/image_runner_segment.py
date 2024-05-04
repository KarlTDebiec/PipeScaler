#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Segment that applies a Runner."""
from __future__ import annotations

from logging import warning

from pipescaler.common import get_temp_file_path
from pipescaler.core.typing import RunnerLike
from pipescaler.image.core.pipelines import ImageSegment, PipeImage


class ImageRunnerSegment(ImageSegment):
    """Segment that applies a Runner."""

    def __init__(
        self,
        runner: RunnerLike,
        input_extension: str = ".png",
        output_extension: str = ".png",
    ) -> None:
        """Initialize.

        Arguments:
            runner: Runner to apply
            input_extension: Extension of input file
            output_extension: Extension of output file
        """
        self.runner = runner
        """Runner to apply"""
        self.input_extension = input_extension
        """Extension of input file"""
        self.output_extension = output_extension
        """Extension of output file"""

    def __call__(self, *input_objs: PipeImage) -> tuple[PipeImage, ...]:
        """Receive input image and returns output image.

        Arguments:
            input_objs: Input image, within a tuple for consistency with other Segments
        Returns:
            Output image, within a tuple for consistency with other Segments
        """
        if len(input_objs) != 1:
            raise ValueError("RunnerSegment requires 1 input")

        with get_temp_file_path(self.output_extension) as output_path:
            if input_objs[0].path is None:
                with get_temp_file_path(self.input_extension) as input_path:
                    input_objs[0].image.save(input_path)
                    self.runner(input_path, output_path)
            else:
                self.runner(input_objs[0].path, output_path)
            output = PipeImage(path=output_path, parents=input_objs[0])
            warning(
                f"{self}: Output file is temporary and only image content is retained; "
                f"if output file is needed (e.g. if the purpose of this processor is "
                f"to convert an image to a specific format such as DDS), use a "
                f"PostCheckpointedImageRunnerSegment."
            )
        output.path = None

        return (output,)

    def __repr__(self) -> str:
        """Representation."""
        return (
            f"{self.__class__.__name__}(runner={self.runner!r},"
            f"input_extension={self.input_extension!r}, "
            f" output_extension={self.output_extension!r})"
        )
