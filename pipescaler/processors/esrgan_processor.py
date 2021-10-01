#!/usr/bin/env python
#   pipescaler/processors/esrgan_processor.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

import collections
from argparse import ArgumentParser
from functools import partial
from inspect import cleandoc
from logging import info, warning
from typing import Any

import numpy as np
import torch
from PIL import Image

from pipescaler.common import validate_input_path
from pipescaler.core import Processor, validate_image_and_convert_mode


class ESRGANProcessor(Processor):
    """
    Upscales and/or denoises image using [ESRGAN](https://github.com/xinntao/ESRGAN);
    supports old and new architectures.

    Adapted from ESRGAN (https://github.com/xinntao/ESRGAN) and Colab-ESRGAN
    (https://github.com/styler00dollar/Colab-ESRGAN), both licensed under the
    `Apache 2.0 License
    (https://raw.githubusercontent.com/xinntao/ESRGAN/master/LICENSE).
    """

    class ResidualDenseBlock5C(torch.nn.Module):
        def __init__(self, nf=64, gc=32, bias=True):
            super().__init__()

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
            self.RDB1 = ESRGANProcessor.ResidualDenseBlock5C(nf, gc)
            self.RDB2 = ESRGANProcessor.ResidualDenseBlock5C(nf, gc)
            self.RDB3 = ESRGANProcessor.ResidualDenseBlock5C(nf, gc)

        def forward(self, x):
            out = self.RDB1(x)
            out = self.RDB2(out)
            out = self.RDB3(out)
            return out * 0.2 + x

    class RRDBNet(torch.nn.Module):
        def __init__(self, in_nc, out_nc, nf, nb, gc=32):
            def make_layer(block, n_layers):
                layers = []
                for _ in range(n_layers):
                    layers.append(block())
                return torch.nn.Sequential(*layers)

            super().__init__()
            RRDB_block_f = partial(ESRGANProcessor.RRDB, nf=nf, gc=gc)

            self.conv_first = torch.nn.Conv2d(in_nc, nf, 3, 1, 1, bias=True)
            self.RRDB_trunk = make_layer(RRDB_block_f, nb)
            self.trunk_conv = torch.nn.Conv2d(nf, nf, 3, 1, 1, bias=True)

            self.HRconv = torch.nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
            self.conv_last = torch.nn.Conv2d(nf, out_nc, 3, 1, 1, bias=True)

            self.lrelu = torch.nn.LeakyReLU(negative_slope=0.2, inplace=True)

            self.n_upscale = 0
            self.nf = nf

        def load_state_dict(self, state_dict, scale, strict=True):
            self.n_upscale = scale

            # build upconv layers based on model scale
            for n in range(1, self.n_upscale + 1):
                upconv = torch.nn.Conv2d(self.nf, self.nf, 3, 1, 1, bias=True)
                setattr(self, "upconv%d" % n, upconv)

            return super().load_state_dict(state_dict, strict)

        def forward(self, x):
            fea = self.conv_first(x)
            trunk = self.trunk_conv(self.RRDB_trunk(fea))
            fea = fea + trunk

            # apply upconv layers
            for n in range(1, self.n_upscale + 1):
                upconv = getattr(self, "upconv%d" % n)
                fea = self.lrelu(
                    upconv(
                        torch.nn.functional.interpolate(
                            fea, scale_factor=2, mode="nearest"
                        )
                    )
                )

            out = self.conv_last(self.lrelu(self.HRconv(fea)))

            return out

    class RRDBNetUpscaler:
        def __init__(self, model_infile, device):
            net, scale = ESRGANProcessor.load_model(model_infile)

            model_net = ESRGANProcessor.RRDBNet(3, 3, 64, 23)
            model_net.load_state_dict(net, scale, strict=True)
            model_net.eval()

            for _, v in model_net.named_parameters():
                v.requires_grad = False

            self.model = model_net.to(device)
            self.device = device
            self.scale_factor = 2 ** scale

        def upscale(self, input_datum):
            input_datum = input_datum * 1.0 / 255
            input_datum = np.transpose(input_datum[:, :, [2, 1, 0]], (2, 0, 1))
            input_datum = torch.from_numpy(input_datum).float()
            input_datum = input_datum.unsqueeze(0).to(self.device)

            output_datum = (
                self.model(input_datum)
                .data.squeeze()
                .float()
                .cpu()
                .clamp_(0, 1)
                .numpy()
            )
            output_datum = np.transpose(output_datum[[2, 1, 0], :, :], (1, 2, 0))
            output_datum = np.array(output_datum * 255, np.uint8)

            return output_datum

    def __init__(self, model_infile: str, device: str = "cuda", **kwargs: Any) -> None:
        """
        Validates and stores static configuration.

        Arguments:
            model_infile (str): Path to model infile
            device (str): Device on which to compute
        """
        super().__init__(**kwargs)

        # Store configuration
        self.model_infile = validate_input_path(model_infile)
        if device == "cuda":
            try:
                self.upscaler = ESRGANProcessor.RRDBNetUpscaler(
                    self.model_infile, torch.device(device)
                )
                self.cpu_upscaler = ESRGANProcessor.RRDBNetUpscaler(
                    self.model_infile, torch.device("cpu")
                )
            except AssertionError as e:
                warning(
                    f"{self}: CUDA ESRGAN upscaler raised exception: '{e}'; "
                    f"trying CPU upscaler"
                )
                self.upscaler = ESRGANProcessor.RRDBNetUpscaler(
                    self.model_infile, torch.device("cpu")
                )
                self.cpu_upscaler = None
        else:
            self.upscaler = ESRGANProcessor.RRDBNetUpscaler(
                self.model_infile, torch.device(device)
            )
            self.cpu_upscaler = None
        # TODO: Determine output scale and store as self.scale

    def process_file(self, infile: str, outfile: str) -> None:
        """
        Processes infile and writes the resulting output to outfile.

        Arguments:
            infile (str): Input file
            outfile (str): Output file
        """

        # Read image
        input_image, input_mode = validate_image_and_convert_mode(
            infile, ["L", "RGB"], "RGB"
        )
        input_datum = np.array(input_image)

        # Process image
        try:
            output_datum = self.upscaler.upscale(input_datum)
        except RuntimeError as e:
            if self.cpu_upscaler is not None:
                warning(
                    f"{self}: CUDA ESRGAN upscaler raised exception: '{e}'; "
                    f"trying CPU upscaler"
                )
                output_datum = self.cpu_upscaler.upscale(input_datum)
            else:
                raise e
        output_image = Image.fromarray(output_datum)
        if input_mode == "L":
            output_image = output_image.convert("L")

        # Write image
        output_image.save(outfile)
        info(f"{self}: '{outfile}' saved")

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Args:
            kwargs (Any): Additional keyword arguments

        Returns:
            parser (ArgumentParser): Argument parser
        """
        description = kwargs.get("description", cleandoc(cls.__doc__))
        parser = super().construct_argparser(description=description, **kwargs)

        # Input
        parser.add_argument(
            "--model",
            dest="model_infile",
            required=True,
            type=cls.input_path_arg(),
            help="model input file",
        )

        # Operations
        parser.add_argument(
            "--device",
            default="cuda",
            type=cls.str_arg(options=["cpu", "cuda"]),
            help="device (default: %(default)s)",
        )

        return parser

    @classmethod
    def load_model(cls, model_infile: str):
        state_dict = torch.load(model_infile)

        # check for old model format
        if "model.0.weight" in state_dict:
            # remap dict keys to new format
            scale_index = cls.get_old_scale_index(state_dict)
            keymap = cls.build_old_keymap(scale_index)
            state_dict = {keymap[k]: v for k, v in state_dict.items()}
        else:
            scale_index = cls.get_scale_index(state_dict)

        return state_dict, scale_index

    @staticmethod
    def build_old_keymap(n_upscale):

        # Build initial keymap
        keymap = collections.OrderedDict()
        keymap["model.0"] = "conv_first"
        for i in range(23):
            for j in range(1, 4):
                for k in range(1, 6):
                    keymap[
                        f"model.1.sub.{i}.RDB{j}.conv{k}.0"
                    ] = f"RRDB_trunk.{i}.RDB{j}.conv{k}"
        keymap["model.1.sub.23"] = "trunk_conv"
        n = 0
        for i in range(1, n_upscale + 1):
            n += 3
            keymap[f"model.{n}"] = f"upconv{i}"
        keymap[f"model.{(n + 2)}"] = "HRconv"
        keymap[f"model.{(n + 4)}"] = "conv_last"

        # Build final keymap
        keymap_final = collections.OrderedDict()
        for k1, k2 in keymap.items():
            keymap_final[f"{k1}.weight"] = f"{k2}.weight"
            keymap_final[f"{k1}.bias"] = f"{k2}.bias"

        return keymap_final

    @staticmethod
    def get_old_scale_index(state_dict):
        try:
            # get largest model index from keys like "model.X.weight"
            max_index = max([int(n.split(".")[1]) for n in state_dict.keys()])
        except:
            # invalid model dict format?
            raise RuntimeError("Unable to determine scale index for model")

        return (max_index - 4) // 3

    @staticmethod
    def get_scale_index(state_dict):
        # this is more or less guesswork, since I haven't seen any non-4x
        # models using the new format in the wild, but it should work in
        # theory
        max_index = 0

        for k in state_dict.keys():
            if k.startswith("upconv") and k.endswith(".weight"):
                max_index = max(max_index, int(k[6:-7]))

        return max_index


if __name__ == "__main__":
    ESRGANProcessor.main()
