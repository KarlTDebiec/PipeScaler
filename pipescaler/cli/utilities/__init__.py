#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Command line interfaces for utilities."""
from __future__ import annotations

from pipescaler.cli.utilities.apng_creator_cli import ApngCreatorCli
from pipescaler.cli.utilities.esrgan_serializer_cli import EsrganSerializerCli
from pipescaler.cli.utilities.host_cli import HostCli
from pipescaler.cli.utilities.waifu_serializer_cli import WaifuSerializerCli

__all__ = [
    "ApngCreatorCli",
    "EsrganSerializerCli",
    "HostCli",
    "WaifuSerializerCli",
]
