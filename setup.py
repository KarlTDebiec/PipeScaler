#!python

from setuptools import setup, find_packages

setup(
    name="lauhseuisin",
    version="0.1",
    include_package_data=True,
    package_data={"lauhseuisin": ["data/*", "data/*/*"]},
    packages=find_packages())
