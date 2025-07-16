#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ESRGAN residual dense block module."""

from __future__ import annotations

from torch import Tensor, cat
from torch.nn import Conv2d, LeakyReLU, Module


class ResidualDenseBlock(Module):
    """ESRGAN residual dense block module."""

    def __init__(self, n_features: int = 64, growth_channels: int = 32) -> None:
        """Validate configuration and initialize.

        Arguments:
            n_features: Number of input features
            growth_channels: Number of channels in the latent space
        """
        super().__init__()

        self.leaky_relu = LeakyReLU(negative_slope=0.2, inplace=True)
        self.conv1 = Conv2d(n_features, growth_channels, 3, 1, 1)
        self.conv2 = Conv2d(n_features + growth_channels, growth_channels, 3, 1, 1)
        self.conv3 = Conv2d(n_features + 2 * growth_channels, growth_channels, 3, 1, 1)
        self.conv4 = Conv2d(n_features + 3 * growth_channels, growth_channels, 3, 1, 1)
        self.conv5 = Conv2d(n_features + 4 * growth_channels, n_features, 3, 1, 1)

    def forward(self, tensor: Tensor) -> Tensor:
        """Forward pass.

        Arguments:
            tensor: Batch of inputs
        Returns:
            Processed outputs
        """
        x1 = self.leaky_relu(self.conv1(tensor))
        x2 = self.leaky_relu(self.conv2(cat((tensor, x1), 1)))
        x3 = self.leaky_relu(self.conv3(cat((tensor, x1, x2), 1)))
        x4 = self.leaky_relu(self.conv4(cat((tensor, x1, x2, x3), 1)))
        x5 = self.conv5(cat((tensor, x1, x2, x3, x4), 1))
        return x5 * 0.2 + tensor  # type: ignore
