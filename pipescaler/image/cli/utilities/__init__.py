#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Image utility command-line interfaces."""
from __future__ import annotations

from pipescaler.image.cli.utilities.esrgan_serializer_cli import EsrganSerializerCli
from pipescaler.image.cli.utilities.waifu_serializer_cli import WaifuSerializerCli

__all__ = [
    "EsrganSerializerCli",
    "WaifuSerializerCli",
]
