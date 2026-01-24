#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Segment that applies an ImageSplitter."""

from __future__ import annotations

from logging import info

from pipescaler.image.core.operators import ImageSplitter
from pipescaler.image.core.pipelines import ImageOperatorSegment, PipeImage


class ImageSplitterSegment(ImageOperatorSegment[ImageSplitter]):
    """Segment that applies a ImageSplitter."""

    def __call__(self, *input_objs: PipeImage) -> tuple[PipeImage, ...]:
        """Split an image.

        Arguments:
            input_objs: Input image, within a tuple for consistency with other Segments
        Returns:
            Output images
        """
        if len(input_objs) != len(self.operator.inputs()):
            raise ValueError(
                f"{self.operator} requires {len(self.operator.inputs())} inputs, "
                f"but {len(input_objs)} were provided."
            )

        input_image = input_objs[0].image
        output_images = self.operator(input_image)
        outputs = tuple(
            PipeImage(image=o, parents=input_objs[0]) for o in output_images
        )
        info(f"{self.operator}: '{input_objs[0].location_name}' split")

        return outputs
