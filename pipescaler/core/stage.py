#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for stages."""
from __future__ import annotations

from abc import ABC, abstractmethod
from importlib.util import module_from_spec, spec_from_file_location
from inspect import cleandoc

from PIL import Image

from pipescaler.common import validate_input_path


def initialize_stage(stage_name, stage_conf, modules):
    """Import and initialize a stage.

    Arguments:
        stage_name: Name with which to initialize stage
        stage_conf: Configuration with which to initialize stage
        modules: Modules from which stage may be imported
    Returns:
        Initialized stage
    """
    # Get stage's class name
    stage_cls_name = next(iter(stage_conf))

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

    @abstractmethod
    def __call__(self, input_image: Image.Image) -> tuple[Image.Image, ...]:
        raise NotImplementedError()

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        if cls.__doc__:
            return cleandoc(cls.__doc__).split(". ", maxsplit=1)[0]
        return ""

    @classmethod
    @property
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        raise NotImplementedError()

    @classmethod
    @property
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        raise NotImplementedError()
