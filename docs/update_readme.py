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

from IPython import embed

from pipescaler import mergers, processors, sorters, sources, splitters, termini
from pipescaler.common import package_root, validate_input_path


def get_github_link(cls):
    return "/".join(
        ["https://github.com/KarlTDebiec/PipeScaler/tree/master"]
        + list(Path(getfile(cls)).parts[len(Path(package_root).parts) - 1 :])
    )


def get_stage_descriptions(module):
    section = ""
    for processor in map(module.__dict__.get, module.__all__):
        name = processor.__name__
        link = get_github_link(processor)
        doc = processor.__doc__
        if doc is None:
            section += f"* [{name}]({link})\n"
        else:
            doc_lines = cleandoc(processor.__doc__).split("\n")
            try:
                doc_head = " ".join(line for line in doc_lines[: doc_lines.index("")])
            except ValueError:
                doc_head = " ".join(line for line in doc_lines)
            section += f"* [{name}]({link}) - {doc_head}\n"
    return section


if __name__ == "__main__":
    modules = {}
    for module in [mergers, processors, sorters, sources, splitters, termini]:
        module_name = splitext(module.__name__)[-1].lstrip(".")
        regex = re.compile(r"(startText)(.+)((?:\n.+)+)(endText)", re.MULTILINE)
        modules[regex] = module

    readme_filename = validate_input_path(join(dirname(package_root), "README.md"))
    with open(readme_filename, "r") as readme:
        current_section = None
        for line in readme.readlines():
            if current_section is None:
                print(line.rstrip())
                for module_re, module in modules.items():
                    if module_re.match(line.rstrip()):
                        current_section = splitext(module.__name__)[-1].lstrip(".")
                        section = get_stage_descriptions(module)
                        break
            elif line.startswith("*"):
                continue
            elif line.rstrip() == "":
                print(section)
                current_section = None
            else:
                embed()
