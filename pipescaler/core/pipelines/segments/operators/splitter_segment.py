#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Segment that applies a Splitter."""
from logging import info
from typing import Sequence

from pipescaler.core.image import Splitter
from pipescaler.core.pipelines.pipe_image import PipeImage
from pipescaler.core.pipelines.segments.operator_segment import OperatorSegment


class SplitterSegment(OperatorSegment):
    """Segment that applies a Splitter."""

    operator: Splitter

    def __init__(self, operator: Splitter) -> None:
        """Initializes.

        Arguments:
            operator: Splitter to apply
        """
        super().__init__(operator)

    def __call__(self, *inputs: PipeImage) -> Sequence[PipeImage]:
        """Receives input image and returns output images.

        Arguments:
            inputs: Input image
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
        outputs = tuple(PipeImage(o, parents=inputs[0]) for o in output_images)
        info(f"{self.operator}: {inputs[0].name} split")

        return outputs
