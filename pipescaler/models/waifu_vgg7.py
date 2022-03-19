#!/usr/bin/env python
#   pipescaler/models/waifu_vgg7.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Waifu2x Vgg7 model"""
from __future__ import annotations

from torch import Tensor
from torch.nn import Conv2d, LeakyReLU, Module, Sequential, ZeroPad2d


class WaifuVgg7(Module):
    """Waifu2x Vgg7 model"""

    def __init__(self):
        """Initializes model"""
        super().__init__()

        self.activation_function = LeakyReLU(0.1)
        self.pad = ZeroPad2d(7)
        # noinspection PyTypeChecker
        self.sequential = Sequential(
            Conv2d(3, 32, 3),
            self.activation_function,
            Conv2d(32, 32, 3),
            self.activation_function,
            Conv2d(32, 64, 3),
            self.activation_function,
            Conv2d(64, 64, 3),
            self.activation_function,
            Conv2d(64, 128, 3),
            self.activation_function,
            Conv2d(128, 128, 3),
            self.activation_function,
            Conv2d(128, 3, 3),
        )

    def forward(self, tensor: Tensor) -> Tensor:
        return self.sequential.forward(self.pad(tensor))
