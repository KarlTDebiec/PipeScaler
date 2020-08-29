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

from os.path import basename, isfile, join, splitext
from typing import Any, Generator, List, Optional, Union

import numpy as np
from PIL import Image

from pipescaler.core import Merger


####################################### CLASSES ########################################
class AlphaMerger(Merger):

    # region Builtins

    def __init__(
        self, downstream_pipes: Optional[Union[str, List[str]]] = None, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        if isinstance(downstream_pipes, str):
            downstream_pipes = [downstream_pipes]
        self.downstream_pipes = downstream_pipes

    def __call__(self) -> Generator[str, str, None]:
        while True:
            rgb_infile: str = (yield)  # type: ignore
            a_infile: str = (yield)  # type: ignore
            outfile = self.get_outfile(rgb_infile, a_infile)
            if outfile is None:
                continue
            if not isfile(outfile):
                self.merge_files(rgb_infile, a_infile, outfile)
            self.log_outfile(outfile)
            if self.downstream_pipes is not None:
                for pipe in self.downstream_pipes:
                    self.pipeline.pipes[pipe].send(outfile)

    # endregion

    # region Properties

    @property
    def desc(self) -> str:
        """str: Description"""
        if not hasattr(self, "_desc"):
            return "alphamerger"
        return self._desc

    # endregion

    # region Methods

    def get_outfile(self, rgb_infile: str, a_infile: str) -> str:
        original_name = self.get_original_name(rgb_infile)
        extension = self.get_extension(rgb_infile)
        if extension == "tga":
            extension = "png"
        desc_so_far = splitext(basename(rgb_infile))[0].replace(original_name, "")
        desc_so_far.rstrip("_RGB").rstrip("_A")
        outfile = f"{desc_so_far}_RGBA-merge.{extension}".lstrip("_")

        return join(self.pipeline.wip_directory, original_name, outfile)

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
