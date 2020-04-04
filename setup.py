#!python
from os import walk
from os.path import join

from setuptools import setup, find_packages


def get_package_data(directory):
    paths = []
    for (path, directories, filenames) in walk(directory):
        for filename in filenames:
            paths.append(join("..", path, filename))
    return paths


setup(
    name="lauhseuisin",
    version="0.1",
    include_package_data=True,
    package_data={"lauhseuisin": get_package_data("lauhseuisin/data")},
    packages=find_packages(),
    scripts=["lauhseuisin/LauhSeuiSin.py"])
