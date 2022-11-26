#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.

from pipescaler.core.image import Operator
from pipescaler.core.pipelines.pipe_stage import PipeStage


class PipeOperator(PipeStage):
    operator: Operator

    def __init__(self, operator: Operator) -> None:
        self.operator = operator
