#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Yields images from a directory."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from pipescaler.core.pipelines import DirectorySource
from pipescaler.image.core.pipelines import PipeImage


class ImageDirectorySource(DirectorySource):
    """Yields images from a directory."""

    def __next__(self) -> PipeImage:
        """Yield next image."""
        if self.index < len(self.file_paths):
            file_path = self.file_paths[self.index]
            self.index += 1
            relative_path: Optional[Path] = file_path.parent.relative_to(self.directory)
            if relative_path == Path("../../sources/image"):
                relative_path = None
            return PipeImage(path=file_path, location=relative_path)
        raise StopIteration
