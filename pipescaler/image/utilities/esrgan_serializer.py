#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Converts ESRGAN models to PyTorch's serialized pth format."""

from __future__ import annotations

from collections import OrderedDict
from logging import info
from pathlib import Path

import torch
from torch import Tensor

from pipescaler.common.validation import val_input_path, val_output_path
from pipescaler.core import Utility
from pipescaler.image.models.esrgan import Esrgan, Esrgan1x, Esrgan4x


class EsrganSerializer(Utility):
    """Converts ESRGAN models to PyTorch's serialized pth format."""

    @classmethod
    def get_model(cls, state_dict: OrderedDict[str, Tensor]) -> Esrgan:
        """Get model from state_dict.

        Arguments:
            state_dict: State dictionary
        Returns:
            Model
        """
        state_dict, scale = cls.parse_state_dict(state_dict)
        if scale == 0:
            model: Esrgan = Esrgan1x()
        else:
            model = Esrgan4x()

        model.load_state_dict(state_dict, strict=True)
        model.eval()

        for _, v in model.named_parameters():
            v.requires_grad = False

        return model

    @classmethod
    def parse_state_dict(
        cls, state_dict: OrderedDict[str, Tensor]
    ) -> tuple[OrderedDict[str, Tensor], int]:
        """Parse state_dict.

        Arguments:
            state_dict: State dictionary
        Returns:
            State dictionary, scale
        """
        if "model.0.weight" in state_dict:
            scale = cls.get_old_scale_index(state_dict)
            keymap = cls.build_old_keymap(scale)
            state_dict = OrderedDict({keymap[k]: v for k, v in state_dict.items()})
        else:
            scale = cls.get_scale_index(state_dict)

        return state_dict, scale

    @classmethod
    def run(cls, input_path: Path | str, output_path: Path | str):
        """Convert input file to output file.

        Arguments:
            input_path: Input file
            output_path: Output file
        """
        input_path = val_input_path(input_path)
        output_path = val_output_path(output_path)

        state_dict = torch.load(input_path)
        model = cls.get_model(state_dict)
        info(f"{cls}: Model built from '{input_path}'")

        torch.save(model, output_path)
        info(f"{cls}: Complete serialized model saved to '{output_path}'")

    @staticmethod
    def build_old_keymap(scale: int) -> dict[str, str]:
        """Build keymap for old state_dict.

        Arguments:
            scale: Scale
        Returns:
            Keymap
        """
        # Build initial keymap
        keymap = OrderedDict()
        keymap["model.0"] = "conv_first"
        for i in range(23):
            for j in range(1, 4):
                for k in range(1, 6):
                    keymap[f"model.1.sub.{i}.RDB{j}.conv{k}.0"] = (
                        f"RRDB_trunk.{i}.RDB{j}.conv{k}"
                    )
        keymap["model.1.sub.23"] = "trunk_conv"
        n = 0
        for i in range(1, scale + 1):
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
    def get_old_scale_index(state_dict: dict[str, Tensor]) -> int:
        """Get scale index for old state_dict.

        Arguments:
            state_dict: State dictionary
        Returns:
            Scale index
        """
        try:
            max_index = max(int(n.split(".")[1]) for n in state_dict.keys())
        except (IndexError, KeyError) as exc:
            raise RuntimeError("Unable to determine scale index for model.") from exc

        return (max_index - 4) // 3

    @staticmethod
    def get_scale_index(state_dict: dict[str, Tensor]) -> int:
        """Get scale index for state_dict.

        Arguments:
            state_dict: State dictionary
        Returns:
            Scale index
        """
        max_index = 0

        for k in state_dict.keys():
            if k.startswith("upconv") and k.endswith(".weight"):
                max_index = max(max_index, int(k[6:-7]))

        return max_index
