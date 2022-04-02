#!/usr/bin/env python
#   pipescaler/models/esrgan.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""ESRGAN module."""
from __future__ import annotations

from functools import partial

from torch.nn import Conv2d, LeakyReLU, Module, Sequential

from pipescaler.models.esrgan.residual_in_residual_dense_block import (
    ResidualInResidualDenseBlock,
)


class Esrgan(Module):
    """ESRGAN module."""

    def __init__(
        self,
        in_channels: int = 3,
        out_channels: int = 3,
        n_features: int = 64,
        n_blocks: int = 23,
        growth_channels: int = 32,
    ):
        """Initialize."""
        super().__init__()

        RRDB_block_f = partial(
            ResidualInResidualDenseBlock,
            n_features=n_features,
            growth_channels=growth_channels,
        )

        self.n_features = n_features

        self.conv_first = Conv2d(in_channels, n_features, 3, 1, 1, bias=True)
        self.RRDB_trunk = self.make_layer(RRDB_block_f, n_blocks)
        self.trunk_conv = Conv2d(n_features, n_features, 3, 1, 1, bias=True)

        self.HRconv = Conv2d(n_features, n_features, 3, 1, 1, bias=True)
        self.conv_last = Conv2d(n_features, out_channels, 3, 1, 1, bias=True)

        self.leaky_relu = LeakyReLU(negative_slope=0.2, inplace=True)

    @staticmethod
    def make_layer(block, n_layers):
        return Sequential(*(block() for _ in range(n_layers)))
