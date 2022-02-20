#!/usr/bin/env python
#   pipescaler/testing/general.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Pipescaler testing general code"""
from inspect import getfile
from typing import Type

from pipescaler.common import run_command, temporary_filename
from pipescaler.core import Processor


def run_processor_on_command_line(processor: Type[Processor], args: str, infile: str):
    with temporary_filename(".png") as outfile:
        command = f"coverage run {getfile(processor)} {args} {infile} {outfile}"
        run_command(command)
