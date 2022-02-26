#!/usr/bin/env python
#   pipescaler/core/image_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Base class for processors"""
from __future__ import annotations

from abc import ABC, abstractmethod
from logging import debug, info
from os.path import splitext
from shutil import copyfile
from typing import Set

from pipescaler.common import run_command, temporary_filename
from pipescaler.common.validation import validate_executable
from pipescaler.core.processor import Processor


class ExternalProcessor(Processor, ABC):
    """Base class for processors"""

    def __call__(self, infile: str, outfile: str) -> None:
        validate_executable(self.executable, self.supported_platforms)

        with temporary_filename(splitext(infile)[-1]) as temp_infile:
            copyfile(infile, temp_infile)
            with temporary_filename(splitext(outfile)[-1]) as temp_outfile:
                self.process(temp_infile, temp_outfile)
                copyfile(temp_outfile, outfile)
                info(f"{self}: '{outfile}' saved")

    @property
    @abstractmethod
    def command_template(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def executable(self) -> str:
        raise NotImplementedError()

    @property
    def supported_platforms(self) -> Set[str]:
        return {"Darwin", "Linux", "Windows"}

    def process(self, temp_infile: str, temp_outfile: str):
        """
        Read image from infile, process it, and save to outfile
        """
        command = self.command_template.format(infile=temp_infile, outfile=temp_outfile)
        debug(f"{self}: {command}")
        run_command(command)
