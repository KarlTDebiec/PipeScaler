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


def test_post_processor(process_xbrz: PipeProcessor) -> None:
    with TemporaryDirectory() as cp_directory:
        cp_directory = Path(cp_directory)
        cp_manager = CheckpointManager(cp_directory)

        @cp_manager.post_processor("checkpoint.png")
        def function(input_img: PipeImage) -> PipeImage:
            output_img = process_xbrz(input_img)
            return output_img

        input_img = PipeImage(path=get_test_infile_path("RGB"))
        output_image = function(input_img)
        assert output_image.path == (cp_directory / input_img.name / "checkpoint.png")
        assert output_image._image is not None

        output_image = function(input_img)
        assert output_image.path == (cp_directory / input_img.name / "checkpoint.png")
        assert output_image._image is None

        # touch an empty file
        mkdir(cp_directory / "to_delete")
        open(cp_directory / input_img.name / "to_delete.png", "a").close()

        cp_manager.purge_unrecognized_files()


def test_post_file_processor() -> None:
    pass


def test_post_splitter(split_alpha: PipeSplitter) -> None:
    with TemporaryDirectory() as cp_directory:
        cp_directory = Path(cp_directory)
        cp_manager = CheckpointManager(cp_directory)

        @cp_manager.post_splitter("color.png", "alpha.png")
        def function(image: PipeImage) -> tuple[PipeImage, ...]:
            color_img, alpha_img = split_alpha(image)
            return color_img, alpha_img

        input_img = PipeImage(path=get_test_infile_path("RGBA"))
        color_img, alpha_img = function(input_img)
        assert color_img.path == (cp_directory / input_img.name / "color.png")
        assert color_img._image is not None
        assert alpha_img.path == (cp_directory / input_img.name / "alpha.png")
        assert alpha_img._image is not None

        color_img, alpha_img = function(input_img)
        assert color_img.path == (cp_directory / input_img.name / "color.png")
        assert color_img._image is None
        assert alpha_img.path == (cp_directory / input_img.name / "alpha.png")
        assert alpha_img._image is None

        cp_manager.purge_unrecognized_files()


def test_pre_processor() -> None:
    pass
