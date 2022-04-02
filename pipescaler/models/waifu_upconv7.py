#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Waifu2x Upconv7 model"""
from __future__ import annotations

from torch import Tensor
from torch.nn import Conv2d, ConvTranspose2d, LeakyReLU, Module, Sequential, ZeroPad2d


class WaifuUpConv7(Module):
    """Waifu2x Upconv7 model"""

    def __init__(self):
        """Initializes model"""
        super().__init__()

        self.leaky_relu = LeakyReLU(0.1)
        self.pad = ZeroPad2d(7)
        # noinspection PyTypeChecker
        self.sequential = Sequential(
            Conv2d(3, 16, 3),
            self.leaky_relu,
            Conv2d(16, 32, 3),
            self.leaky_relu,
            Conv2d(32, 64, 3),
            self.leaky_relu,
            Conv2d(64, 128, 3),
            self.leaky_relu,
            Conv2d(128, 128, 3),
            self.leaky_relu,
            Conv2d(128, 256, 3),
            self.leaky_relu,
            ConvTranspose2d(256, 3, kernel_size=4, stride=2, padding=3, bias=False),
        )

    def forward(self, tensor: Tensor) -> Tensor:
        return self.sequential.forward(self.pad(tensor))
