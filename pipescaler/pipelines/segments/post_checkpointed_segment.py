#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Segment with post-execution checkpoints."""
from __future__ import annotations

from logging import info

from pipescaler.core.pipelines import CheckpointedSegment, PipeObject


class PostCheckpointedSegment(CheckpointedSegment):
    """Segment with post-execution checkpoints."""

    def __call__(self, *inputs: PipeObject) -> tuple[PipeObject, ...]:
        """Return outputs of wrapped Segment, loaded from checkpoints if available.

        Arguments:
            inputs: Input objects
        Returns:
            Output objects, loaded from checkpoint if available, within a tuple even if
            only one
        """
        cls = inputs[0].__class__
        cpt_paths = [
            self.cp_manager.directory / i.location_name / c
            for i in inputs
            for c in self.cpts
        ]
        if all(p.exists() for p in cpt_paths):
            outputs = tuple(cls(path=p, parents=inputs) for p in cpt_paths)
            info(
                f"{self}: '{inputs[0].location_name}' checkpoints '{self.cpts}' loaded"
            )
            for i in inputs:
                for c in self.internal_cpts:
                    self.cp_manager.observe(i.location_name, c)
        else:
            if not hasattr(self.segment, "__call__"):
                raise ValueError(
                    f"{self.__class__.__name__} requires a callable Segment; "
                    f"{self.segment.__class__.__name__} is not callable."
                )
            outputs = self.segment(*inputs)
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
        for i in inputs:
            for c in self.cpts:
                self.cp_manager.observe(i.location_name, c)

        return outputs
