#!/usr/bin/env python
#   pipescaler/processors/source.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from abc import ABC, abstractmethod
from os import listdir
from typing import Any, Iterator, List, Optional, Union

from pipescaler.common import validate_input_path
from pipescaler.core import PipeImage
from pipescaler.core.pipeline import Pipeline
from pipescaler.core.stage import Stage


####################################### CLASSES ########################################
class Source(ABC):

    # region Builtins

    def __init__(
        self,
        pipeline: Pipeline,
        directory: str,
        downstream_stages: Optional[Union[List[str], str]] = None,
        **kwargs: Any,
    ) -> None:
        self._pipeline = pipeline
        self.directory = directory
        if isinstance(downstream_stages, str):
            downstream_stages = [downstream_stages]
        self._downstream_stages = downstream_stages

        # Prepare description
        desc = f"source {self.__class__.__name__} ({self.directory})"
        if self.downstream_stages is not None:
            if len(self.downstream_stages) >= 2:
                for stage in self.downstream_stages[:-1]:
                    desc += f"\n ├─ {stage}:"
            desc += f"\n └─ {self.downstream_stages[-1]}"
        self._desc = desc

    def __call__(self, **kwargs: Any) -> Iterator[str]:
        while True:
            image: PipeImage = (yield)
            print(f"{self} processing {image.name}")
            if self.downstream_stages is not None:
                for stage in self.downstream_stages:
                    try:
                        self.pipeline.stages[stage].send(image)
                    except KeyError:
                        raise ValueError(
                            f"Downstream stage '{stage}' sought by '{self}' does not "
                            f"exist in '{self.pipeline}'"
                        )

    def __iter__(self):
        for i, infile in enumerate(self.infiles):
            image = PipeImage(infile)
            if self.pipeline.verbosity >= 1:
                print(f"{self} yielding: {image.name} ({i}/{len(self.infiles)})")
            yield image

    def __repr__(self) -> str:
        return self.desc

    def __str__(self) -> str:
        return self.name

    # endregion

    # region Properties

    @property
    def desc(self) -> str:
        """str: Description"""
        if not hasattr(self, "_desc"):
            self._desc = self.name
        return self._desc

    @property
    def downstream_stages(self) -> Optional[List[Stage]]:
        """Optional[List[Stage]]: Downstream pipes"""
        return self._downstream_stages

    @property
    def directory(self) -> str:
        """str: Input directory"""
        return self._directory

    @directory.setter
    def directory(self, value: str) -> None:
        self._directory = validate_input_path(value, file_ok=False, directory_ok=True)

    @property
    def infiles(self) -> List[str]:
        """List[str]: Input files"""
        if not hasattr(self, "_infiles"):
            self._infiles = [
                validate_input_path(f, default_directory=self.directory)
                for f in listdir(self.directory)
                if f != ".DS_Store"
            ]
            self._infiles.sort(key=self.sort)
        return self._infiles

    @property
    def name(self) -> str:
        """str: Name"""
        if not hasattr(self, "_name"):
            self._name = self.__class__.__name__
        return self._name

    @property
    def pipeline(self) -> Pipeline:
        """Pipeline: Pipeline"""
        return self._pipeline

    # endregion

    # region Static Methods

    @staticmethod
    @abstractmethod
    def sort(filename):
        raise NotImplementedError()

    # endregion
