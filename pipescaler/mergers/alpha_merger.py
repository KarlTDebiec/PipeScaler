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

from pipescaler.common import get_name, validate_output_path
from pipescaler.core import Merger, PipeImage


####################################### CLASSES ########################################
class AlphaMerger(Merger):

    # region Builtins

    def __init__(
        self, downstream_stages: Optional[Union[str, List[str]]] = None, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        # Store configuration
        if isinstance(downstream_stages, str):
            downstream_stages = [downstream_stages]
        self.downstream_stages = downstream_stages

        # Prepare description
        desc = f"{self.name} {self.__class__.__name__}"
        if self.downstream_stages is not None:
            if len(self.downstream_stages) >= 2:
                for stage in self.downstream_stages[:-1]:
                    desc += f"\n ├─ {stage}"
            desc += f"\n └─ {self.downstream_stages[-1]}"
        self.desc = desc

    def __call__(self) -> Generator[PipeImage, PipeImage, None]:
        while True:
            image = yield
            rgb_infile = image.last
            image = yield
            a_infile = image.last
            stages = get_name(image.last).split("_")
            strip = "_".join(stages[stages.index("A") :])
            outfile = validate_output_path(
                self.pipeline.get_outfile(image, "merge-RGBA", strip,)
            )

            if self.pipeline.verbosity >= 2:
                print(f"{self} merging: {image.name}")
            rgb_datum = np.array(Image.open(rgb_infile))
            a_datum = np.array(Image.open(a_infile).convert("L"))
            rgba_datum = np.zeros((rgb_datum.shape[0], rgb_datum.shape[1], 4), np.uint8)
            rgba_datum[:, :, :3] = rgb_datum
            rgba_datum[:, :, 3] = a_datum
            rgba_image = Image.fromarray(rgba_datum)
            rgba_image.save(outfile)

            image.log(self.name, outfile)
            if self.downstream_stages is not None:
                for pipe in self.downstream_stages:
                    self.pipeline.stages[pipe].send(image)

    # endregion
