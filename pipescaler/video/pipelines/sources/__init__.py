#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PipeScaler video pipeline sources package.

This module may import from: common, core.pipelines, video.core.pipelines

Hierarchy within module:
* video_directory_source
"""

from __future__ import annotations

from .video_directory_source import (
    VideoDirectorySource,
)

__all__ = [
    "VideoDirectorySource",
]
