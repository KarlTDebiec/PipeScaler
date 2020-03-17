#!python
#   lauhseuisin/processors/AutomatorProcessor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from os.path import basename, expandvars
from shutil import copyfile
from subprocess import Popen
from typing import Any

from lauhseuisin.processors.Processor import Processor


################################### CLASSES ###################################
class AutomatorProcessor(Processor):

    def __init__(self, workflow: str, executable: str = "automator",
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.workflow = expandvars(workflow)
        self.executable = expandvars(executable)
        self.desc = f"{basename(self.workflow).rstrip('.workflow')}"

    def process_file(self, infile: str, outfile: str) -> None:
        copyfile(infile, outfile)
        command = f"{self.executable} " \
                  f"-i {outfile} " \
                  f"{self.workflow}"
        if self.pipeline.verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()
