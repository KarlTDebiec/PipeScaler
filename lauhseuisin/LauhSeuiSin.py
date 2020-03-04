#!python
# -*- coding: utf-8 -*-
#   LauhSeuiSin.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from collections import OrderedDict
from os import R_OK, W_OK, access, getcwd, listdir, makedirs
from os.path import (basename, expandvars, isdir, isfile, join,
                     splitext)
from pathlib import Path
from shutil import copyfile
from sys import modules
from typing import Any, List, Optional

import yaml
from IPython import embed
from lauhseuisin.processors import *
from lauhseuisin.filters import *


################################### CLASSES ###################################
class LauhSeuiSin:
    # region Class Variables

    package_root: str = str(Path(__file__).parent.absolute())

    # endregion

    # region Builtins

    def __init__(self, conf_file: str = "conf2.yaml") -> None:
        """
        Initializes

        Args:
            conf_file (str): file from which to load configuration
        """
        # Read configuration file
        conf_file = expandvars(conf_file)
        if not (isfile(conf_file) and access(conf_file, R_OK)):
            raise ValueError(f"Configuration file '{conf_file}' could not be "
                             f"read")
        with open(conf_file, "r") as f:
            conf = yaml.load(f, Loader=yaml.SafeLoader)

        # General configuration
        self.verbosity = conf.get("verbosity", 1)

        # Input configuration
        self.input_directory = conf.get("input_directory", getcwd())

        # Work in process configuration
        self.wip_directory = conf.get("wip_directory", getcwd())

        # Preprocessor configuration
        self.pipeline: OrderedDict[str, List[Processor]] = OrderedDict()
        for stage in conf["pipeline"]:
            stage_name = list(stage.keys())[0]
            pipes: List[Processor] = []
            for pipe in list(stage.values())[0]:
                if isinstance(pipe, dict):
                    pipe_name = list(pipe.keys())[0]
                    pipe_args = list(pipe.values())[0]
                else:
                    pipe_name = pipe
                    pipe_args = {}
                pipe_args["wip_directory"] = self.wip_directory
                pipe_cls = getattr(modules[__name__], pipe_name)
                print(pipe_cls, pipe_args)
                pipes.extend(pipe_cls.get_pipes(**pipe_args))
            self.pipeline[stage_name] = pipes

    def __call__(self) -> None:
        """
        Performs operations
        """
        downstream_processors = None
        for stage in reversed(self.pipeline.keys()):
            print(stage)
            processors = []
            for processor_object in self.pipeline[stage]:
                processor_generator = processor_object(downstream_processors)
                next(processor_generator)
                processors.append(processor_generator)
            downstream_processors = processors

        self.scan_input_directory(downstream_processors)

    # endregion

    # region Properties

    @property
    def input_directory(self) -> Optional[str]:
        """Optional[str]: Directory from which to load lo-res image files"""
        if not hasattr(self, "_input_directory"):
            self._input_directory: Optional[str] = None
        return self._input_directory

    @input_directory.setter
    def input_directory(self, value: Optional[str]) -> None:
        if value is not None:
            value = expandvars(value)
            if not (isdir(value) and access(value, W_OK)):
                raise ValueError()
        self._input_directory = value

    @property
    def wip_directory(self) -> Optional[str]:
        """Optional[str]: Directory to which to save hi-res image files"""
        if not hasattr(self, "_wip_directory"):
            self._wip_directory: Optional[str] = None
        return self._wip_directory

    @wip_directory.setter
    def wip_directory(self, value: Optional[str]) -> None:
        if value is not None:
            value = expandvars(value)
            # TODO: Create if possible
            if not (isdir(value) and access(value, W_OK)):
                raise ValueError()
        self._wip_directory = value

    @property
    def verbosity(self) -> int:
        """int: Level of output to provide"""
        if not hasattr(self, "_verbosity"):
            self._verbosity = 1
        return self._verbosity

    @verbosity.setter
    def verbosity(self, value: int) -> None:
        if not isinstance(value, int) and value >= 0:
            raise ValueError()
        self._verbosity = value

    # endregion

    # region Methods

    def scan_input_directory(self, downstream_pipes: Any) -> None:
        print(f"Scanning infiles in '{self.input_directory}'")
        for infile in listdir(self.input_directory):
            if infile == ".DS_Store":
                continue
            infile = join(str(self.input_directory), infile)
            for processor in downstream_pipes:
                processor.send(infile)
            # break

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    LauhSeuiSin()()
