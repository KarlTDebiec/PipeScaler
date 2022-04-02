#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Converts ESRGAN models to PyTorch's serialized pth format."""
from __future__ import annotations

from collections import OrderedDict
from logging import info

import torch
from torch import Tensor

from pipescaler.common import validate_input_file, validate_output_file
from pipescaler.models.esrgan import Esrgan1x, Esrgan4x


class EsrganSerializer:
    """Converts ESRGAN models to PyTorch's serialized pth format."""

    def __call__(self, infile: str, outfile: str) -> None:
        """Converts infile to outfile.

        Arguments:
            infile: Input file
            outfile: Output file
        """
        self.infile = validate_input_file(infile)
        self.outfile = validate_output_file(outfile)

        state_dict, scale = self.load_model(infile)
        if scale == 0:
            model = Esrgan1x(3, 3, 64, 23)
        else:
            model = Esrgan4x(3, 3, 64, 23)
        info(f"{self}: Esrgan model built")

        model.load_state_dict(state_dict, strict=True)
        model.eval()

        for _, v in model.named_parameters():
            v.requires_grad = False

        torch.save(model, self.outfile)
        info(f"{self}: Complete serialized model saved to '{self.outfile}'")

    @staticmethod
    def build_old_keymap(n_upscale: int) -> dict[str, str]:
        # Build initial keymap
        keymap = OrderedDict()
        keymap["model.0"] = "conv_first"
        for i in range(23):
            for j in range(1, 4):
                for k in range(1, 6):
                    keymap[
                        f"model.1.sub.{i}.RDB{j}.conv{k}.0"
                    ] = f"RRDB_trunk.{i}.RDB{j}.conv{k}"
        keymap["model.1.sub.23"] = "trunk_conv"
        n = 0
        for i in range(1, n_upscale + 1):
            n += 3
            keymap[f"model.{n}"] = f"upconv{i}"
        keymap[f"model.{(n + 2)}"] = "HRconv"
        keymap[f"model.{(n + 4)}"] = "conv_last"

        # Build final keymap
        keymap_final = OrderedDict()
        for k1, k2 in keymap.items():
            keymap_final[f"{k1}.weight"] = f"{k2}.weight"
            keymap_final[f"{k1}.bias"] = f"{k2}.bias"

        return keymap_final

    @staticmethod
    def get_old_scale_index(state_dict: dict[str, str]) -> int:
        try:
            # get the largest model index from keys like "model.X.weight"
            max_index = max([int(n.split(".")[1]) for n in state_dict.keys()])
        except:
            # invalid model dict format?
            raise RuntimeError("Unable to determine scale index for model")

        return (max_index - 4) // 3

    @staticmethod
    def get_scale_index(state_dict: dict[str, str]) -> int:
        max_index = 0

        for k in state_dict.keys():
            if k.startswith("upconv") and k.endswith(".weight"):
                max_index = max(max_index, int(k[6:-7]))

        return max_index

    @classmethod
    def load_model(cls, model_infile: str) -> tuple[OrderedDict[str, Tensor], int]:
        state_dict = torch.load(model_infile)

        # check for old model format
        if "model.0.weight" in state_dict:
            # remap dict keys to new format
            scale = cls.get_old_scale_index(state_dict)
            keymap = cls.build_old_keymap(scale)
            state_dict = {keymap[k]: v for k, v in state_dict.items()}
        else:
            scale = cls.get_scale_index(state_dict)

        return state_dict, scale
