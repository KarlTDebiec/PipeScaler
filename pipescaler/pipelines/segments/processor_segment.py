#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Segment that applies a Processor."""
from logging import info

from pipescaler.core.image import Processor
from pipescaler.core.pipelines import OperatorSegment, PipeImage


class ProcessorSegment(OperatorSegment):
    """Segment that applies a Processor."""

    operator: Processor

    def __init__(self, operator: Processor) -> None:
        """Initialize.

        Arguments:
            operator: Processor to apply
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
        output = PipeImage(output_image, parents=inputs[0])
        info(f"{self.operator}: '{inputs[0].location_name}' processed")

        return (output,)
