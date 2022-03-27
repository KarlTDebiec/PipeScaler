#!/usr/bin/env python
#   update_readme.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Updates readme"""
import re
from inspect import getfile
from os.path import dirname, join, splitext
from pathlib import Path
from types import ModuleType
from typing import Type

from pipescaler import mergers, processors, sorters, sources, splitters, termini
from pipescaler.common import package_root, validate_input_path
from pipescaler.core import Stage


def get_github_link(cls: Type[Stage]) -> str:
    """
    Get the GitHub master branch link to the file containing a class

    Arguments:
        cls: Class for which to get link

    Returns:
        GitHub link
    """
    return "/".join(
        ["https://github.com/KarlTDebiec/PipeScaler/tree/master"]
        + list(Path(getfile(cls)).parts[len(Path(package_root).parts) - 1 :])
    )


def get_module_regexes(modules: list[ModuleType]) -> dict[ModuleType, re.Pattern]:
    """
    Get regular expressions to identify README sections for provided modules

    Arguments:
        modules: Modules for which to generate regexes

    Returns:
        Dictionary of modules to their regexes
    """
    module_regexes = {}
    for module in modules:
        module_name = splitext(module.__name__)[-1].lstrip(".")
        module_regex = re.compile(
            f"[\S\s]*(?P<header>^.*{module_name}:$)\n(?P<body>(^\*\s.*$\n)+)[\S\s]*",
            re.MULTILINE,
        )
        module_regexes[module] = module_regex
    return module_regexes


def get_stage_description(stage: Type[Stage]) -> str:
    """
    Get the formatted description of a stage, including GitHub link

    Uses the first block of lines in the Stage's docstring

    Arguments:
        stage: Stage for which to get formatted description

    Returns:
        Formatted description of stage
    """
    return f"* [{stage.__name__}]({get_github_link(stage)}) - {stage.help_markdown}\n"


def get_stage_descriptions(module: ModuleType) -> str:
    """
    Get the descriptions of stages within a module

    Arguments:
        module: Module for which to get stage descriptions

    Returns:
        Formatted descriptions of stages
    """
    section = ""
    for stage in map(module.__dict__.get, module.__all__):
        section += get_stage_description(stage)
    return section


if __name__ == "__main__":
    readme_filename = validate_input_path(join(dirname(package_root), "README.md"))

    # Read README
    with open(readme_filename, "r") as readme_file:
        readme = readme_file.read()

    # Update README
    module_regexes = get_module_regexes(
        [mergers, processors, sorters, sources, splitters, termini]
    )
    for module, module_regex in module_regexes.items():
        body = module_regex.match(readme)["body"]
        readme = readme.replace(body, get_stage_descriptions(module))

    # Write README
    with open(readme_filename, "w") as readme_file:
        readme_file.write(readme)
