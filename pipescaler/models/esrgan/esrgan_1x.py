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

from collections import OrderedDict

from torch import Tensor
from torch.nn import Conv2d
from torch.nn.functional import interpolate

from pipescaler.models.esrgan import Esrgan


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
        trunk = self.conv_trunk(self.RRDB_trunk(fea))
        fea = fea + trunk

        fea = self.leaky_relu(
            self.upconv1(interpolate(fea, scale_factor=2, mode="nearest"))
        )

        out = self.conv_last(self.leaky_relu(self.HRconv(fea)))

        return out

    def load_state_dict(
        self, state_dict: OrderedDict[str, Tensor], strict: bool = True
    ):
        self.upconv1 = Conv2d(self.n_features, self.n_features, 3, 1, 1)

        return super().load_state_dict(state_dict, strict)

    @classmethod
    @property
    def scale(cls) -> int:
        return 1
