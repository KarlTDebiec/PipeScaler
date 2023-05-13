#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ESRGAN 1X module."""
from __future__ import annotations

from torch import Tensor

from pipescaler.image.models.esrgan.esrgan import Esrgan


class Esrgan1x(Esrgan):
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

        out = self.conv_last(self.leaky_relu(self.HRconv(fea)))

        return out  # type: ignore

    @classmethod
    def scale(cls) -> int:
        """Scale of model."""
        return 1
