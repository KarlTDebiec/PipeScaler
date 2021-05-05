#!/usr/bin/env python
#   pipescaler/processors/automator_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
####################################### MODULES ########################################
from __future__ import annotations

from argparse import ArgumentParser
from os.path import isfile, join, split
from shutil import copyfile
from subprocess import Popen
from typing import Any

from pipescaler.common import (
    package_root,
    temporary_filename,
    validate_input_path,
    validate_output_path,
)
from pipescaler.core import PipeImage, Processor


####################################### CLASSES ########################################
class AutomatorProcessor(Processor):

    # region Builtins

    def __init__(self, workflow: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Store configuration
        self.workflow = validate_input_path(
            workflow if workflow.endswith(".workflow") else f"{workflow}.workflow",
            file_ok=False,
            directory_ok=True,
            default_directory=join(*split(package_root), "data", "workflows"),
        )

        # Prepare description
        desc = f"{self.name} {self.__class__.__name__} ({self.workflow})"
        if self.downstream_stages is not None:
            if len(self.downstream_stages) >= 2:
                for stage in self.downstream_stages[:-1]:
                    desc += f"\n ├─ {stage}"
            desc += f"\n └─ {self.downstream_stages[-1]}"
        self.desc = desc

    # endregion

    # region Methods

    def process_file_in_pipeline(self, image: PipeImage) -> None:
        infile = image.last
        outfile = validate_output_path(self.pipeline.get_outfile(image, self.suffix))
        if not isfile(outfile):
            self.process_file(
                infile, outfile, self.pipeline.verbosity, workflow=self.workflow
            )
        image.log(self.name, outfile)

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Args:
            kwargs (Any): Additional keyword arguments

        Returns:
            parser (ArgumentParser): Argument parser
        """
        parser = super().construct_argparser(description=__doc__.strip(), **kwargs)

        # Operations
        parser.add_argument(
            "--workflow",
            type=cls.input_path_arg(
                file_ok=False,
                directory_ok=True,
                default_directory=join(*split(package_root), "data", "workflows"),
            ),
            help="path to workflow",
        )

        return parser

    @classmethod
    def process_file(
        cls, infile: str, outfile: str, verbosity: int = 1, **kwargs: Any
    ) -> None:
        workflow = kwargs.pop("workflow")

        with temporary_filename(".png") as tempfile:
            copyfile(infile, tempfile)
            command = f"automator -i {tempfile} {workflow}"
            if verbosity >= 2:
                print(command)
            Popen(command, shell=True, close_fds=True).wait()
            copyfile(tempfile, outfile)

    @classmethod
    def process_file_from_cl(cls, infile: str, outfile: str, **kwargs: Any) -> None:
        infile = validate_input_path(infile)
        outfile = validate_output_path(outfile)
        workflow = validate_input_path(
            kwargs.pop("workflow"), file_ok=False, directory_ok=True
        )

        cls.process_file(infile, outfile, workflow=workflow, **kwargs)

    # endregion


######################################### MAIN #########################################
if __name__ == "__main__":
    AutomatorProcessor.main()
