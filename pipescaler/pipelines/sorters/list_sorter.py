#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Sorts objects based on location/name using a set of configured lists."""
from __future__ import annotations

from collections.abc import Iterable
from logging import info
from pathlib import Path

from pipescaler.common.typing import PathLike
from pipescaler.core.pipelines import PipeObject
from pipescaler.core.pipelines.sorter import Sorter


class ListSorter(Sorter):
    """Sorts objects based on location/name using a set of configured lists."""

    exclusions = {".DS_Store", "Thumbs", "desktop"}
    """File stems to exclude"""

    def __init__(self, **outlets: PathLike | list[PathLike]) -> None:
        """Validate configuration and initialize.

        Arguments:
            **outlets: Outlets to which images may be sorted; keys are outlet names
              and values are paths to directories or text files; if path is to a
              directory, images with names matching the files within that directory will
              be sorted to that outlet; if path is to a text file, images with names
              matching a line in the file will be sorted to that outlet
        """
        self._outlets = tuple(sorted(outlets.keys()))
        self.outlets_by_filename = {}

        for outlet, paths in outlets.items():
            path_seq = paths if isinstance(paths, list) else [paths]
            for outlet_path in path_seq:
                if isinstance(outlet_path, Path):
                    path_obj = outlet_path
                else:
                    path_obj = Path(outlet_path)
                path_obj = path_obj.absolute().resolve()
                if path_obj.exists():
                    names: Iterable[str] = []
                    if path_obj.is_file():
                        with open(path_obj, encoding="utf8") as infile:
                            names = (
                                line.strip()
                                for line in infile.readlines()
                                if not line.startswith("#")
                            )
                    elif path_obj.is_dir():
                        names = (f.stem for f in path_obj.iterdir() if f.is_file())
                    for name in names:
                        if name in self.exclusions:
                            continue
                        self.outlets_by_filename[name] = outlet

    def __call__(self, pipe_object: PipeObject) -> str | None:
        """Get the outlet to which an object should be sorted.

        Arguments:
            pipe_object: Object to sort
        Returns:
            Outlet to which object should be sorted
        """
        outlet = self.outlets_by_filename.get(pipe_object.name, None)

        if outlet:
            info(f"{self}: '{pipe_object.location_name}' matches '{outlet}'")
        else:
            info(f"{self}: '{pipe_object.location_name}' does not match any outlet")
        return outlet

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets to which objects may be sorted."""
        return self._outlets
