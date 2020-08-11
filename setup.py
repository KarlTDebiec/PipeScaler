#!/usr/bin/env python
#   setup.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from os import walk
from os.path import join
from typing import List

from setuptools import find_packages, setup


################################## FUNCTIONS ##################################
def get_package_data(directory: str) -> List[str]:
    paths = []
    for (path, directories, filenames) in walk(directory):
        for filename in filenames:
            paths.append(join("..", path, filename))
    return paths


#################################### MAIN #####################################
setup(
    name="pipescaler",
    version="0.1",
    include_package_data=True,
    package_data={
        "pipescaler": get_package_data("pipescaler/data")},
    packages=find_packages(),
    scripts=[
        "pipescaler/PipeScaler.py",
        "pipescaler/tools/ScaledImageIdentifier.py",
    ])
