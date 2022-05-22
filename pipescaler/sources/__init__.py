#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Source stages."""
from __future__ import annotations

from pipescaler.sources.citra_source import CitraSource
from pipescaler.sources.directory_source import DirectorySource
from pipescaler.sources.dolphin_source import DolphinSource
from pipescaler.sources.texmod_source import TexmodSource

__all__: list[str] = ["CitraSource", "DirectorySource", "DolphinSource", "TexmodSource"]
