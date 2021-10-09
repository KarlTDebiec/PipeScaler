#!/usr/bin/env python
#   pipescaler/core/stage.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from __future__ import annotations

from abc import ABC, abstractmethod
from importlib.util import module_from_spec, spec_from_file_location
from typing import Any, List, Optional

from pipescaler.common import validate_input_path


def initialize_stage(stage_name, stage_conf, modules):
    # Get stage's class name
    stage_cls_name = next(iter(stage_conf))  # get first key

    # Get stage's configuration
    stage_args = stage_conf.get(stage_cls_name)
    if stage_args is None:
        stage_args = {}

    # Get stage's class
    stage_cls = None
    for module in modules:
        try:
            stage_cls = getattr(module, stage_cls_name)
        except AttributeError:
            continue
    if stage_cls is None:
        if "infile" in stage_args:
            module_infile = validate_input_path(stage_args.pop("infile"))
            spec = spec_from_file_location(stage_cls_name, module_infile)
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            stage_cls = getattr(module, stage_cls_name)
        else:
            raise KeyError(f"Class '{stage_cls_name}' not found")

    return stage_cls(name=stage_name, **stage_args)


class Stage(ABC):
    """Base class for stages."""

    trim_suffixes = None
    extension = "png"

    def __init__(
        self, name: Optional[str] = None, desc: Optional[str] = None, **kwargs: Any
    ) -> None:
        """
        Validates and stores static configuration.

        Arguments:
            name (Optional[str]): Name of stage
            desc (Optional[str]): Description of stage
            kwargs (Any): Additional keyword arguments
        """
        if name is not None:
            self.name = name
        else:
            self.name = self.__class__.__name__
        if desc is not None:
            self.desc = desc
        else:
            self.desc = self.name

    def __repr__(self) -> str:
        return self.desc

    def __str__(self) -> str:
        return self.name

    @property
    @abstractmethod
    def inlets(self) -> List[str]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def outlets(self) -> List[str]:
        raise NotImplementedError()
