#!/usr/bin/env python
#   pipescaler/core/source.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
####################################### MODULES ########################################
from __future__ import annotations

from abc import ABC, abstractmethod
from os import listdir
from typing import Any, Generator, List, Optional, Union

from pipescaler.common import validate_input_path, validate_output_path
from pipescaler.core import PipeImage
from pipescaler.core.pipeline import Pipeline


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

        # Prepare attributes
        self.pipeline = pipeline
        self.directory = validate_output_path(
            directory, file_ok=False, directory_ok=True
        )
        if isinstance(downstream_stages, str):
            downstream_stages = [downstream_stages]
        self.downstream_stages = downstream_stages
        self.infiles = [
            validate_input_path(f, default_directory=self.directory)
            for f in listdir(self.directory)
            if f != ".DS_Store"
        ]
        self.infiles.sort(key=self.sort)

        # Prepare name and description
        self.name = self.__class__.__name__.lower()
        desc = f"source {self.__class__.__name__} ({self.directory})"
        if self.downstream_stages is not None:
            if len(self.downstream_stages) >= 2:
                for stage in self.downstream_stages[:-1]:
                    desc += f"\n ├─ {stage}"
            desc += f"\n └─ {self.downstream_stages[-1]}"
        self.desc = desc

    def __call__(self, **kwargs: Any) -> Generator[PipeImage, PipeImage, None]:
        while True:
            image = yield
            if self.pipeline.verbosity >= 2:
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

    # region Static Methods

    @staticmethod
    @abstractmethod
    def sort(filename):
        raise NotImplementedError()

    # endregion
