#!/usr/bin/env python
#   pipescaler/scripts/apng_creator.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from __future__ import annotations

from argparse import ArgumentParser
from os import remove
from subprocess import Popen
from tempfile import NamedTemporaryFile
from typing import Any, List, Optional

from PIL import Image, ImageDraw, ImageFont

from pipescaler.common import (
    CLTool,
    validate_executable,
    validate_input_path,
    validate_output_path,
)


class APNGCreator(CLTool):
    def __init__(
        self,
        infiles: List[str],
        outfile: str,
        labels: Optional[List[str]] = None,
        show_size: bool = False,
        duration: Optional[int] = 500,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        self.infiles = list(map(validate_input_path, infiles))
        self.outfile = validate_output_path(outfile)
        self.labels = labels
        if self.labels is not None and len(self.labels) != len(self.infiles):
            raise ValueError
        self.show_size = show_size
        self.duration = duration
        self.apngasm_executable = validate_executable("apngasm")

    def __call__(self, **kwargs: Any) -> None:
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
                # width, height = draw.textsize(label, font=font)
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
        if self.verbosity >= 1:
            print(command)
        Popen(command, shell=True, close_fds=True).wait()
        for tempfile in tempfiles:
            remove(tempfile.name)

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Args:
            kwargs (Any): Additional keyword arguments

        Returns:
            ArgumentParser: Argument parser
        """
        parser = super().construct_argparser(description=__doc__.strip(), **kwargs)

        # Input
        parser.add_argument(
            "-i",
            "--infiles",
            nargs="+",
            required=True,
            type=cls.input_path_arg(),
            help="input image files",
        )
        # Labels

        # Operations
        parser.add_argument(
            "--labels",
            nargs="+",
            type=str,
            help="labels with which to annotate images",
        )
        parser.add_argument(
            "--show_size", action="store_true", help="annotate each image with size",
        )
        parser.add_argument(
            "--duration",
            default=500,
            type=cls.int_arg(min_value=1),
            help="duration for which to show each image (ms)",
        )

        # Output
        parser.add_argument(
            "-o",
            "--outfile",
            default="out.png",
            required=True,
            type=cls.output_path_arg(),
            help="output animated png",
        )

        return parser


if __name__ == "__main__":
    APNGCreator.main()
