#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler image processor command-line interfaces package."""

from __future__ import annotations

from pipescaler.image.cli.processors.crop_cli import CropCli
from pipescaler.image.cli.processors.expand_cli import ExpandCli
from pipescaler.image.cli.processors.height_to_normal_cli import HeightToNormalCli
from pipescaler.image.cli.processors.mode_cli import ModeCli
from pipescaler.image.cli.processors.resize_cli import ResizeCli
from pipescaler.image.cli.processors.sharpen_cli import SharpenCli
from pipescaler.image.cli.processors.solid_color_cli import SolidColorCli
from pipescaler.image.cli.processors.threshold_cli import ThresholdCli
from pipescaler.image.cli.processors.xbrz_cli import XbrzCli

__all__ = [
    "CropCli",
    "ExpandCli",
    "HeightToNormalCli",
    "ModeCli",
    "ResizeCli",
    "SharpenCli",
    "SolidColorCli",
    "ThresholdCli",
    "XbrzCli",
]
