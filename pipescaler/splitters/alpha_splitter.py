#!/usr/bin/env python
#   pipescaler/splitter/alpha_splitter.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from os.path import basename, join, splitext
from typing import Any, Generator, Optional

import numpy as np
from PIL import Image

from pipescaler.core import Splitter


####################################### CLASSES ########################################
class AlphaSplitter(Splitter):

    # region Builtins

    def __init__(
        self,
        downstream_pipe_for_rgb: Optional[str] = None,
        downstream_pipe_for_a: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        self.downstream_pipe_for_rgb = downstream_pipe_for_rgb
        self.downstream_pipe_for_a = downstream_pipe_for_a

    def __call__(self) -> Generator[str, str, None]:
        while True:
            infile: str = (yield)  # type: ignore
            infile = self.backup_infile(infile)
            image = Image.open(infile)
            if image.mode == "RGBA":
                if self.downstream_pipe_for_rgb is not None:
                    rgb_outfile = self.get_outfile(infile, "RGB")
                    Image.fromarray(np.array(image)[:, :, :3]).save(rgb_outfile)
                    self.pipeline.pipes[self.downstream_pipe_for_rgb].send(rgb_outfile)
                if self.downstream_pipe_for_a is not None:
                    a_outfile = self.get_outfile(infile, "A")
                    Image.fromarray(np.array(image)[:, :, 3]).save(a_outfile)
                    self.pipeline.pipes[self.downstream_pipe_for_a].send(a_outfile)

    # endregion

    # region Properties

    @property
    def desc(self) -> str:
        """str: Description"""
        if not hasattr(self, "_desc"):
            return "alphasplitter"
        return self._desc

    # endregion

    # region Methods

    def get_outfile(self, infile: str, nay: str) -> str:
        original_name = self.get_original_name(infile)
        extension = self.get_extension(infile)
        if extension == "tga":
            extension = "png"
        desc_so_far = splitext(basename(infile))[0].replace(original_name, "")
        outfile = f"{desc_so_far}_{nay}.{extension}".lstrip("_")

        return join(self.pipeline.wip_directory, original_name, outfile)

    # endregion
