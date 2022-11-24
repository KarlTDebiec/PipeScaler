#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from pipescaler.core.pipelines import CheckpointManagerBase
from pipescaler.core.pipelines.pipe_operator import PipeOperator


class PipeOperatorWithCheckpoints(PipeOperator):
    def __init__(
        self,
        operator: PipeOperator,
        cp_manager: CheckpointManagerBase,
        cpt: str,
        internal_cpts: list[str],
    ) -> None:
        self.operator = operator
        self.cp_manager = cp_manager
        self.cpt = cpt
        self.internal_cpts = internal_cpts
