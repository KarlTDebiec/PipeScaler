#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Scans Citra dump directories for new files."""

from __future__ import annotations

from logging import debug, info
from os import remove
from pathlib import Path
from re import compile

from .file_scanner import FileScanner


class CitraFileScanner(FileScanner):
    """Scans Citra dump directories for new files."""

    _mip_regex = compile(r"^(?P<base>.+)_mip(?P<level>\d+)$")

    def __call__(self):
        """Perform operations."""
        self.clean_project_root()

        # Populate mapping from base name of input file to full path to
        # This is uses for Citra-specific cleanup of mipmap files
        self.input_names: set[str] = set()
        for input_dir_path in self.input_dir_paths:
            self.input_names.update(
                file_path.stem for file_path in input_dir_path.iterdir()
            )
        self.reviewed_paths_by_base_name = self.get_reviewed_paths_by_base_name()

        for input_dir_path in self.input_dir_paths:
            for file_path in input_dir_path.iterdir():
                self.perform_operation(file_path)

    def get_operation(self, name: str) -> str:
        """Select operation for filename.

        Arguments:
            name: name of file
        Returns:
            operation to perform
        """
        mip_match = self._mip_regex.match(name)

        if mip_match is None:
            normalized_name = self.get_normalized_name(name)
            if any(
                self.get_normalized_name(mip_name).startswith(f"{normalized_name}_mip")
                for mip_name in self.input_names
            ):
                return "remove"
            return super().get_operation(name)

        mip_level = int(mip_match.group("level"))
        base_name = mip_match.group("base")
        if mip_level > 0:
            return "ignore"
        return super().get_operation(base_name)

    def get_output_name(self, file_path: Path) -> str:
        """Get output filename for a file.

        Arguments:
            file_path: path to source file
        Returns:
            output filename
        """
        output_name = super().get_output_name(file_path)
        mip_match = self._mip_regex.match(Path(output_name).stem)
        if mip_match and int(mip_match.group("level")) == 0:
            return f"{mip_match.group('base')}{Path(output_name).suffix}"
        return output_name

    def get_reviewed_paths_by_base_name(self) -> dict[str, list[Path]]:
        """Build index of reviewed file paths by base filename stem.

        Returns:
            reviewed file paths keyed by base filename stem
        """
        reviewed_paths_by_base_name: dict[str, list[Path]] = {}
        if not self.reviewed_dir_path:
            return reviewed_paths_by_base_name

        if isinstance(self.reviewed_dir_path, Path):
            reviewed_dir_paths = [self.reviewed_dir_path]
        else:
            reviewed_dir_paths = self.reviewed_dir_path

        for reviewed_dir_path in reviewed_dir_paths:
            for reviewed_path in reviewed_dir_path.iterdir():
                mip_match = self._mip_regex.match(reviewed_path.stem)
                base_stem = (
                    mip_match.group("base")
                    if mip_match is not None
                    else reviewed_path.stem
                )
                base_name = self.get_normalized_name(base_stem)
                reviewed_paths_by_base_name.setdefault(base_name, []).append(
                    reviewed_path
                )

        return reviewed_paths_by_base_name

    def perform_operation(self, file_path: Path):
        """Perform operations for filename.

        Arguments:
            file_path: path to file
        """
        if not file_path.exists():
            debug(f"'{file_path.stem}' missing")
            return

        mip_match = self._mip_regex.match(file_path.stem)
        if mip_match is not None and int(mip_match.group("level")) > 0:
            self.remove_reviewed_paths_for_mip(file_path)
            debug(f"'{file_path.stem}' ignored")
            return

        super().perform_operation(file_path)

    def remove(self, file_path: Path):
        """Remove file and analogous mip variants from input directory.

        Arguments:
            file_path: path to file to remove
        """
        super().remove(file_path)

        mip_match = self._mip_regex.match(file_path.stem)
        base_name = mip_match.group("base") if mip_match else file_path.stem
        for input_dir_path in self.input_dir_paths:
            for match in input_dir_path.glob(f"{base_name}_mip*.*"):
                mip_suffix = self._mip_regex.match(match.stem)
                if mip_suffix is None:
                    continue
                if match.exists():
                    remove(match)
                    info(f"'{match.stem}' removed")

    def remove_reviewed_paths_for_mip(self, file_path: Path):
        """Remove reviewed files corresponding to a nonzero mip file.

        Arguments:
            file_path: input path that may be a nonzero mip
        """
        mip_match = self._mip_regex.match(file_path.stem)
        if mip_match is None:
            return

        mip_level = int(mip_match.group("level"))
        if mip_level == 0:
            return

        base_name = self.get_normalized_name(mip_match.group("base"))
        input_names: set[str] = getattr(self, "input_names", set())
        if any(
            self.get_normalized_name(name) == f"{base_name}_mip0"
            for name in input_names
        ):
            return

        for reviewed_path in self.reviewed_paths_by_base_name.pop(base_name, []):
            if reviewed_path.exists():
                remove(reviewed_path)
                info(f"'{reviewed_path}' removed")
        self.reviewed_names.discard(base_name)
