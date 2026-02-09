#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Sorts objects based on location/name using a set of configured lists."""

from __future__ import annotations

from collections.abc import Iterable
from logging import info
from pathlib import Path

from pipescaler.core.pipelines import PipeObject
from pipescaler.core.pipelines.sorter import Sorter


class ListSorter(Sorter):
    """Sorts objects based on location/name using a set of configured lists."""

    exclusions = {".DS_Store", "Thumbs", "desktop"}
    """File stems to exclude"""

    def __init__(self, **outlets: Path | str | list[Path | str]):
        """Validate configuration and initialize.

        Arguments:
            **outlets: Outlets to which images may be sorted; keys are outlet names
              and values are paths to directories or text files; if path is to a
              directory, images with names matching the files within that directory will
              be sorted to that outlet; if path is to a text file, images with names
              matching a line in the file will be sorted to that outlet
        """
        self._outlets = tuple(sorted(outlets.keys()))
        self._input_paths_by_outlet: dict[str, list[str]] = {}
        self.outlets_by_filename = {}

        for outlet, configured_paths in outlets.items():
            path_values = configured_paths
            if not isinstance(path_values, list):
                path_values = [path_values]
            self._input_paths_by_outlet[outlet] = []

            for configured_path in path_values:
                path_object = configured_path
                if not isinstance(path_object, Path):
                    path_object = Path(path_object)
                resolved_path = path_object.resolve()
                self._input_paths_by_outlet[outlet].append(str(resolved_path))
                if resolved_path.exists():
                    names: Iterable[str] = []
                    if resolved_path.is_file():
                        with open(resolved_path, encoding="utf8") as input_file:
                            names = (
                                line.strip()
                                for line in input_file.readlines()
                                if not line.startswith("#")
                            )
                    elif resolved_path.is_dir():
                        names = (f.stem for f in resolved_path.iterdir() if f.is_file())
                    for name in names:
                        if name in self.exclusions:
                            continue
                        self.outlets_by_filename[name] = outlet

    def __call__(self, obj: PipeObject) -> str | None:
        """Get the outlet to which an object should be sorted.

        Arguments:
            obj: Object to sort
        Returns:
            Outlet to which object should be sorted
        """
        outlet = self.outlets_by_filename.get(obj.name, None)

        if outlet:
            info(f"{self}: '{obj.location_name}' matches '{outlet}'")
        else:
            info(f"{self}: '{obj.location_name}' does not match any outlet")
        return outlet

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(**{self._input_paths_by_outlet!r})"

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets to which objects may be sorted."""
        return self._outlets
