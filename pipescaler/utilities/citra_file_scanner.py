#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Citra-specific file scanner."""

from __future__ import annotations

from pathlib import Path
from re import Match, compile

from .file_scanner import FileScanner


class CitraFileScanner(FileScanner):
    """Scans Citra texture dump directories."""

    _mip_regex = compile(r"^(?P<base>.+)_mip(?P<level>\d+)$")

    def __call__(self):
        """Perform operations."""
        self.input_names: set[str] = set()
        for input_dir_path in self.input_dir_paths:
            self.input_names.update(
                file_path.stem for file_path in input_dir_path.iterdir()
            )

        super().__call__()

    @classmethod
    def get_mip_match(cls, name: str) -> Match[str] | None:
        """Get mip suffix match for filename stem.

        Arguments:
            name: filename stem
        Returns:
            mip suffix match, if present
        """
        return cls._mip_regex.match(name)

    @classmethod
    def strip_mip0_suffix(cls, name: str) -> str:
        """Remove _mip0 suffix from a stem or filename, if present.

        Arguments:
            name: filename stem or full filename
        Returns:
            name with trailing _mip0 removed before extension, if present
        """
        suffix = "_mip0"
        stem = Path(name).stem
        extension = Path(name).suffix
        if stem.endswith(suffix):
            stem = stem.removesuffix(suffix)
            return f"{stem}{extension}"
        return name

    def get_operation(self, name: str) -> str:
        """Select operation for filename.

        Arguments:
            name: name of file
        Returns:
            operation to perform
        """
        mip_match = self.get_mip_match(name)

        if mip_match is None:
            if any(mip_name.startswith(f"{name}_mip") for mip_name in self.input_names):
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
        return self.strip_mip0_suffix(output_name)
