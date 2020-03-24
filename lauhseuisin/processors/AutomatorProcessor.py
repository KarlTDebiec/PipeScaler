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

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile, self.executable, self.workflow,
                          self.pipeline.verbosity)

    @classmethod
    def process_file(cls, infile: str, outfile: str, executable: str,
                     workflow: str, verbosity: int) -> None:
        copyfile(infile, outfile)
        command = f"{executable} " \
                  f"-i {outfile} " \
                  f"{workflow}"
        if verbosity >= 1:
            print(cls.get_indented_text(command))
        Popen(command, shell=True, close_fds=True).wait()
