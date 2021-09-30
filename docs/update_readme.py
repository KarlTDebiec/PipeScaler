#!/usr/bin/env python
#   update_readme.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Updates readme."""
import re
from inspect import cleandoc, getfile
from os.path import dirname, join, splitext
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Type

from pipescaler import mergers, processors, sorters, sources, splitters, termini
from pipescaler.common import package_root, validate_input_path
from pipescaler.core import Stage


def get_github_link(cls: Type) -> str:
    """
    Gets the GitHub master branch link to the file containing a class

    Args:
        cls: Class for which to get link

    Returns:
        GitHub link
    """
    return "/".join(
        ["https://github.com/KarlTDebiec/PipeScaler/tree/master"]
        + list(Path(getfile(cls)).parts[len(Path(package_root).parts) - 1 :])
    )


def get_module_regexes(modules: List[ModuleType]) -> Dict[ModuleType, re.Pattern]:
    """
    Gets regular expressions to identify README sections for provided modules

    Args:
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


def get_stage_description(stage: Stage) -> str:
    """
    Gets the formatted description of a stage, including GitHub link

    Uses the first block of lines in the Stage's docstring

    Args:
        stage: Stage for which to get formatted description

    Returns:
        Formatted description of stage
    """
    name = stage.__name__
    link = get_github_link(stage)
    doc = stage.__doc__
    if doc is None:
        return f"* [{name}]({link})\n"
    else:
        doc_lines = cleandoc(stage.__doc__).split("\n")
        try:
            doc_head = " ".join(line for line in doc_lines[: doc_lines.index("")])
        except ValueError:
            doc_head = " ".join(line for line in doc_lines)
        return f"* [{name}]({link}) - {doc_head}\n"


def get_stage_descriptions(module: ModuleType) -> str:
    """
    Gets the descriptions of stages within a module

    Args:
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
