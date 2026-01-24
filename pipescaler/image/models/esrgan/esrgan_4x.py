#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ESRGAN 4X module."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from torch import Tensor
from torch.nn import Conv2d
from torch.nn.functional import interpolate

from pipescaler.image.models.esrgan.esrgan import Esrgan


class Esrgan4x(Esrgan):
    """ESRGAN module."""

    def forward(self, tensor: Tensor) -> Tensor:
        """Forward pass.

        Arguments:
            tensor: Batch of inputs
        Returns:
            Processed outputs
        """
        fea = self.conv_first(tensor)
        trunk = self.trunk_conv(self.RRDB_trunk(fea))
        fea = fea + trunk

        fea = self.leaky_relu(
            self.upconv1(interpolate(fea, scale_factor=2, mode="nearest"))
        )
        fea = self.leaky_relu(
            self.upconv2(interpolate(fea, scale_factor=2, mode="nearest"))
        )

        out = self.conv_last(self.leaky_relu(self.HRconv(fea)))

        return out  # type: ignore

    def load_state_dict(
        self, state_dict: Mapping[str, Any], strict: bool = True
    ) -> Any:
        """Copy parameters and buffers from state_dict.

        Actual return type is torch.nn.modules.module._IncompatibleKeys.

        Arguments:
            state_dict: Parameters and persistent buffers
            strict: Whether to strictly enforce that keys in state_dict match
        Returns:
            Named tuple with missing and unexpected keys
        """
        self.upconv1 = Conv2d(self.n_features, self.n_features, 3, 1, 1)
        self.upconv2 = Conv2d(self.n_features, self.n_features, 3, 1, 1)

        return super().load_state_dict(state_dict, strict)

    @classmethod
    def scale(cls) -> int:
        """Scale of model."""
        return 4
