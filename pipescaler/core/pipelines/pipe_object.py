#  Copyright 2020-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for object within pipelines."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Self, Sequence

from pipescaler.common.typing import PathLike
from pipescaler.common.validation import validate_input_file


class PipeObject(ABC):
    """Abstract base class for object within pipelines."""

    def __init__(
        self,
        *,
        path: PathLike | None = None,
        name: str | None = None,
        parents: Self | Sequence[Self] | None = None,
        location: Path | None = None,
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
        self._path = None
        if path:
            self._path = validate_input_file(path)

        self._parents = None
        if parents:
            if isinstance(parents, self.__class__):
                self._parents = [parents]
            elif isinstance(parents, Sequence) and all(
                isinstance(p, self.__class__) for p in parents
            ):
                self._parents = list(parents)
            else:
                raise TypeError(
                    f"{self.__class__.__name__}'s parents must be a list of "
                    f"{self.__class__.__name__}"
                )

        if name:
            self._name = name
        elif self.parents:
            self._name = self.parents[0].name
        elif self.path:
            self._name = self.path.stem
        else:
            raise ValueError(
                f"{self.__class__.__name__} requires either a name, the path to a file "
                f"whose name will be used, or a parent object whose name will be used."
            )

        if location:
            self._location: Path | None = location
        elif self.parents:
            self._location = self.parents[0].location
        else:
            self._location = None

    def __repr__(self) -> str:
        """Representation."""
        return (
            f"{self.__class__.__name__}("
            f"path={self.path!r}, "
            f"name={self.name!r}, "
            f"parents={self.parents!r}, "
            f"location={self.location!r})"
        )

    def __str__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__} '{self.location_name}'>"

    @property
    def location_name(self) -> str:
        """Location relative to root directory and name."""
        if self.location:
            return str(self.location / self.name)
        return self.name

    @property
    def location(self) -> Path | None:
        """Location relative to root directory."""
        return self._location

    @property
    def name(self) -> str:
        """Name of this object."""
        return self._name

    @property
    def parents(self) -> list[Self] | None:
        """Parent objects of this object."""
        return self._parents

    @property
    def path(self) -> Path | None:
        """Path to this object, if applicable."""
        return self._path

    @path.setter
    def path(self, value: PathLike | None) -> None:
        if value:
            self._path = validate_input_file(value)
        else:
            self._path = None

    @abstractmethod
    def save(self, path: PathLike) -> None:
        """Save object to file and set path.

        Arguments:
            path: Path to which to save object
        """
        raise NotImplementedError()
