#!/usr/bin/env python
#   pipescaler/processors/ESRGANProcessor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Processes an image using ESRGAN.

Adapted from ESRGAN (https://github.com/xinntao/ESRGAN), licensed
under the `Apache 2.0 License
(https://raw.githubusercontent.com/xinntao/ESRGAN/master/LICENSE)."""
################################### MODULES ###################################
from __future__ import annotations

from argparse import ArgumentParser
from functools import partial
from os.path import basename, splitext
from typing import Any

import cv2
import numpy as np
import torch

from pipescaler.common import validate_infile
from pipescaler.processors.Processor import Processor


################################### CLASSES ###################################
class ESRGANProcessor(Processor):
    # region Classes

    class ResidualDenseBlock_5C(torch.nn.Module):
        def __init__(self, nf=64, gc=32, bias=True):
            super().__init__()

            # gc: growth channel, i.e. intermediate channels
            self.conv1 = torch.nn.Conv2d(nf, gc, 3, 1, 1, bias=bias)
            self.conv2 = torch.nn.Conv2d(nf + gc, gc, 3, 1, 1, bias=bias)
            self.conv3 = torch.nn.Conv2d(nf + 2 * gc, gc, 3, 1, 1, bias=bias)
            self.conv4 = torch.nn.Conv2d(nf + 3 * gc, gc, 3, 1, 1, bias=bias)
            self.conv5 = torch.nn.Conv2d(nf + 4 * gc, nf, 3, 1, 1, bias=bias)
            self.lrelu = torch.nn.LeakyReLU(negative_slope=0.2, inplace=True)

        def forward(self, x):
            x1 = self.lrelu(self.conv1(x))
            x2 = self.lrelu(self.conv2(torch.cat((x, x1), 1)))
            x3 = self.lrelu(self.conv3(torch.cat((x, x1, x2), 1)))
            x4 = self.lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
            x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1))

            return x5 * 0.2 + x

    class RRDB(torch.nn.Module):
        def __init__(self, nf, gc=32):
            super().__init__()

            self.RDB1 = ESRGANProcessor.ResidualDenseBlock_5C(nf, gc)
            self.RDB2 = ESRGANProcessor.ResidualDenseBlock_5C(nf, gc)
            self.RDB3 = ESRGANProcessor.ResidualDenseBlock_5C(nf, gc)

        def forward(self, x):
            out = self.RDB1(x)
            out = self.RDB2(out)
            out = self.RDB3(out)

            return out * 0.2 + x

    class RRDBNet(torch.nn.Module):
        def __init__(self, in_nc, out_nc, nf, nb, gc=32):
            super().__init__()

            RRDB_block_f = partial(ESRGANProcessor.RRDB, nf=nf, gc=gc)

            self.conv_first = torch.nn.Conv2d(in_nc, nf, 3, 1, 1, bias=True)
            self.RRDB_trunk = self.make_layer(RRDB_block_f, nb)
            self.trunk_conv = torch.nn.Conv2d(nf, nf, 3, 1, 1, bias=True)

            #### upsampling
            self.upconv1 = torch.nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
            self.upconv2 = torch.nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
            self.HRconv = torch.nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
            self.conv_last = torch.nn.Conv2d(nf, out_nc, 3, 1, 1, bias=True)

            self.lrelu = torch.nn.LeakyReLU(negative_slope=0.2, inplace=True)

        def forward(self, x):
            fea = self.conv_first(x)
            trunk = self.trunk_conv(self.RRDB_trunk(fea))
            fea = fea + trunk

            fea = self.lrelu(self.upconv1(
                torch.nn.functional.interpolate(
                    fea, scale_factor=2, mode="nearest")))
            fea = self.lrelu(self.upconv2(
                torch.nn.functional.interpolate(
                    fea, scale_factor=2, mode="nearest")))
            out = self.conv_last(self.lrelu(self.HRconv(fea)))

            return out

        @staticmethod
        def make_layer(block, n_layers):
            layers = []
            for _ in range(n_layers):
                layers.append(block())

            return torch.nn.Sequential(*layers)

    # endregion

    # region Builtins

    def __init__(self,
                 model_infile: str,
                 device: str = "cpu",
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.model_infile = model_infile
        self.device = device
        self.desc = f"esrgan-{splitext(basename(self.model_infile))[0]}"

    # endregion

    # region Properties

    @property
    def model_infile(self) -> str:
        """str: Path to model infile"""
        if not hasattr(self, "_model_infile"):
            raise ValueError()
        return self._model_infile

    @model_infile.setter
    def model_infile(self, value: str) -> None:
        self._model_infile = validate_infile(value)

    # endregion

    # region Methods

    def process_file_in_pipeline(self, infile: str, outfile: str) -> None:
        self.process_file(infile, outfile, self.model_infile, self.device,
                          self.pipeline.verbosity)

    # endregion

    # region Class Methods

    @classmethod
    def construct_argparser(cls) -> ArgumentParser:
        """
        Constructs argument parser

        Returns:
            parser (ArgumentParser): Argument parser
        """
        parser = super().construct_argparser(description=__doc__)

        # Input
        parser.add_argument(
            "-m", "--model",
            dest="model_infile",
            required=True,
            type=cls.infile_argument(),
            help="model input file")

        # Operations
        parser.add_argument(
            "-d", "--device",
            default="cpu",
            type=str,
            help="device (default: cpu)")

        return parser

    @classmethod
    def process_file(cls,
                     infile: str,
                     outfile: str,
                     model_infile: str,
                     device: str = "cpu",
                     **kwargs: Any) -> None:
        # Read model
        model = cls.RRDBNet(3, 3, 64, 23, gc=32)
        model.load_state_dict(torch.load(model_infile), strict=True)
        model.eval()
        model = model.to(device)

        # Read image
        image = cv2.imread(infile, cv2.IMREAD_COLOR)
        image = image * 1.0 / 255
        image = torch.from_numpy(
            np.transpose(image[:, :, [2, 1, 0]], (2, 0, 1))).float()
        image2 = image.unsqueeze(0)
        image2 = image2.to(device)

        # Run model
        with torch.no_grad():
            output = model(
                image2).data.squeeze().float().cpu().clamp_(0, 1).numpy()
        output = np.transpose(output[[2, 1, 0], :, :], (1, 2, 0))
        output = (output * 255.0).round()

        # Write image
        cv2.imwrite(outfile, output)

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    ESRGANProcessor.main()
