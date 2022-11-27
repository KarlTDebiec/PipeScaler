#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Segment that applies a Merger."""
from logging import info

from pipescaler.core.image import Merger
from pipescaler.core.pipelines.pipe_image import PipeImage
from pipescaler.core.pipelines.segments.operator_segment import OperatorSegment


class MergerSegment(OperatorSegment):
    """Segment that applies a Merger."""

    operator: Merger

    def __init__(self, operator: Merger) -> None:
        """Initialize.

        Arguments:
            operator: Merger to apply
        """
        super().__init__(operator)

    def __call__(self, *inputs: PipeImage) -> tuple[PipeImage]:
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
        output = PipeImage(output_image, parents=inputs)
        info(f"{self.operator}: {output.name} merged")

        return (output,)
