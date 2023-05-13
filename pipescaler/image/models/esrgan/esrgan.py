#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ESRGAN module."""
from __future__ import annotations

from abc import ABC
from functools import partial

from torch.nn import Conv2d, LeakyReLU, Module, Sequential

from pipescaler.image.models.esrgan.residual_in_residual_dense_block import (
    ResidualInResidualDenseBlock,
)


class Esrgan(Module, ABC):
    """ESRGAN module."""

    def __init__(
        self,
        *,
        in_channels: int = 3,
        out_channels: int = 3,
        n_features: int = 64,
        n_blocks: int = 23,
        growth_channels: int = 32,
    ):
        """Validate configuration and initialize.

        Arguments:
            in_channels: Number of input channels
            out_channels: Number of output channels
            n_features: Number of features per block
            n_blocks: Number of blocks per stage
            growth_channels: Number of growth channels per block
        """
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
        """Make a layer of blocks.

        Arguments:
            block: Block to use
            n_layers: Number of layers
        Returns:
            Layer of blocks
        """
        return Sequential(*(block() for _ in range(n_layers)))
