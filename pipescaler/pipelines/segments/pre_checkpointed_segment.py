#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Segment with pre-execution checkpoints."""
from __future__ import annotations

from logging import info

from pipescaler.core.pipelines import CheckpointedSegment, PipeObject


class PreCheckpointedSegment(CheckpointedSegment):
    """Segment with pre-execution checkpoints."""

    def __call__(self, *inputs: PipeObject) -> tuple[PipeObject, ...]:
        """Checkpoint inputs and return outputs of wrapped Segment.

        Inputs' paths are set to checkpoint paths before passing on to wrapped
        Segment.

        Arguments:
            inputs: Input objects, saved to checkpoints if not already present
        Returns:
            Output objects, within a tuple even if only one
        """
        if len(inputs) != len(self.cpts):
            raise ValueError(
                f"Expected {len(self.cpts)} inputs to {self.segment} "
                f"but received {len(inputs)}."
            )

        cpt_paths = [
            self.cp_manager.directory / i.location_name / c
            for i in inputs
            for c in self.cpts
        ]
        for i, c, p in zip(inputs, self.cpts, cpt_paths):
            if p.exists():
                i.path = p
            else:
                i.save(p)
                info(f"{self}: '{i.location_name}' checkpoint '{p}' saved")
            self.cp_manager.observe(i.location_name, c)

        if not hasattr(self.segment, "__call__"):
            raise TypeError(f"{self.segment} is not callable.")
        return self.segment(*inputs)
