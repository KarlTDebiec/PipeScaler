#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Copies videos to an output directory."""
from __future__ import annotations

from logging import info, warning
from shutil import copyfile

from pipescaler.core.pipelines import DirectoryTerminus
from pipescaler.video.core.pipelines import PipeVideo, VideoTerminus


class VideoDirectoryTerminus(VideoTerminus, DirectoryTerminus):
    """Copies videos to an output directory."""

    def __call__(self, input_video: PipeVideo) -> None:
        """Save video to output directory.

        Arguments:
            input_video: Video to save to output directory
        """

        def save_video():
            if not self.directory.exists():
                self.directory.mkdir(parents=True)
                info(f"{self}: '{self.directory}' created")
            if not outfile.parent.exists():
                outfile.parent.mkdir(parents=True)
                info(f"{self}: '{outfile.parent.relative_to(self.directory)}' created")
            if input_video.path is not None:
                copyfile(input_video.path, outfile)
            else:
                raise NotImplementedError("Saving video from memory not implemented")

        suffix = input_video.path.suffix if input_video.path is not None else ".mp4"
        outfile = (self.directory / input_video.location_name).with_suffix(suffix)
        self.observed_files.add(str(outfile.relative_to(self.directory)))
        if outfile.exists():
            if (
                input_video.path
                and outfile.stat().st_mtime > input_video.path.stat().st_mtime
            ):
                info(f"{self}: '{outfile}' is newer; not overwritten")
                return
            warning(
                f"{self}: '{outfile}' already exists; not overwritten; comparing video "
                f"contents not implemented"
            )
            return
        save_video()
        info(f"{self}: '{outfile}' saved")
