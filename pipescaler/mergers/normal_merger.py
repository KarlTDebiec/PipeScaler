#!/usr/bin/env python
#   pipescaler/mergers/normal_merger.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from os.path import isfile
from typing import Any, Generator, List, Optional, Union

import numpy as np
from PIL import Image

from pipescaler.common import get_name, validate_output_path
from pipescaler.core import Merger, PipeImage


####################################### CLASSES ########################################
class NormalMerger(Merger):

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
            r_infile = image.last
            image = yield
            g_infile = image.last
            image = yield
            b_infile = image.last
            stages = get_name(image.last).split("_")
            rstrip = "_" + "_".join(stages[stages.index("B") :])
            outfile = validate_output_path(
                self.pipeline.get_outfile(image, "merge-RGB", rstrip=rstrip)
            )

            if not isfile(outfile):
                if self.pipeline.verbosity >= 2:
                    print(f"    merging: {image.name}")
                r_datum = np.array(Image.open(r_infile).convert("L"), np.float) - 128
                g_datum = np.array(Image.open(g_infile).convert("L"), np.float) - 128
                b_datum = np.array(Image.open(b_infile).convert("L"), np.float) - 128
                b_datum[b_datum < 0] = 0
                mag = np.sqrt(r_datum ** 2 + g_datum ** 2 + b_datum ** 2)
                r_datum = (((r_datum / mag) * 128) + 128).astype(np.uint8)
                g_datum = (((g_datum / mag) * 128) + 128).astype(np.uint8)
                b_datum = (((b_datum / mag) * 128) + 128).astype(np.uint8)
                b_datum[b_datum == 0] = 255
                rgb_datum = np.zeros((r_datum.shape[0], r_datum.shape[1], 3), np.uint8)
                rgb_datum[:, :, 0] = r_datum
                rgb_datum[:, :, 1] = g_datum
                rgb_datum[:, :, 2] = b_datum
                rgb_image = Image.fromarray(rgb_datum)
                rgb_image.save(outfile)
            image.log(self.name, outfile)
            if self.downstream_stages is not None:
                for pipe in self.downstream_stages:
                    self.pipeline.stages[pipe].send(image)

    # endregion
