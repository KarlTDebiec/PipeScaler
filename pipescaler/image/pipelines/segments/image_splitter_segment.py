#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Segment that applies an ImageSplitter."""
from __future__ import annotations

from logging import info

from pipescaler.image.core.operators import ImageSplitter
from pipescaler.image.core.pipelines import ImageOperatorSegment, PipeImage


class ImageSplitterSegment(ImageOperatorSegment):
    """Segment that applies a ImageSplitter."""

    operator: ImageSplitter

    def __init__(self, operator: ImageSplitter) -> None:
        """Initialize.

        Arguments:
            operator: Splitter to apply
        """
        super().__init__(operator)

    def __call__(self, *inputs: PipeImage) -> tuple[PipeImage, ...]:
        """Split an image.

        Arguments:
            inputs: Input image, within a tuple for consistency with other Segments
        Returns:
            Output images
        """
        if len(inputs) != len(self.operator.inputs()):
            raise ValueError(
                f"{self.operator} requires {len(self.operator.inputs())} inputs, "
                f"but {len(inputs)} were provided."
            )

        input_image = inputs[0].image
        output_images = self.operator(input_image)
        outputs = tuple(PipeImage(image=o, parents=inputs[0]) for o in output_images)
        info(f"{self.operator}: '{inputs[0].location_name}' split")

        return outputs
