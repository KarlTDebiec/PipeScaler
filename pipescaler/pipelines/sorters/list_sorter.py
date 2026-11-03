#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Sorts objects based on location/name using a set of configured lists."""

from __future__ import annotations

from collections.abc import Iterable
from logging import info, warning
from pathlib import Path

from pipescaler.core.pipelines import PipeObject
from pipescaler.core.pipelines.sorter import Sorter

__all__ = ["ListSorter"]


class ListSorter(Sorter):
    """Sorts objects based on location/name using a set of configured lists."""

    exclusions = {".DS_Store", "Thumbs", "desktop"}
    """File stems to exclude"""

    def __init__(
        self,
        *,
        allow_duplicates: bool = False,
        **outlet_paths_by_name: Path | str | list[Path | str],
    ):
        """Validate configuration and initialize.

        Arguments:
            allow_duplicates: whether to allow names assigned to multiple outlets;
              defaults to False; when True, log a warning and use the last configured
              outlet for each conflicting name; repetitions within one outlet are
              always allowed
            **outlet_paths_by_name: outlets to which images may be sorted; keys are
              outlet names and values are paths to directories or text files; if path is
              to a directory, images with names matching the files within that directory
              will be sorted to that outlet; if path is to a text file, images with
              names matching a line in the file will be sorted to that outlet;
              blank lines and excluded file stems are ignored
        Raises:
            ValueError: if a name is assigned to multiple outlets and allow_duplicates
              is False
        """
        self.allow_duplicates = allow_duplicates
        self._outlets = tuple(sorted(outlet_paths_by_name.keys()))
        self._input_paths_by_outlet: dict[str, list[str]] = {}
        self.outlets_by_filename: dict[str, str] = {}
        conflicting_outlets_by_name: dict[str, set[str]] = {}

        for outlet, configured_paths in outlet_paths_by_name.items():
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
                        if not name or name in self.exclusions:
                            continue
                        previous_outlet = self.outlets_by_filename.get(name)
                        if previous_outlet is not None and previous_outlet != outlet:
                            conflicting_outlets_by_name.setdefault(
                                name, {previous_outlet}
                            ).add(outlet)
                        self.outlets_by_filename[name] = outlet

        if conflicting_outlets_by_name:
            conflicts = "; ".join(
                f"{name!r}: {', '.join(repr(outlet) for outlet in sorted(outlets))}"
                for name, outlets in sorted(conflicting_outlets_by_name.items())
            )
            message = f"{self}: names assigned to multiple outlets: {conflicts}"
            if not self.allow_duplicates:
                raise ValueError(message)
            warning(f"{message}; last configured outlet wins")

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
        """Representation.

        Returns:
            string representation of this object
        """
        return (
            f"{self.__class__.__name__}(allow_duplicates={self.allow_duplicates!r}, "
            f"**{self._input_paths_by_outlet!r})"
        )

    @property
    def outlets(self) -> tuple[str, ...]:
        """Outlets to which objects may be sorted."""
        return self._outlets
