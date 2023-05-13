#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ESRGAN residual-in-residual dense block module."""
from __future__ import annotations

from torch import Tensor
from torch.nn import Module

from pipescaler.image.models.esrgan.residual_dense_block import ResidualDenseBlock


class ResidualInResidualDenseBlock(Module):
    """ESRGAN residual-in-residual dense block module."""

    def __init__(self, n_features: int, growth_channels: int = 32) -> None:
        """Validate configuration and initialize.

        Arguments:
            n_features: Number of input features
            growth_channels: Number of channels in the latent space
        """
        super().__init__()

        self.RDB1 = ResidualDenseBlock(n_features, growth_channels)
        self.RDB2 = ResidualDenseBlock(n_features, growth_channels)
        self.RDB3 = ResidualDenseBlock(n_features, growth_channels)

    def forward(self, tensor: Tensor) -> Tensor:
        """Forward pass.

        Arguments:
            tensor: Batch of inputs
        Returns:
            Processed outputs
        """
        out = self.RDB1(tensor)
        out = self.RDB2(out)
        out = self.RDB3(out)

        return out * 0.2 + tensor  # type: ignore
