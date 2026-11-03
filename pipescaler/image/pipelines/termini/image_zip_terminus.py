#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Collects images into a ZIP archive."""

from __future__ import annotations

from contextlib import ExitStack
from pathlib import Path
from types import TracebackType
from typing import Self
from zipfile import ZIP_DEFLATED, ZipFile

from pipescaler.common.archive import ZipMemberPaths
from pipescaler.common.file import get_temp_file_path
from pipescaler.common.validation import val_output_path
from pipescaler.image.core.pipelines import ImageTerminus, PipeImage

__all__ = ["ImageZipTerminus"]


class ImageZipTerminus(ImageTerminus):
    """Collect images into a ZIP archive published on successful context exit.

    Use a `with` block. Each run replaces the complete output collection; previous
    entries are discarded. File-backed images retain their bytes and extension;
    in-memory images are encoded as PNG. Relative locations and dotted names are
    preserved using forward slashes. Unsafe or colliding member paths are rejected.

    A temporary archive beside the destination replaces it only after all writes
    and archive closure succeed. Processing or write failures discard the temporary
    archive and preserve any existing destination, including when a write exception
    is caught inside the context. Instances are single-use.
    """

    def __init__(self, output_path: Path | str):
        """Validate and store the destination without opening an archive.

        Arguments:
            output_path: archive to publish on successful context exit
        """
        self.output_path = val_output_path(output_path, exist_ok=True, create=False)
        """Path to the output ZIP archive."""
        self._stack = ExitStack()
        self._archive: ZipFile | None = None
        self._temp_path: Path | None = None
        self._member_paths = ZipMemberPaths()
        self._closed = False
        self._failed = False

    def __call__(self, input_obj: PipeImage):
        """Write an image to the temporary archive.

        Arguments:
            input_obj: image to save, preserving its name and relative location
        Raises:
            ValueError: if the context is inactive, a prior write failed, or the
              member path is unsafe or collides with a previous output
            OSError: if the input cannot be read or archive data cannot be written
        """
        if self._archive is None or self._closed:
            raise ValueError("ZIP terminus requires an active context.")
        if self._failed:
            raise ValueError("Cannot write to a failed ZIP terminus.")
        try:
            suffix = input_obj.path.suffix if input_obj.path else ".png"
            path = (input_obj.location or Path()) / f"{input_obj.name}{suffix}"
            member_path = self._member_paths.add(path.as_posix())
            if input_obj.path is not None:
                self._archive.write(input_obj.path, member_path.as_posix())
            else:
                with self._archive.open(
                    member_path.as_posix(), "w", force_zip64=True
                ) as output:
                    input_obj.image.save(output, format="PNG")
        except BaseException:
            self._failed = True
            raise

    def __enter__(self) -> Self:
        """Open a temporary archive beside the destination.

        Returns:
            this active terminus
        Raises:
            ValueError: if this terminus is already active or closed
            OSError: if the output directory or temporary archive cannot be created
        """
        if self._archive is not None or self._closed:
            raise ValueError("Cannot reenter an active or closed ZIP terminus.")
        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self._temp_path = self._stack.enter_context(
                get_temp_file_path(".zip", parent_dir_path=self.output_path.parent)
            )
            self._archive = self._stack.enter_context(
                ZipFile(
                    self._temp_path,
                    "w",
                    compression=ZIP_DEFLATED,
                    strict_timestamps=False,
                )
            )
        except BaseException:
            self._closed = True
            self._stack.close()
            raise
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ):
        """Publish a completed archive or discard it after any failure.

        Arguments:
            exc_type: active exception type, if any
            exc_value: active exception, if any
            traceback: active traceback, if any
        Raises:
            ValueError: if a write failed and its exception was caught in the context
            OSError: if the archive cannot be finalized or the destination replaced
        """
        self._closed = True
        with self._stack:
            if self._archive is not None:
                self._archive.close()
            if exc_type is None:
                if self._failed:
                    raise ValueError("Cannot publish ZIP archive after a failed write.")
                if self._temp_path is not None:
                    self._temp_path.replace(self.output_path)

    def __repr__(self) -> str:
        """Describe the destination configuration.

        Returns:
            reconstructible terminus configuration
        """
        return f"{self.__class__.__name__}(output_path={self.output_path!r})"
