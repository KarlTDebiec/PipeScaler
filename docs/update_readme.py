#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Updates README."""
import re
from inspect import getfile
from pathlib import Path, PurePosixPath
from types import ModuleType
from typing import Type

from pipescaler.common import package_root
from pipescaler.core.image import Operator
from pipescaler.core.pipelines import Source, Terminus
from pipescaler.core.pipelines.sorter import Sorter
from pipescaler.image import mergers, processors, splitters
from pipescaler.pipelines import sorters, sources, termini


def get_github_link(cls: Type[Operator]) -> str:
    """Get the GitHub master branch link to the file containing a class.

    Arguments:
        cls: Class for which to get link
    Returns:
        GitHub link
    """
    return "https://github.com/KarlTDebiec/PipeScaler/tree/master/" + str(
        PurePosixPath(Path(getfile(cls)).relative_to(package_root.parent))
    )


def get_module_regexes(modules: list[ModuleType]) -> dict[ModuleType, re.Pattern]:
    """Get regular expressions to identify README sections for provided modules.

    Arguments:
        modules: Modules for which to generate regexes
    Returns:
        Dictionary of modules to their regexes
    """
    module_regexes = {}
    for module in modules:
        module_name = module.__name__.split(".")[-1]
        module_regex = re.compile(
            r"[\S\s]*"
            r"(?P<header>^.*" + module_name + r":$)"
            r"\n"
            r"(?P<body>(^\*\s.*$\n)+)"
            r"[\S\s]*",
            re.MULTILINE,
        )
        module_regexes[module] = module_regex
    return module_regexes


def get_stage_description(stage: Type[Operator]) -> str:
    """Get the formatted description of a stage, including GitHub link.

    Uses the first block of lines in the Stage's docstring.

    Arguments:
        stage: Stage for which to get formatted description
    Returns:
        Formatted description of stage
    """
    return f"* [{stage.__name__}]({get_github_link(stage)}) - {stage.help_markdown()}\n"


def get_stage_descriptions(module: ModuleType) -> str:
    """Get the descriptions of stages within a module.

    Arguments:
        module: Module for which to get stage descriptions
    Returns:
        Formatted descriptions of stages
    """
    section = ""
    for stage in map(module.__dict__.get, module.__all__):
        if stage and issubclass(stage, (Operator, Source, Sorter, Terminus)):
            section += get_stage_description(stage)
    return section


if __name__ == "__main__":
    # Read README
    readme_path = package_root.parent / "README.md"
    with open(readme_path, "r", encoding="utf-8") as readme_file:
        readme = readme_file.read()

    # Update README
    module_regexes = get_module_regexes(
        [processors, splitters, mergers, sources, sorters, termini]
    )
    for module, module_regex in module_regexes.items():
        match = module_regex.match(readme)
        if match:
            body = match["body"]
            readme = readme.replace(body, get_stage_descriptions(module))

    # Write README
    with open(package_root.parent / "README.md", "w", encoding="utf-8") as readme_file:
        readme_file.write(readme)
