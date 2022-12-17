#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Object within a pipeline."""
from __future__ import annotations

from abc import ABC
from pathlib import Path
from typing import Optional, Sequence, Union

from pipescaler.common import PathLike, validate_input_file


class PipeObject(ABC):
    """Object within a pipeline."""

    def __init__(
        self,
        *,
        path: Optional[Path] = None,
        name: Optional[str] = None,
        parents: Optional[Union[PipeObject, Sequence[PipeObject]]] = None,
        location: Optional[Path] = None,
    ) -> None:
        """Initialize.

        Arguments:
            path: Path to object file
            name: Name of object; if not provided will name of first parent object, and
              if that is not available will use filename of path excluding extension;
              one of these must be available
            parents: Parent object(s) from which this object is descended
            location: Path relative to parent directory
        """
        self.path = path

        if parents is not None:
            if isinstance(parents, PipeObject):
                parents = [parents]
            if not isinstance(parents, list):
                parents = list(parents)
        self._parents = parents

        if name is not None:
            self._name = name
        elif self.parents is not None:
            self._name = self.parents[0].name
        elif self.path is not None:
            self._name = self.path.stem
        else:
            raise ValueError(
                f"{self.__class__.__name__} requires either a name, the path to a file "
                f"whose name will be used, or a parent object whose name will be used."
            )

        if location is not None:
            self._location: Optional[Path] = location
        elif self.parents is not None:
            self._location = self.parents[0].location
        else:
            self._location = None

    def __str__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__} '{self.location_name}'>"

    def count_parents(self) -> int:
        """Count number of parents of this object."""
        if self.parents is not None:
            return len(self.parents) + sum(p.count_parents() for p in self.parents)
        return 0

    @property
    def location_name(self) -> str:
        """Location relative to root directory and name."""
        if self.location is not None:
            return str(self.location / self.name)
        return self.name

    @property
    def location(self) -> Optional[Path]:
        """Location relative to root directory."""
        return self._location

    @property
    def parents(self) -> Optional[list[PipeObject]]:
        """Parent objects of this object."""
        return self._parents

    @property
    def path(self) -> Optional[Path]:
        """Path to this object, if applicable."""
        return self._path

    @path.setter
    def path(self, value: Optional[PathLike]) -> None:
        if value is not None:
            value = validate_input_file(value)
        self._path = value

    @property
    def name(self) -> str:
        """Name of this object."""
        return self._name
