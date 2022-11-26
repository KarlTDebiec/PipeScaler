#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from abc import abstractmethod
from typing import Collection, Union

from pipescaler.core.pipelines.pipe_image import PipeImage


class PipeStage:
    @abstractmethod
    def __call__(
        self, *input_pimgs: PipeImage
    ) -> Union[PipeImage, Collection[PipeImage]]:
        raise NotImplementedError()
