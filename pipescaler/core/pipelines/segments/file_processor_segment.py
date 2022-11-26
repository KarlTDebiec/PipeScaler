#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
from logging import warning
from pathlib import Path
from typing import Callable

from pipescaler.common import get_temp_file_path
from pipescaler.core.pipelines import PipeImage
from pipescaler.core.pipelines.segment import Segment


class FileProcessorSegment(Segment):
    def __init__(
        self,
        file_processor: Callable[[Path, Path], None],
        input_extension: str = ".png",
        output_extension: str = ".png",
    ) -> None:
        self.file_processor = file_processor
        self.input_extension = input_extension
        self.output_extension = output_extension

    def __call__(self, *input_pimgs: PipeImage) -> PipeImage:
        input_pimg = input_pimgs[0]

        with get_temp_file_path(self.output_extension) as output_path:
            if input_pimg.path is None:
                with get_temp_file_path(self.input_extension) as input_path:
                    input_pimg.image.save(input_path)
                    self.file_processor(input_path, output_path)
            else:
                self.file_processor(input_pimg.path, output_path)
            output_pimg = PipeImage(path=output_path, parents=input_pimg)
        if self.output_extension != ".png":
            warning(
                f"{self}: Output file is temporary and only image is retained; if "
                f"output file is needed (e.g. if the purpose of this processor is to "
                f"convert to a format such as DDS), use a "
                f"CheckpointedFileProcessorSegment."
            )
        output_pimg.path = None

        return output_pimg
