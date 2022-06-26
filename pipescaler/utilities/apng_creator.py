#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Concatenates images into an animated PNG file."""
from __future__ import annotations

from os import remove
from subprocess import Popen
from tempfile import NamedTemporaryFile
from typing import Any, Optional

from PIL import Image, ImageDraw, ImageFont

from pipescaler.common import (
    validate_executable,
    validate_input_path,
    validate_output_path,
)
from pipescaler.core import Utility


class ApngCreator(Utility):
    """Concatenates images into an animated PNG file."""

    def __init__(
        self,
        infiles: list[str],
        outfile: str,
        labels: Optional[list[str]] = None,
        show_size: bool = False,
        duration: Optional[int] = 500,
        **kwargs: Any,
    ) -> None:
        """Validate configuration and initialize.

        Arguments:
            infiles: Input files
            outfile: Output animated png file
            labels: Image labels
            show_size: Show size
            duration: Duration
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.infiles = list(map(validate_input_path, infiles))
        self.outfile = validate_output_path(outfile)
        self.labels = labels
        if self.labels is not None and len(self.labels) != len(self.infiles):
            raise ValueError
        self.show_size = show_size
        self.duration = duration
        self.apngasm_executable = validate_executable("apngasm")

    def __call__(self) -> None:
        """Concatenate images into an animated PNG file."""
        images = []
        sizes = []
        for infile in self.infiles:
            image = Image.open(infile).convert("RGBA")
            images.append(image)
            sizes.append(image.size)
        final_size = sizes[-1]

        tempfiles = []
        label = ""
        for i, image in enumerate(images):
            if image.size != max(sizes):
                image = image.resize(final_size, resample=Image.NEAREST)
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype("Arial", 32)
            if self.labels is not None:
                label = f"{label} → {self.labels[i]}".strip(" → ")
                draw.text(
                    (15, final_size[1] - 45),
                    label,
                    font=font,
                    stroke="white",
                    stroke_fill="black",
                    stroke_width=2,
                )
                # Annotate with label
            if self.show_size:
                print(sizes[i], final_size, image.mode)
                draw.text(
                    (15, 15),
                    f"{sizes[i][0]} x {sizes[i][1]}",
                    font=font,
                    stroke="white",
                    stroke_fill="black",
                    stroke_width=2,
                )
                # Annotate with size
            tempfiles.append(NamedTemporaryFile(delete=False, suffix=".png"))
            tempfiles[-1].close()
            image.save(tempfiles[-1].name)
        command = (
            f"{self.apngasm_executable} "
            f"-o {self.outfile} "
            f"{' '.join([t.name for t in tempfiles])} "
            f"-d {self.duration} "
            f"--force"
        )
        print(command)
        Popen(command, shell=True, close_fds=True).wait()
        for tempfile in tempfiles:
            remove(tempfile.name)
