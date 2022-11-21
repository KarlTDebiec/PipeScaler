#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for CheckpointManager."""
from os import mkdir
from pathlib import Path
from tempfile import TemporaryDirectory

from pytest import fixture

from pipescaler.core.pipelines import (
    PipeImage,
    wrap_merger,
    wrap_processor,
    wrap_splitter,
)
from pipescaler.core.types import PipeMerger, PipeProcessor, PipeSplitter
from pipescaler.image.mergers import AlphaMerger
from pipescaler.image.processors import XbrzProcessor
from pipescaler.image.splitters import AlphaSplitter
from pipescaler.pipelines import CheckpointManager
from pipescaler.testing import get_test_infile_path


@fixture
def merge_alpha() -> PipeMerger:
    return wrap_merger(AlphaMerger())


@fixture
def split_alpha() -> PipeSplitter:
    return wrap_splitter(AlphaSplitter())


@fixture
def process_xbrz() -> PipeProcessor:
    return wrap_processor(XbrzProcessor())


def test_post_processor(process_xbrz) -> None:
    with TemporaryDirectory() as cp_directory:
        cp_directory = Path(cp_directory)
        cp_manager = CheckpointManager(cp_directory)

        @cp_manager.post_processor("checkpoint.png")
        def function(image: PipeImage) -> PipeImage:
            image = process_xbrz(image)
            return image

        input_image = PipeImage(path=get_test_infile_path("RGB"))
        output_image = function(input_image)
        assert output_image.path == (cp_directory / input_image.name / "checkpoint.png")
        assert output_image._image is not None

        output_image = function(input_image)
        assert output_image.path == (cp_directory / input_image.name / "checkpoint.png")
        assert output_image._image is None

        # touch an empty file
        mkdir(cp_directory / "to_delete")
        open(cp_directory / input_image.name / "to_delete.png", "a").close()

        cp_manager.purge_unrecognized_files()


def test_post_file_processor() -> None:
    pass


def test_post_splitter() -> None:
    pass


def test_pre_processor() -> None:
    pass


def test_purge_unrecognized_files() -> None:
    pass
