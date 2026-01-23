#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Converts Waifu models in JSON format to PyTorch's serialized pth format."""

from __future__ import annotations

import json
from logging import info
from pathlib import Path

import torch

from pipescaler.common.validation import val_input_path, val_output_path, val_str
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

    @classmethod
    def run(cls, architecture: str, input_path: Path | str, output_path: Path | str):
        """Convert input file to output file.

        Arguments:
            architecture: Model architecture
            input_path: Input file
            output_path: Output file
        """
        architecture = val_str(architecture, cls.architectures.keys())
        input_path = val_input_path(input_path)
        output_path = val_output_path(output_path)

        model = cls.architectures[architecture]()
        info(f"{cls}: Waifu {architecture} model built")

        with open(input_path, encoding="utf-8") as input_file:
            weights = json.load(input_file)
        box = []
        for weight in weights:
            box.append(weight["weight"])
            box.append(weight["bias"])
        state_dict = model.state_dict()
        for index, (name, _) in enumerate(state_dict.items()):
            state_dict[name].copy_(torch.FloatTensor(box[index]))
        info(f"{cls}: Model parameters loaded from '{input_path}'")

        torch.save(model, output_path)
        info(f"{cls}: Complete serialized model saved to '{output_path}'")
