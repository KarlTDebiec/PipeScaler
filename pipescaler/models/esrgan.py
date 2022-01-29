#!/usr/bin/env python
#   pipescaler/models/esrgan.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""ESRGAN model"""
from __future__ import annotations

from functools import partial

from torch import Tensor, cat
from torch.nn import Conv2d, ConvTranspose2d, LeakyReLU, Module, Sequential, ZeroPad2d
from torch.nn.functional import interpolate


class ResidualDenseBlock5C(Module):
    def __init__(self, nf=64, gc=32, bias=True):
        super().__init__()

        self.leaky_relu = LeakyReLU(negative_slope=0.2, inplace=True)
        self.conv1 = Conv2d(nf, gc, 3, 1, 1, bias=bias)
        self.conv2 = Conv2d(nf + gc, gc, 3, 1, 1, bias=bias)
        self.conv3 = Conv2d(nf + 2 * gc, gc, 3, 1, 1, bias=bias)
        self.conv4 = Conv2d(nf + 3 * gc, gc, 3, 1, 1, bias=bias)
        self.conv5 = Conv2d(nf + 4 * gc, nf, 3, 1, 1, bias=bias)

    def forward(self, tensor: Tensor) -> Tensor:
        x1 = self.leaky_relu(self.conv1(tensor))
        x2 = self.leaky_relu(self.conv2(cat((tensor, x1), 1)))
        x3 = self.leaky_relu(self.conv3(cat((tensor, x1, x2), 1)))
        x4 = self.leaky_relu(self.conv4(cat((tensor, x1, x2, x3), 1)))
        x5 = self.conv5(cat((tensor, x1, x2, x3, x4), 1))
        return x5 * 0.2 + tensor


class ResidualInResidualDenseBlock(Module):
    def __init__(self, nf, gc=32):
        super().__init__()
        self.RDB1 = ResidualDenseBlock5C(nf, gc)
        self.RDB2 = ResidualDenseBlock5C(nf, gc)
        self.RDB3 = ResidualDenseBlock5C(nf, gc)

    def forward(self, tensor: Tensor) -> Tensor:
        out = self.RDB1(tensor)
        out = self.RDB2(out)
        out = self.RDB3(out)
        return out * 0.2 + tensor


class RRDBNet(Module):
    def __init__(self, in_nc, out_nc, nf, nb, gc=32):
        def make_layer(block, n_layers):
            layers = []
            for _ in range(n_layers):
                layers.append(block())
            return Sequential(*layers)

        super().__init__()
        RRDB_block_f = partial(ResidualInResidualDenseBlock, nf=nf, gc=gc)

        self.conv_first = Conv2d(in_nc, nf, 3, 1, 1, bias=True)
        self.RRDB_trunk = make_layer(RRDB_block_f, nb)
        self.trunk_conv = Conv2d(nf, nf, 3, 1, 1, bias=True)

        self.HRconv = Conv2d(nf, nf, 3, 1, 1, bias=True)
        self.conv_last = Conv2d(nf, out_nc, 3, 1, 1, bias=True)

        self.leaky_relu = LeakyReLU(negative_slope=0.2, inplace=True)

        self.n_upscale = 0
        self.nf = nf

    def load_state_dict(self, state_dict, scale, strict=True):
        self.n_upscale = scale

        # build upconv layers based on model scale
        for n in range(1, self.n_upscale + 1):
            upconv = Conv2d(self.nf, self.nf, 3, 1, 1, bias=True)
            setattr(self, "upconv%d" % n, upconv)

        return super().load_state_dict(state_dict, strict)

    def forward(self, tensor: Tensor) -> Tensor:
        fea = self.conv_first(tensor)
        trunk = self.trunk_conv(self.RRDB_trunk(fea))
        fea = fea + trunk

        # apply upconv layers
        for n in range(1, self.n_upscale + 1):
            upconv = getattr(self, "upconv%d" % n)
            fea = self.leaky_relu(
                upconv(interpolate(fea, scale_factor=2, mode="nearest"))
            )

        out = self.conv_last(self.leaky_relu(self.HRconv(fea)))

        return out
