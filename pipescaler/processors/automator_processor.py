#!/usr/bin/env python
#   pipescaler/processors/automator_processor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from os.path import basename, join, split
from shutil import copyfile
from subprocess import Popen
from typing import Any

from pipescaler.common import package_root, validate_input_path, validate_output_path
from pipescaler.core import Processor


####################################### CLASSES ########################################
class AutomatorProcessor(Processor):

    # region Builtins

    def __init__(self, workflow: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.workflow = workflow

    # endregion

    # region Properties

    @property
    def desc(self) -> str:
        """str: Description"""
        if not hasattr(self, "_desc"):
            return f"{basename(self.workflow).rstrip('.workflow')}"
        return self._desc

    @property
    def workflow(self) -> str:
        """str: Path to workflow"""
        if not hasattr(self, "_workflow"):
            raise ValueError()
        return self._workflow

    @workflow.setter
    def workflow(self, value: str) -> None:
        if not value.endswith(".workflow"):
            value = f"{value}.workflow"
        self._workflow = validate_input_path(
            value,
            file_ok=False,
            directory_ok=True,
            default_directory=join(*split(package_root), "data", "workflows"),
        )

    # endregion

    # region Methods

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        infile = validate_input_path(infile)
        outfile = validate_output_path(outfile)
        self.process_file(
            infile, outfile, self.pipeline.verbosity, workflow=self.workflow
        )

    # endregion

    # region Class Methods

    @classmethod
    def process_file(
        cls, infile: str, outfile: str, verbosity: int = 1, **kwargs: Any
    ) -> None:
        workflow = kwargs.get("workflow")
        copyfile(infile, outfile)
        command = f"automator " f"-i {outfile} " f"{workflow}"
        if verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()

    @classmethod
    def process_file_from_cl(cls, infile: str, outfile: str, **kwargs: Any) -> None:
        infile = validate_input_path(infile)
        outfile = validate_output_path(outfile)
        workflow = kwargs.get("workflow")
        if not workflow.endswith(".workflow"):
            workflow = f"{workflow}.workflow"
        workflow = validate_input_path(
            workflow,
            file_ok=False,
            directory_ok=True,
            default_directory=join(*split(package_root), "data", "workflows"),
        )
        cls.process_file(infile, outfile, workflow=workflow, **kwargs)

    # endregion
