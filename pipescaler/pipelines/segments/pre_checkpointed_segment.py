#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Segment with pre-execution checkpoints."""

from __future__ import annotations

from logging import info

from pipescaler.core.pipelines import CheckpointedSegment, PipeObject

__all__ = ["PreCheckpointedSegment"]


class PreCheckpointedSegment(CheckpointedSegment):
    """Segment with pre-execution checkpoints."""

    def __call__(self, *input_objs: PipeObject) -> tuple[PipeObject, ...]:
        """Checkpoint inputs and return outputs of wrapped Segment.

        Inputs' paths are set to checkpoint paths before passing on to wrapped
        Segment. Each input is paired with the checkpoint name at the same position.

        Arguments:
            *input_objs: input objects, saved to checkpoints if not already present
        Returns:
            output objects, within a tuple even if only one
        Raises:
            ValueError: if input values or configuration are invalid
        """
        if len(input_objs) != len(self.cpts):
            raise ValueError(
                f"Expected {len(self.cpts)} inputs to {self.segment} "
                f"but received {len(input_objs)}."
            )

        for input_obj, cpt in zip(input_objs, self.cpts):
            cpt_path = self.cp_manager.dir_path / input_obj.location_name / cpt
            if cpt_path.exists():
                input_obj.path = cpt_path
            else:
                input_obj.save(cpt_path)
                info(
                    f"{self}: '{input_obj.location_name}' checkpoint '{cpt_path}' saved"
                )
            self.cp_manager.observe(input_obj.location_name, cpt)

        if not hasattr(self.segment, "__call__"):
            raise ValueError(
                f"{self.__class__.__name__} requires a callable Segment; "
                f"{self.segment.__class__.__name__} is not callable."
            )
        return self.segment(*input_objs)
