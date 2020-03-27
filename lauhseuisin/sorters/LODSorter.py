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

    def __init__(self, lods: Union[str, Dict[str, Dict[float, str]]],
                 downstream_pipes: Optional[Union[str, List[str]]] = None,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        if isinstance(lods, str):
            with open(expandvars(lods), "r") as f:
                lods = yaml.load(f, Loader=yaml.SafeLoader)
        self.lods = lods
        if isinstance(downstream_pipes, str):
            downstream_pipes = [downstream_pipes]
        self.downstream_pipes = downstream_pipes

    def __call__(self) -> Iterator[str]:
        while True:
            infile = (yield)
            infile = self.backup_infile(infile)
            if self.pipeline.verbosity >= 2:
                print(f"{self}: {infile}")

            # Pass infile along pipeline
            if self.downstream_pipes is not None:
                for pipe in self.downstream_pipes:
                    self.pipeline.pipes[pipe].send(infile)

            # Split off LODs, scale them, and pass them along pipeline
            if self.get_original_name(infile) in self.lods:
                lods = self.lods[self.get_original_name(infile)]
                for scale, name in lods.items():
                    self.backup_lod(name)
                    desc_so_far = splitext(basename(infile))[0].lstrip(
                        "original")
                    outfile = f"{desc_so_far}_" \
                              f"lod-{scale:4.2f}.png".lstrip("_")
                    outfile = f"{self.pipeline.wip_directory}/{name}/{outfile}"
                    if self.pipeline.verbosity >= 2:
                        print(f"{self}: {outfile}")

                    if not isfile(outfile):
                        input_image = Image.open(infile)
                        output_image = input_image.resize((
                            int(np.round(input_image.size[0] * scale)),
                            int(np.round(input_image.size[1] * scale))),
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
