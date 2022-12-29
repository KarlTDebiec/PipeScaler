#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Segment that applies an image merger."""
from __future__ import annotations

from logging import info

from pipescaler.image.core.operators import ImageMerger
from pipescaler.image.core.pipelines import ImageOperatorSegment, PipeImage


class ImageMergerSegment(ImageOperatorSegment):
    """Segment that applies a Merger."""

    operator: ImageMerger

    def __init__(self, operator: ImageMerger) -> None:
        """Initialize.

        Arguments:
            operator: Merger to apply
        """
        super().__init__(operator)

    def __call__(self, *inputs: PipeImage) -> tuple[PipeImage, ...]:
        """Merge images.

        Arguments:
            inputs: Input images
        Returns:
            Output image, within a tuple for consistency with other Segments
        """
        if len(inputs) != len(self.operator.inputs()):
            raise ValueError(
                f"{self.operator} requires {len(self.operator.inputs())} inputs, "
                f"but {len(inputs)} were provided."
            )

        input_images = tuple(i.image for i in inputs)
        output_image = self.operator(*input_images)
        output = PipeImage(image=output_image, parents=inputs)
        info(f"{self.operator}: '{output.location_name}' merged")

        return (output,)
