#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base classes for and functions related to pipelines."""
from __future__ import annotations

from pipescaler.core.pipelines.checkpoint_manager_base import CheckpointManagerBase
from pipescaler.core.pipelines.pipe_image import PipeImage
from pipescaler.core.pipelines.pipe_merger import PipeMerger
from pipescaler.core.pipelines.pipe_operator_with_checkpoints import (
    PipeOperatorWithCheckpoints,
)
from pipescaler.core.pipelines.pipe_pre_checkpoint import PipePreCheckpoint
from pipescaler.core.pipelines.pipe_processor import PipeProcessor
from pipescaler.core.pipelines.pipe_processor_with_checkpoints import (
    PipeProcessorWithCheckpoints,
)
from pipescaler.core.pipelines.pipe_processor_with_post_checkpoint import (
    PipeProcessorWithPostCheckpoint,
)
from pipescaler.core.pipelines.pipe_splitter import PipeSplitter
from pipescaler.core.pipelines.pipe_splitter_with_checkpoints import (
    PipeSplitterWithCheckpoints,
)
from pipescaler.core.pipelines.pipe_splitter_with_post_checkpoint import (
    PipeSplitterWithPostCheckpoints,
)
from pipescaler.core.pipelines.source import Source
from pipescaler.core.pipelines.terminus import Terminus

__all__: list[str] = [
    "CheckpointManagerBase",
    "PipeImage",
    "PipeMerger",
    "PipeOperatorWithCheckpoints",
    "PipeProcessor",
    "PipeProcessorWithCheckpoints",
    "PipeProcessorWithPostCheckpoint",
    "PipePreCheckpoint",
    "PipeSplitterWithCheckpoints",
    "PipeSplitterWithPostCheckpoints",
    "PipeSplitter",
    "Source",
    "Terminus",
]
