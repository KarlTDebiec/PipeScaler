#!/usr/bin/env python
#   pipescaler/mergers/alpha_merger.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from typing import Any, Generator, List, Optional, Union

import numpy as np
from PIL import Image

from pipescaler.core import Merger, PipeImage


####################################### CLASSES ########################################
class AlphaMerger(Merger):

    # region Builtins

    def __init__(
        self, downstream_stages: Optional[Union[str, List[str]]] = None, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        if isinstance(downstream_stages, str):
            downstream_stages = [downstream_stages]
        self.downstream_stages = downstream_stages

    def __call__(self) -> Generator[PipeImage, PipeImage, None]:
        while True:
            image = yield
            image = yield

            # self.merge_files(image, image, outfile)
            # self.log_outfile(outfile)
            # if self.downstream_stages is not None:
            #     for pipe in self.downstream_stages:
            #         self.pipeline.pipes[pipe].send(image)

    # endregion

    # region Class Methods

    @classmethod
    def merge_files(cls, rgb_infile: str, a_infile: str, outfile: str):
        rgb_datum = np.array(Image.open(rgb_infile))
        a_datum = np.array(Image.open(a_infile).convert("L"))
        rgba_datum = np.zeros((rgb_datum.shape[0], rgb_datum.shape[1], 4), np.uint8)
        rgba_datum[:, :, :3] = rgb_datum
        rgba_datum[:, :, 3] = a_datum
        rgba_image = Image.fromarray(rgba_datum)

        rgba_image.save(outfile)

    # endregion
