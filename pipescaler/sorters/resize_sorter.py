#!/usr/bin/env python
#   pipescaler/sorters/resize_sorter.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from os import makedirs
from os.path import basename, expandvars, isdir, isfile, splitext
from shutil import copyfile
from typing import Any, Dict, Generator, List, Optional, Union

import numpy as np
import yaml
from PIL import Image

from pipescaler.core import Sorter


####################################### CLASSES ########################################
class ResizeSorter(Sorter):

    # region Builtins

    def __init__(
        self,
        scalesets: Union[str, Dict[str, Dict[float, str]]],
        mode: str = "fork",
        downstream_pipes: Optional[Union[str, List[str]]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        if isinstance(scalesets, str):
            with open(expandvars(scalesets), "r") as f:
                scalesets = yaml.load(f, Loader=yaml.SafeLoader)
        if scalesets is None:
            scalesets = {}
        self.scalesets = scalesets

        self.scales: List[str] = []
        for scaleset in self.scalesets.values():
            if scaleset is not None:
                for scales in scaleset.values():
                    if isinstance(scales, str):
                        scales = [scales]
                    self.scales.extend(scales)
        self.scales = set(self.scales)

        if mode not in ["filter", "fork"]:
            raise ValueError()
        self.mode = mode

        if isinstance(downstream_pipes, str):
            downstream_pipes = [downstream_pipes]
        self.downstream_pipes = downstream_pipes

    def __call__(self) -> Generator[str, str, None]:
        while True:
            infile = yield  # type:ignore
            infile = self.backup_infile(infile)
            if self.pipeline.verbosity >= 2:
                print(f"{self}: {infile}")

            # If infile is a mipmap, skip
            if self.mode == "filter":
                if self.get_original_name(infile) in self.scales:
                    continue

            # Pass infile along pipeline
            if self.downstream_pipes is not None:
                for pipe in self.downstream_pipes:
                    self.pipeline.pipes[pipe].send(infile)

            # Split off mipmaps, scale them, and pass them along pipeline
            if self.mode == "fork":
                if self.get_original_name(infile) in self.scalesets:
                    scaleset = self.scalesets[self.get_original_name(infile)]
                    for scale, names in scaleset.items():
                        if isinstance(names, str):
                            names = [names]
                        for name in names:
                            self.backup_mipmap(name)
                            desc_so_far = splitext(basename(infile))[0].lstrip(
                                "original"
                            )
                            outfile = f"{desc_so_far}_" f"scale-{scale}.png".lstrip("_")
                            outfile = (
                                f"{self.pipeline.wip_directory}/" f"{name}/{outfile}"
                            )
                            if self.pipeline.verbosity >= 2:
                                print(f"{self}: {outfile}")

                            if not isfile(outfile):
                                # Load and scale image
                                input_image = Image.open(infile)
                                size = (
                                    int(np.round(input_image.size[0] * scale)),
                                    int(np.round(input_image.size[1] * scale)),
                                )
                                output_image = input_image.convert("RGB").resize(
                                    size, resample=Image.LANCZOS
                                )

                                # Combine R, G, and B from RGB with A from RGBA
                                if input_image.mode == "RGBA":
                                    rgba_image = input_image.resize(
                                        size, resample=Image.LANCZOS
                                    )
                                    merged_data = np.zeros(
                                        (size[1], size[0], 4), np.uint8
                                    )
                                    merged_data[:, :, :3] = np.array(output_image)
                                    merged_data[:, :, 3] = np.array(rgba_image)[:, :, 3]
                                    output_image = Image.fromarray(merged_data)

                                # Save image
                                output_image.save(outfile)

                            self.log_outfile(outfile)
                            if self.downstream_pipes is not None:
                                for pipe in self.downstream_pipes:
                                    self.pipeline.pipes[pipe].send(outfile)

    # endregion

    # region Methods

    def backup_mipmap(self, name: str) -> None:
        if not isdir(f"{self.pipeline.wip_directory}/{name}"):
            makedirs(f"{self.pipeline.wip_directory}/{name}")
        original = f"{self.pipeline.source.input_directory}/{name}.png"
        backup = f"{self.pipeline.wip_directory}/{name}/{name}.png"
        if not isfile(original):
            original = f"{self.pipeline.source.input_directory}/{name}.tga"
            backup = f"{self.pipeline.wip_directory}/{name}/{name}.tga"
        if not isfile(backup):
            copyfile(original, backup)

    # endregion
