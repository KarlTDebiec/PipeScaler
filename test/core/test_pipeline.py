#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for Pipeline"""
from os import environ
from tempfile import TemporaryDirectory
from typing import Any, Union

import pytest
import yaml

from pipescaler.core import Pipeline
from pipescaler.testing import get_sub_directory


@pytest.fixture()
def stages():
    return yaml.load(
        """
source:
    DirectorySource:
        directory: $INPUT_DIRECTORY
mode-sorter:
    ModeSorter:
alpha-splitter:
    AlphaSplitter:
alpha-merger:
    AlphaMerger:
xbrz-2:
    XbrzProcessor:
        scale: 2
copy-final:
    CopyFileTerminus:
        directory: $OUTPUT_DIRECTORY
        purge: False
""",
        Loader=yaml.SafeLoader,
    )


@pytest.fixture()
def pipeline():
    return yaml.load(
        """
- source
- mode-sorter:
    l:
        - xbrz-2
    la:
        - alpha-splitter:
            alpha:
                - xbrz-2
                - alpha-merger: alpha
            color:
                - xbrz-2
                - alpha-merger: color
        - alpha-merger
    rgb:
        - xbrz-2
    rgba:
        - alpha-splitter:
            alpha:
                - xbrz-2
                - alpha-merger: alpha
            color:
                - xbrz-2
                - alpha-merger: color
        - alpha-merger
- copy-final
""",
        Loader=yaml.SafeLoader,
    )


def test_pipeline(
    stages: dict[str, dict[str, dict[str, Any]]],
    pipeline: list[Union[str, dict[str, Any]]],
):
    with TemporaryDirectory() as wip_directory, TemporaryDirectory() as output_directory:
        environ["INPUT_DIRECTORY"] = get_sub_directory("basic")
        environ["OUTPUT_DIRECTORY"] = output_directory
        pipeline = Pipeline(
            wip_directory=wip_directory,
            stages=stages,
            pipeline=pipeline,
            purge_wip=True,
        )
        pipeline()
