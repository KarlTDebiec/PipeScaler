#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Converts Waifu models in JSON format to PyTorch's serialized pth format."""
from __future__ import annotations

import json
from logging import info
from pathlib import Path

import torch

from pipescaler.common import validate_input_file, validate_output_file, validate_str
from pipescaler.core import Utility
from pipescaler.image.models import WaifuUpConv7, WaifuVgg7


class WaifuSerializer(Utility):
    """Converts Waifu models in JSON format to PyTorch's serialized pth format.

    Input JSON is available from [yu45020/Waifu2x on GitHub]
    (https://github.com/yu45020/Waifu2x/tree/master/model_check_points)
    """

    architectures = {
        "upconv7": WaifuUpConv7,
        "vgg7": WaifuVgg7,
    }

    def __call__(self, architecture: str, infile: Path, outfile: Path) -> None:
        """Converts infile to outfile.

        Arguments:
            architecture: Model architecture
            infile: Input file
            outfile: Output file
        """
        architecture = validate_str(architecture, self.architectures.keys())
        infile = validate_input_file(infile)
        outfile = validate_output_file(outfile)

        model = self.architectures[architecture]()
        info(f"{self}: Waifu {architecture} model built")

        with open(infile, "r", encoding="utf-8") as input_file:
            weights = json.load(input_file)
        box = []
        for weight in weights:
            box.append(weight["weight"])
            box.append(weight["bias"])
        state_dict = model.state_dict()
        for index, (name, _) in enumerate(state_dict.items()):
            state_dict[name].copy_(torch.FloatTensor(box[index]))
        info(f"{self}: Model parameters loaded from '{infile}'")

        torch.save(model, outfile)
        info(f"{self}: Complete serialized model saved to '{outfile}'")
