#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Abstract base classes for and functions related to pipelines."""
from __future__ import annotations

from pipescaler.core.pipelines.checkpoint_manager_base import CheckpointManagerBase
from pipescaler.core.pipelines.pipe_image import PipeImage
from pipescaler.core.pipelines.pipe_merger import PipeMerger
from pipescaler.core.pipelines.pipe_processor import PipeProcessor
from pipescaler.core.pipelines.pipe_splitter import PipeSplitter
from pipescaler.core.pipelines.pipe_with_checkpoints import PipeWithCheckpoints
from pipescaler.core.pipelines.pipe_with_post_checkpoints import PipeWithPostCheckpoints
from pipescaler.core.pipelines.pipe_with_pre_checkpoints import PipeWithPreCheckpoints
from pipescaler.core.pipelines.source import Source
from pipescaler.core.pipelines.terminus import Terminus

__all__: list[str] = [
    "CheckpointManagerBase",
    "PipeImage",
    "PipeMerger",
    "PipeWithCheckpoints",
    "PipeWithPostCheckpoints",
    "PipeWithPreCheckpoints",
    "PipeProcessor",
    "PipeSplitter",
    "Source",
    "Terminus",
]
