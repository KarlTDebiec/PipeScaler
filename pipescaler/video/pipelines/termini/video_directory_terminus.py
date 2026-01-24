#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Copies videos to an output directory."""

from __future__ import annotations

from logging import info, warning
from shutil import copyfile

from pipescaler.core.pipelines import DirectoryTerminus
from pipescaler.video.core.pipelines import PipeVideo, VideoTerminus


class VideoDirectoryTerminus(VideoTerminus, DirectoryTerminus):
    """Copies videos to an output directory."""

    def __call__(self, input_video: PipeVideo):
        """Save video to output directory.

        Arguments:
            input_video: Video to save to output directory
        """

        def save_video():
            """Save video to output directory."""
            if not self.directory.exists():
                self.directory.mkdir(parents=True)
                info(f"{self}: '{self.directory}' created")
            if not output_path.parent.exists():
                output_path.parent.mkdir(parents=True)
                info(
                    f"{self}: "
                    f"'{output_path.parent.relative_to(self.directory)}' created"
                )
            if input_video.path:
                copyfile(input_video.path, output_path)
            else:
                raise NotImplementedError("Saving video from memory not implemented")

        suffix = input_video.path.suffix if input_video.path else ".mp4"
        output_path = (self.directory / input_video.location_name).with_suffix(suffix)
        self.observed_files.add(str(output_path.relative_to(self.directory)))
        if output_path.exists():
            if (
                input_video.path
                and output_path.stat().st_mtime > input_video.path.stat().st_mtime
            ):
                info(f"{self}: '{output_path}' is newer; not overwritten")
                return
            warning(
                f"{self}: '{output_path}' already exists; not overwritten; "
                f"comparing video contents not implemented"
            )
            return
        save_video()
        info(f"{self}: '{output_path}' saved")
