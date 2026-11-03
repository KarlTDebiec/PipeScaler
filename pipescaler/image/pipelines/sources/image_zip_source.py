#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Yields images from a ZIP archive."""

from __future__ import annotations

import re
from collections.abc import Callable
from contextlib import ExitStack
from os import utime
from pathlib import Path, PurePosixPath
from shutil import copyfileobj
from types import TracebackType
from typing import Self
from zipfile import ZipFile

from pipescaler.common.archive import ZipMemberPaths
from pipescaler.common.file import get_temp_directory_path
from pipescaler.common.validation import val_input_path
from pipescaler.core.pipelines import DirectorySource
from pipescaler.core.sorting import basic_sort
from pipescaler.image.core.pipelines import ImageSource, PipeImage

__all__ = ["ImageZipSource"]


class ImageZipSource(ImageSource):
    """Yield images backed by temporary files extracted from a ZIP archive.

    Use a `with` block or call `close()` to remove the extracted files. Exhaustion
    leaves files available until closure, so collected images remain usable within
    the context. Selected members are extracted during initialization without
    decoding them. On first image access, the first frame is copied into memory
    and its file handles are released. Loaded images and shared processor outputs
    remain usable after closure. Filters and sorting use normalized names with
    forward slashes.

    Extracted files use the archive's filesystem modification time, allowing mtime
    checkpoint validation across runs. Changing the archive invalidates checkpoints
    for all its members when its modification time advances. Member timestamps are
    ignored. Unsafe or colliding selected paths are rejected.
    """

    def __init__(
        self,
        input_path: Path | str,
        *,
        exclusions: set[str | re.Pattern] | None = None,
        inclusions: set[str | re.Pattern] | None = None,
        sort: Callable[[str], int] | Callable[[str], str] = basic_sort,
        reverse: bool = False,
    ):
        """Validate configuration and extract selected members to temporary files.

        Arguments:
            input_path: archive from which to yield images
            exclusions: member name regular expressions to exclude, in addition to
              the directory source's default exclusions
            inclusions: member name regular expressions to include
            sort: function with which to sort member names
            reverse: whether to reverse member sort order
        Raises:
            ValueError: if selected member paths are unsafe or collide
            BadZipFile: if the archive is invalid or a selected member is corrupt
            OSError: if the archive cannot be read or temporary files cannot be written
        """
        super().__init__()
        self.input_path = val_input_path(input_path)
        """Path to the input ZIP archive."""
        self.exclusions = DirectorySource.parse_exclusions(exclusions)
        """Compiled exclusions, including the directory source defaults."""
        self.inclusions = DirectorySource.parse_inclusions(inclusions)
        """Compiled inclusions, or None to include all non-excluded files."""
        self.sort = sort
        """Function with which to sort normalized member names."""
        self.reverse = reverse
        """Whether to reverse member sort order."""
        self.file_paths: list[Path] = []
        """Extracted files in iteration order; valid until closure."""
        self.index = 0
        """Index of the next file to yield."""
        self._stack = ExitStack()
        self._closed = False
        try:
            self._dir_path = self._stack.enter_context(get_temp_directory_path())
            member_paths = ZipMemberPaths()
            mtime_ns = self.input_path.stat().st_mtime_ns
            with ZipFile(self.input_path) as archive:
                for member in archive.infolist():
                    if member.is_dir():
                        continue
                    member_name = PurePosixPath(member.orig_filename).as_posix()
                    if any(e.match(member_name) for e in self.exclusions):
                        continue
                    if self.inclusions and not any(
                        i.match(member_name) for i in self.inclusions
                    ):
                        continue
                    member_path = member_paths.add(member.orig_filename)
                    file_path = self._dir_path.joinpath(*member_path.parts)
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(member) as source, file_path.open("xb") as output:
                        copyfileobj(source, output)
                    utime(file_path, ns=(mtime_ns, mtime_ns))
                    self.file_paths.append(file_path)
            self.file_paths.sort(
                key=lambda path: self.sort(path.relative_to(self._dir_path).as_posix()),
                reverse=self.reverse,
            )
        except BaseException:
            self.close()
            raise

    def __enter__(self) -> Self:
        """Return this source for deterministic temporary file cleanup.

        Returns:
            this open source
        Raises:
            ValueError: if this source is already closed
        """
        if self._closed:
            raise ValueError("Cannot enter a closed ZIP source.")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ):
        """Remove temporary files without suppressing processing exceptions.

        Arguments:
            exc_type: active exception type, if any
            exc_value: active exception, if any
            traceback: active traceback, if any
        """
        self.close()

    def __next__(self) -> PipeImage:
        """Yield the next image without decoding it.

        Returns:
            image backed by an extracted file
        Raises:
            StopIteration: when closed or no selected members remain
        """
        if self._closed or self.index >= len(self.file_paths):
            raise StopIteration
        file_path = self.file_paths[self.index]
        self.index += 1
        return PipeImage(
            path=file_path,
            location_path=file_path.parent.relative_to(self._dir_path),
            detach_file=True,
        )

    def __repr__(self) -> str:
        """Describe the source configuration.

        Returns:
            source configuration
        """
        return (
            f"{self.__class__.__name__}(input_path={self.input_path!r}, "
            f"exclusions={self.exclusions!r}, inclusions={self.inclusions!r}, "
            f"sort={self.sort!r}, reverse={self.reverse!r})"
        )

    def close(self):
        """Remove temporary files once and permanently stop iteration.

        Raises:
            OSError: if temporary files cannot be removed
        """
        if not self._closed:
            self._closed = True
            self._stack.close()
