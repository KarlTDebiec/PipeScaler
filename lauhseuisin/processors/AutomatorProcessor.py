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

from os.path import expandvars, isfile
from pathlib import Path
from shutil import copyfile
from subprocess import Popen
from typing import Any, List, Union

from IPython import embed

from lauhseuisin.processors import Processor


################################### CLASSES ###################################
class AutomatorProcessor(Processor):
    executable_name = "automator"

    def __init__(self, workflow: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.workflow = workflow

    def process_file(self, infile: str, outfile: str) -> None:
        if isfile(outfile):
            return
        print(f"Processing to '{outfile}'")
        copyfile(infile, outfile)
        command = f"{self.executable} " \
                  f"-i {outfile} " \
                  f"{self.workflow}"
        print(command)
        Popen(command, shell=True, close_fds=True).wait()

    @classmethod
    def get_pipes(cls, **kwargs: Any) -> List[Processor]:
        if "workflow_directory" in kwargs:
            workflow_directory = expandvars(
                str(kwargs.pop("workflow_directory")))
        else:
            workflow_directory = f"{Path(__file__).parent.absolute()}/" \
                                 f"../data/workflows"
        workflows: Union[List[str], str] = kwargs.pop("workflow")
        if not isinstance(workflows, list):
            workflows = [workflows]
        processors: List[Processor] = []
        for workflow in workflows:
            processors.append(cls(
                workflow=f"{workflow_directory}/{workflow}.workflow",
                paramstring=f"pixelmator-"
                            f"{workflow}",
                **kwargs))
        return processors
