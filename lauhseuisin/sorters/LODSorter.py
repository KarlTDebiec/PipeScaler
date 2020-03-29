#!python
#   lauhseuisin/sorters/ListSorter.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from os import makedirs
from os.path import basename, isdir, isfile, splitext, expandvars
from shutil import copyfile
from typing import Any, Dict, Iterator, List, Optional, Union

import numpy as np
import yaml
from IPython import embed
from PIL import Image

from lauhseuisin.sorters.Sorter import Sorter


################################### CLASSES ###################################
class LODSorter(Sorter):

    def __init__(self, lodsets: Union[str, Dict[str, Dict[float, str]]],
                 mode: str = "fork",
                 downstream_pipes: Optional[Union[str, List[str]]] = None,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        if isinstance(lodsets, str):
            with open(expandvars(lodsets), "r") as f:
                lodsets = yaml.load(f, Loader=yaml.SafeLoader)
        self.lodsets = lodsets

        self.lods: List[str] = []
        for lodset in self.lodsets.values():
            if lodset is not None:
                for lods in lodset.values():
                    if isinstance(lods, str):
                        lods = [lods]
                    self.lods.extend(lods)
        self.lods = set(self.lods)

        if mode not in ["filter", "fork"]:
            raise ValueError()
        self.mode = mode

        if isinstance(downstream_pipes, str):
            downstream_pipes = [downstream_pipes]
        self.downstream_pipes = downstream_pipes

    def __call__(self) -> Iterator[str]:
        while True:
            infile = (yield)
            infile = self.backup_infile(infile)
            if self.pipeline.verbosity >= 2:
                print(f"{self}: {infile}")

            # If infile is a lod, skip
            if self.mode == "filter":
                if self.get_original_name(infile) in self.lods:
                    continue

            # Pass infile along pipeline
            if self.downstream_pipes is not None:
                for pipe in self.downstream_pipes:
                    self.pipeline.pipes[pipe].send(infile)

            # Split off LODs, scale them, and pass them along pipeline
            if self.mode == "fork":
                if self.get_original_name(infile) in self.lodsets:
                    lodset = self.lodsets[self.get_original_name(infile)]
                    for scale, names in lodset.items():
                        if isinstance(names, str):
                            names = [names]
                        for name in names:
                            self.backup_lod(name)
                            desc_so_far = splitext(basename(infile))[0].lstrip(
                                "original")
                            outfile = f"{desc_so_far}_" \
                                      f"lod-{scale:4.2f}.png".lstrip("_")
                            outfile = f"{self.pipeline.wip_directory}/" \
                                      f"{name}/{outfile}"
                            if self.pipeline.verbosity >= 2:
                                print(f"{self}: {outfile}")

                            if not isfile(outfile):
                                input_image = Image.open(infile)
                                output_image = input_image.resize((
                                    int(np.round(
                                        input_image.size[0] * scale)),
                                    int(np.round(
                                        input_image.size[1] * scale))),
                                    resample=Image.LANCZOS)
                                output_image.save(outfile)
                            self.log_outfile(outfile)
                            if self.downstream_pipes is not None:
                                for pipe in self.downstream_pipes:
                                    self.pipeline.pipes[pipe].send(outfile)

    def backup_lod(self, name: str) -> None:
        if not isdir(f"{self.pipeline.wip_directory}/{name}"):
            makedirs(f"{self.pipeline.wip_directory}/{name}")
        backup = f"{self.pipeline.wip_directory}/{name}/original.png"
        if not isfile(backup):
            original = f"{self.pipeline.source.input_directory}/{name}.png"
            copyfile(original, backup)
