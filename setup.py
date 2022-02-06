#!/usr/bin/env python
#   setup.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
""""""
from os import walk
from os.path import join
from typing import List

from setuptools import find_packages, setup


def get_package_data(directory: str) -> List[str]:
    paths = []
    for (path, directories, filenames) in walk(directory):
        for filename in filenames:
            paths.append(join("..", path, filename))
    return paths


def get_scripts(directory: str) -> List[str]:
    paths = []
    for (path, directories, filenames) in walk(directory):
        for filename in [f for f in filenames if f.endswith(".py")]:
            paths.append(join(directory, filename))
        print(path, directories, filenames)
    return paths


setup(
    name="pipescaler",
    version="0.1",
    include_package_data=True,
    package_data={"pipescaler": get_package_data(join("pipescaler", "data"))},
    packages=find_packages(),
    scripts=get_scripts(join("pipescaler", "scripts")),
)
