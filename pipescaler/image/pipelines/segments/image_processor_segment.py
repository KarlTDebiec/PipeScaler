#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Segment that applies an ImageProcessor."""
from __future__ import annotations

from logging import info

from pipescaler.image.core.operators import ImageProcessor
from pipescaler.image.core.pipelines import ImageOperatorSegment, PipeImage


class ImageProcessorSegment(ImageOperatorSegment):
    """Segment that applies an ImageProcessor."""

    operator: ImageProcessor

    def __init__(self, operator: ImageProcessor) -> None:
        """Initialize.

        Arguments:
            operator: ImageProcessor to apply
        """
        super().__init__(operator)

    def __call__(self, *inputs: PipeImage) -> tuple[PipeImage, ...]:
        """Process an image.

        Arguments:
            inputs: Input image, within a tuple for consistency with other Segments
        Returns:
            Output image, within a tuple for consistency with other Segments
        """
        if len(inputs) != len(self.operator.inputs()):
            raise ValueError(
                f"{self.operator} requires {len(self.operator.inputs())} inputs, "
                f"but {len(inputs)} were provided."
            )

        input_image = inputs[0].image
        output_image = self.operator(input_image)
        output = PipeImage(image=output_image, parents=inputs[0])
        info(f"{self.operator}: '{inputs[0].location_name}' processed")

        return (output,)
