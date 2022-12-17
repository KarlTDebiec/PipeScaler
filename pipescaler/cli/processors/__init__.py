#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Command line interfaces for image processors."""
from __future__ import annotations

from pipescaler.cli.processors.crop_cli import CropCli
from pipescaler.cli.processors.esrgan_cli import EsrganCli
from pipescaler.cli.processors.expand_cli import ExpandCli
from pipescaler.cli.processors.height_to_normal_cli import HeightToNormalCli
from pipescaler.cli.processors.mode_cli import ModeCli
from pipescaler.cli.processors.resize_cli import ResizeCli
from pipescaler.cli.processors.sharpen_cli import SharpenCli
from pipescaler.cli.processors.solid_color_cli import SolidColorCli
from pipescaler.cli.processors.threshold_cli import ThresholdCli
from pipescaler.cli.processors.waifu_cli import WaifuCli
from pipescaler.cli.processors.web_cli import WebCli
from pipescaler.cli.processors.xbrz_cli import XbrzCli

__all__ = [
    "CropCli",
    "EsrganCli",
    "ExpandCli",
    "HeightToNormalCli",
    "ModeCli",
    "ResizeCli",
    "SharpenCli",
    "SolidColorCli",
    "ThresholdCli",
    "WaifuCli",
    "WebCli",
    "XbrzCli",
]
