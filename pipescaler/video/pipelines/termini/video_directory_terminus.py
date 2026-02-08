#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Copies videos to an output directory."""

from __future__ import annotations

from logging import info, warning
from shutil import copyfile

from pipescaler.core.pipelines import DirectoryTerminus
from pipescaler.video.core.pipelines import PipeVideo, VideoTerminus


class VideoDirectoryTerminus(VideoTerminus, DirectoryTerminus[PipeVideo]):
    """Copies videos to an output directory."""

    def __call__(self, input_obj: PipeVideo):
        """Save video to output directory.

        Arguments:
            input_obj: Video to save to output directory
        """

        def save_video():
            """Save video to output directory."""
            if not self.dir_path.exists():
                self.dir_path.mkdir(parents=True)
                info(f"{self}: '{self.dir_path}' created")
            if not output_path.parent.exists():
                output_path.parent.mkdir(parents=True)
                info(
                    f"{self}: '{output_path.parent.relative_to(self.dir_path)}' created"
                )
            if input_obj.path:
                copyfile(input_obj.path, output_path)
            else:
                raise NotImplementedError("Saving video from memory not implemented")

        suffix = input_obj.path.suffix if input_obj.path else ".mp4"
        output_path = (self.dir_path / input_obj.location_name).with_suffix(suffix)
        self.observed_files.add(str(output_path.relative_to(self.dir_path)))
        if output_path.exists():
            if (
                input_obj.path
                and output_path.stat().st_mtime > input_obj.path.stat().st_mtime
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
