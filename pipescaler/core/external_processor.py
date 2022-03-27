#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Base class for processors that perform their processing using an external tool"""
from __future__ import annotations

from abc import ABC, abstractmethod
from logging import debug, info
from os.path import splitext
from shutil import copyfile

from pipescaler.common import run_command, temporary_filename
from pipescaler.common.validation import validate_executable
from pipescaler.core.processor import Processor


class ExternalProcessor(Processor, ABC):
    """Base class for processors that perform their processing using an external tool"""

    def __call__(self, infile: str, outfile: str) -> None:
        """
        Read image from infile, process it, and save to outfile

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        validate_executable(self.executable, self.supported_platforms)

        with temporary_filename(splitext(infile)[-1]) as temp_infile:
            copyfile(infile, temp_infile)
            with temporary_filename(splitext(outfile)[-1]) as temp_outfile:
                self.process(temp_infile, temp_outfile)
                copyfile(temp_outfile, outfile)
                info(f"{self}: '{outfile}' saved")

    @property
    @abstractmethod
    def command_template(self) -> str:
        """String template with which to generate command"""
        raise NotImplementedError()

    def process(self, infile: str, outfile: str) -> None:
        """
        Read image from infile, process it, and save to outfile

        Arguments:
            infile: Input file path
            outfile: Output file path
        """
        command = self.command_template.format(infile=infile, outfile=outfile)
        debug(f"{self}: {command}")
        run_command(command, timeout=600)

        # If command template lacks outfile, assume infile is processed in place
        if "{outfile}" not in self.command_template:
            copyfile(infile, outfile)

    @classmethod
    @property
    def executable(self) -> str:
        """Name of executable"""
        raise NotImplementedError()

    @classmethod
    @property
    def supported_platforms(self) -> set[str]:
        """Platforms on which processor is supported"""
        return {"Darwin", "Linux", "Windows"}
