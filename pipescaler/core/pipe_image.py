#!/usr/bin/env python
#   pipescaler/core/pipe_image.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from os.path import basename, splitext
from typing import List, Optional, Tuple

from PIL import Image

from pipescaler.common import validate_input_path


class PipeImage:
    def __init__(self, infile: str) -> None:
        self.orig_full_path = validate_input_path(infile)
        self.orig_filename = basename(self.orig_full_path)
        self.name = splitext(basename(self.orig_filename))[0]
        self.current_full_path = self.orig_full_path
        self.current_filename = basename(self.current_full_path)
        self.current_prefix = None

        with Image.open(self.orig_full_path) as image:
            self.mode: str = image.mode
            self.shape: Tuple[int] = image.size

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def get_outfile(
        self,
        infile: str,
        suffix: str,
        trim_suffixes: Optional[List[str]] = None,
        extension="png",
    ) -> PipeImage:
        prefix = splitext(basename(infile))[0]
        if prefix.startswith(self.name):
            prefix = prefix[len(self.name) :]

        if trim_suffixes is not None:
            for trim_suffix in trim_suffixes:
                if trim_suffix in prefix:
                    prefix = prefix[: prefix.rindex(trim_suffix)]
                    break
            prefix = prefix.rstrip("_")

        outfile = f"{prefix}_{suffix}.{extension}"
        outfile = outfile.lstrip("_")

        return outfile
