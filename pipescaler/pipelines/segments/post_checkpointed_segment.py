#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Segment with post-execution checkpoints."""

from __future__ import annotations

from logging import info

from pipescaler.core.pipelines import CheckpointedSegment, PipeObject

__all__ = ["PostCheckpointedSegment"]


class PostCheckpointedSegment(CheckpointedSegment):
    """Segment with post-execution checkpoints."""

    def __call__(self, *input_objs: PipeObject) -> tuple[PipeObject, ...]:
        """Return outputs of wrapped Segment, loaded from checkpoints if available.

        All output checkpoints use the first input's location and name. A cached
        call returns one object per checkpoint with all inputs retained as parents.

        Arguments:
            *input_objs: input objects
        Returns:
            output objects, loaded from checkpoint if available, within a tuple even if
            only one
        Raises:
            ValueError: if input values or configuration are invalid
        """
        cls = input_objs[0].__class__
        location_name = input_objs[0].location_name
        cpt_paths = [self.cp_manager.dir_path / location_name / c for c in self.cpts]
        if all(p.exists() for p in cpt_paths) and self.cp_manager.checkpoints_current(
            input_objs, cpt_paths
        ):
            outputs = tuple(cls(path=p, parents=input_objs) for p in cpt_paths)
            info(f"{self}: '{location_name}' checkpoints '{self.cpts}' loaded")
            for i in input_objs:
                for c in self.internal_cpts:
                    self.cp_manager.observe(i.location_name, c)
        else:
            if not hasattr(self.segment, "__call__"):
                raise ValueError(
                    f"{self.__class__.__name__} requires a callable Segment; "
                    f"{self.segment.__class__.__name__} is not callable."
                )
            outputs = self.segment(*input_objs)
            if len(outputs) != len(self.cpts):
                raise ValueError(
                    f"Expected {len(self.cpts)} outputs from {self.segment} "
                    f"but received {len(outputs)}."
                )
            if not cpt_paths[0].parent.exists():
                cpt_paths[0].parent.mkdir(parents=True)
            for o, c, p in zip(outputs, self.cpts, cpt_paths):
                o.save(p)
                info(f"{self}: '{o.location_name}' checkpoint '{c}' saved")
        for c in self.cpts:
            self.cp_manager.observe(location_name, c)

        return outputs
