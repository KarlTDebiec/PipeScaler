#!/usr/bin/env python
#   pipescaler/models/waifu_pytorch_pickler.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Converts Waifu models in JSON format to PyTorch's serialized pth format"""
from __future__ import annotations

import json
from argparse import ArgumentParser
from inspect import cleandoc
from logging import info
from typing import Any

import torch

from pipescaler.common import (
    CommandLineTool,
    validate_input_file,
    validate_output_file,
    validate_str,
)
from pipescaler.models import WaifuUpConv7, WaifuVgg7


class WaifuPyTorchPickler(CommandLineTool):
    """
    Converts Waifu models in JSON format to PyTorch's serialized pth format

    Inputs JSON is available from
    [yu45020/Waifu2x on GitHub](https://github.com/yu45020/Waifu2x/tree/master/model_check_points)
    """

    architectures = {
        "upconv7": WaifuUpConv7,
        "vgg7": WaifuVgg7,
    }

    def __init__(
        self, architecture: str, infile: str, outfile: str, **kwargs: Any
    ) -> None:
        """
        Validate and store static configuration

        Arguments:
            architecture: Model architecture
            infile: Input file
            outfile: Output file
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        self.architecture = validate_str(architecture, self.architectures.keys())
        self.infile = validate_input_file(infile)
        self.outfile = validate_output_file(outfile)

    def __call__(self) -> None:
        """Converts infile to outfile"""
        model = self.architectures[self.architecture]()
        info(f"{self}: Waifu {self.architecture} model built")

        with open(self.infile, "r", encoding="utf-8") as infile:
            weights = json.load(infile)
        box = []
        for weight in weights:
            box.append(weight["weight"])
            box.append(weight["bias"])
        state_dict = model.state_dict()
        for index, (name, parameter) in enumerate(state_dict.items()):
            state_dict[name].copy_(torch.FloatTensor(box[index]))
        info(f"{self}: Model parameters loaded from '{self.infile}'")

        torch.save(model, self.outfile)
        info(f"{self}: Complete serialized model saved to '{self.outfile}'")

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Construct argument parser

        Arguments:
            **kwargs: Additional keyword arguments

        Returns:
            parser: Argument parser
        """
        description = kwargs.pop(
            "description", cleandoc(cls.__doc__) if cls.__doc__ is not None else ""
        )
        parser = super().construct_argparser(description=description, **kwargs)

        # Input
        parser.add_argument(
            "architecture",
            type=cls.str_arg(cls.architectures.keys()),
            help=f"model architecture {cls.architectures.keys()}",
        )
        parser.add_argument("infile", type=cls.input_path_arg(), help="input json file")
        parser.add_argument(
            "outfile", type=cls.output_path_arg(), help="output pth file"
        )

        return parser


if __name__ == "__main__":
    WaifuPyTorchPickler.main()
