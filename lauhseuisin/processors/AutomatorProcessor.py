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

from os.path import basename, isfile, isdir
from shutil import copyfile
from subprocess import Popen
from typing import Any

from lauhseuisin import package_root
from lauhseuisin.processors.Processor import Processor


################################### CLASSES ###################################
class AutomatorProcessor(Processor):

    def __init__(self, workflow: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.workflow = f"{package_root}/data/workflows/{workflow}"
        if not self.workflow.endswith(".workflow"):
            self.workflow = f"{self.workflow}.workflow"
        self.desc = f"{basename(self.workflow).rstrip('.workflow')}"

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile, self.workflow,
                          self.pipeline.verbosity)

    @classmethod
    def process_file(cls, infile: str, outfile: str, workflow: str,
                     verbosity: int) -> None:
        if not isdir(workflow):
            raise ValueError(workflow)

        copyfile(infile, outfile)
        command = f"automator " \
                  f"-i {outfile} " \
                  f"{workflow}"
        if verbosity >= 1:
            print(cls.get_indented_text(command))
        Popen(command, shell=True, close_fds=True).wait()
