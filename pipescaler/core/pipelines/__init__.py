#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Core classes and functions related to pipelines."""
from __future__ import annotations

from pipescaler.core.pipelines.checkpoint_manager_base import CheckpointManagerBase
from pipescaler.core.pipelines.pipe_image import PipeImage
from pipescaler.core.pipelines.segment import Segment
from pipescaler.core.pipelines.segments.checkpointed.post_checkpointed_runner_segment import (
    PostCheckpointedRunnerSegment,
)
from pipescaler.core.pipelines.segments.checkpointed.post_checkpointed_segment import (
    PostCheckpointedSegment,
)
from pipescaler.core.pipelines.segments.checkpointed.pre_checkpointed_segment import (
    PreCheckpointedSegment,
)
from pipescaler.core.pipelines.segments.checkpointed_segment import CheckpointedSegment
from pipescaler.core.pipelines.segments.operator_segment import OperatorSegment
from pipescaler.core.pipelines.segments.operators.merger_segment import MergerSegment
from pipescaler.core.pipelines.segments.operators.processor_segment import (
    ProcessorSegment,
)
from pipescaler.core.pipelines.segments.operators.splitter_segment import (
    SplitterSegment,
)
from pipescaler.core.pipelines.segments.runner_segment import RunnerSegment
from pipescaler.core.pipelines.sorter import Sorter
from pipescaler.core.pipelines.source import Source
from pipescaler.core.pipelines.terminus import Terminus

__all__: list[str] = [
    "CheckpointedSegment",
    "CheckpointManagerBase",
    "MergerSegment",
    "OperatorSegment",
    "PipeImage",
    "PostCheckpointedRunnerSegment",
    "PostCheckpointedSegment",
    "PreCheckpointedSegment",
    "ProcessorSegment",
    "RunnerSegment",
    "Segment",
    "Sorter",
    "Source",
    "SplitterSegment",
    "Terminus",
]
