#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Segment that applies an ImageMerger."""
from __future__ import annotations

from logging import info

from pipescaler.image.core.operators import ImageMerger
from pipescaler.image.core.pipelines import ImageOperatorSegment, PipeImage


class ImageMergerSegment(ImageOperatorSegment):
    """Segment that applies an ImageMerger."""

    operator: ImageMerger

    def __init__(self, operator: ImageMerger) -> None:
        """Initialize.

        Arguments:
            operator: ImageMerger to apply
        """
        super().__init__(operator)

    def __call__(self, *input_objs: PipeImage) -> tuple[PipeImage, ...]:
        """Merge images.

        Arguments:
            input_objs: Input images
        Returns:
            Output image, within a tuple for consistency with other Segments
        """
        if len(input_objs) != len(self.operator.inputs()):
            raise ValueError(
                f"{self.operator} requires {len(self.operator.inputs())} inputs, "
                f"but {len(input_objs)} were provided."
            )

        input_images = tuple(i.image for i in input_objs)
        output_image = self.operator(*input_images)
        output = PipeImage(image=output_image, parents=input_objs)
        info(f"{self.operator}: '{output.location_name}' merged")

        return (output,)
