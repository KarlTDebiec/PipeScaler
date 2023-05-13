#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Yields videos from a directory."""
from __future__ import annotations

from pathlib import Path

from pipescaler.core.pipelines import DirectorySource
from pipescaler.video.core.pipelines import PipeVideo


class VideoDirectorySource(DirectorySource):
    """Yields videos from a directory."""

    def __next__(self) -> PipeVideo:
        """Yield next image."""
        if self.index < len(self.file_paths):
            file_path = self.file_paths[self.index]
            self.index += 1
            relative_path: Path | None = file_path.parent.relative_to(self.directory)
            if relative_path == Path("../../sources/video"):
                relative_path = None
            return PipeVideo(path=file_path, location=relative_path)
        raise StopIteration
