#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from typing import Sequence

from pipescaler.core.pipelines.checkpoint_manager_base import CheckpointManagerBase
from pipescaler.core.pipelines.pipe_stage import PipeStage


class PipeWithCheckpoints(PipeStage):
    def __init__(
        self,
        pipe_stage: PipeStage,
        cp_manager: CheckpointManagerBase,
        cpts: Sequence[str],
        internal_cpts: Sequence[str],
    ) -> None:
        self.pipe_stage = pipe_stage
        self.cp_manager = cp_manager
        self.cpts = cptsd
        self.internal_cpts = internal_cpts
