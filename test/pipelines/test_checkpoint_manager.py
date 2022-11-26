#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for CheckpointManager."""
from os import mkdir

import numpy as np
import pytest

from pipescaler.common import get_temp_directory_path
from pipescaler.core.pipelines import PipeImage, PipeMerger, PipeProcessor, PipeSplitter
from pipescaler.core.pipelines.pipe_stage import PipeStage
from pipescaler.image.mergers import AlphaMerger
from pipescaler.image.processors import XbrzProcessor
from pipescaler.image.splitters import AlphaSplitter
from pipescaler.pipelines import CheckpointManager
from pipescaler.testing import get_test_infile_path

# TODO: internal_cpt should be a set
# TODO: internal_cpt tracking for PipeSplitter
# TODO: Test with heavier pipeline


@pytest.fixture
def xbrz_processor() -> PipeProcessor:
    return PipeProcessor(XbrzProcessor())


@pytest.fixture
def alpha_splitter() -> PipeSplitter:
    return PipeSplitter(AlphaSplitter())


@pytest.fixture
def alpha_merger() -> PipeMerger:
    return PipeMerger(AlphaMerger())


# def test_nested() -> None:
#     process_1 = PipeProcessor(XbrzProcessor(scale=2))
#     process_2 = PipeProcessor(XbrzProcessor(scale=2))
#     process_3 = PipeProcessor(XbrzProcessor(scale=2))
#
#     def run(cp_directory: Path) -> None:
#         cp_manager = CheckpointManager(cp_directory)
#
#         @cp_manager.pre("pre_1.png")
#         @cp_manager.post_processor("post_1.png")
#         def stage_1(img: PipeImage) -> PipeImage:
#             return process_1(img)
#
#         @cp_manager.pre("pre_2.png")
#         @cp_manager.post_processor("post_2.png", calls=(stage_1,))
#         def stage_2(img: PipeImage) -> PipeImage:
#             return process_2(stage_1(img))
#
#         @cp_manager.pre("pre_3.png")
#         @cp_manager.post_processor("post_3.png", calls=(stage_2,))
#         def stage_3(img: PipeImage) -> PipeImage:
#             return process_3(stage_2(img))
#
#         input_img = PipeImage(path=get_test_infile_path("RGB"))
#         stage_3(input_img)
#
#         cp_manager.purge_unrecognized_files()
#         assert (cp_directory / input_img.name / "pre_1.png").exists()
#         assert (cp_directory / input_img.name / "post_1.png").exists()
#         assert (cp_directory / input_img.name / "pre_2.png").exists()
#         assert (cp_directory / input_img.name / "post_2.png").exists()
#         assert (cp_directory / input_img.name / "pre_3.png").exists()
#         assert (cp_directory / input_img.name / "post_3.png").exists()
#
#     with get_temp_directory_path() as temp_directory:
#         run(temp_directory)
#         run(temp_directory)


# def test_post_file_processor() -> None:
#
#     with get_temp_directory_path() as cp_directory:
#         cp_manager = CheckpointManager(cp_directory)
#
#         @cp_manager.post_file_processor("checkpoint.png")
#         def function(infile: Path, outfile: Path) -> None:
#             outfile.write_bytes(infile.read_bytes())
#
#         # Test image from file
#         file_input_img = PipeImage(path=get_test_infile_path("RGB"))
#         file_output_img = function(file_input_img)
#         expected_path = cp_directory / file_input_img.name / "checkpoint.png"
#         assert file_output_img.path == expected_path
#         file_output_img = function(file_input_img)
#         assert file_output_img.path == expected_path
#
#         # Test image from code
#         image_input_img = PipeImage(image=Image.new("RGB", (100, 100)), name="RGB_2")
#         image_output_img = function(image_input_img)
#
#         expected_path = cp_directory / image_input_img.name / "checkpoint.png"
#         assert image_output_img.path == expected_path
#         image_output_img = function(image_input_img)
#         assert image_output_img.path == expected_path
#
#         # Test purge
#         mkdir(cp_directory / "to_delete")
#         open(cp_directory / file_input_img.name / "to_delete.png", "a").close()
#         cp_manager.purge_unrecognized_files()
#         assert file_output_img.path.exists()
#         assert image_output_img.path.exists()


def test_post_merger(alpha_merger: PipeStage) -> None:
    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)
        stage = cp_manager.post("checkpoint.png")(alpha_merger)

        color_input_path = get_test_infile_path("split/RGBA_color_RGB")
        color_input_img = PipeImage(path=color_input_path, name="test")
        alpha_input_path = get_test_infile_path("split/RGBA_alpha_L")
        alpha_input_img = PipeImage(path=alpha_input_path, name="test")
        output_img = stage(color_input_img, alpha_input_img)
        cp_manager.purge_unrecognized_files()

        assert output_img.path == cp_directory / "test" / "checkpoint.png"
        assert output_img.path.exists()


def test_post_processor(xbrz_processor: PipeStage) -> None:
    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)
        stage = cp_manager.post("checkpoint.png")(xbrz_processor)

        input_path = get_test_infile_path("RGB")
        input_img = PipeImage(path=input_path)
        output_img = stage(input_img)
        cp_manager.purge_unrecognized_files()

        assert output_img.path == cp_directory / input_img.name / "checkpoint.png"
        assert output_img.path.exists()

        # output_img = function(input_img)
        # assert process.count == 1


def test_post_splitter(alpha_splitter: PipeStage) -> None:
    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)
        stage = cp_manager.post("color.png", "alpha.png")(alpha_splitter)

        input_path = get_test_infile_path("RGBA")
        input_img = PipeImage(path=input_path)
        color_img, alpha_img = stage(input_img)
        cp_manager.purge_unrecognized_files()

        assert color_img.path == cp_directory / input_img.name / "color.png"
        assert color_img.path.exists()
        assert alpha_img.path == cp_directory / input_img.name / "alpha.png"
        assert alpha_img.path.exists()

        # color_img, alpha_img = function(input_img)
        # assert split.count == 1


def test_pre_merger(alpha_merger: PipeStage) -> None:
    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)
        stage = cp_manager.pre("color.png", "alpha.png")(alpha_merger)

        color_input_path = get_test_infile_path("split/RGBA_color_RGB")
        color_input_img = PipeImage(path=color_input_path, name="test")
        alpha_input_path = get_test_infile_path("split/RGBA_alpha_L")
        alpha_input_img = PipeImage(path=alpha_input_path, name="test")
        stage(color_input_img, alpha_input_img)
        cp_manager.purge_unrecognized_files()

        assert color_input_img.path == cp_directory / color_input_img.name / "color.png"
        assert color_input_img.path.exists()
        assert (
            np.array(PipeImage(path=color_input_path).image)
            == np.array(PipeImage(path=color_input_img.path).image)
        ).all()
        assert alpha_input_img.path == cp_directory / alpha_input_img.name / "alpha.png"
        assert alpha_input_img.path.exists()
        assert (
            np.array(PipeImage(path=alpha_input_path).image)
            == np.array(PipeImage(path=alpha_input_img.path).image)
        ).all()


def test_pre_processor(xbrz_processor: PipeStage) -> None:
    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)
        stage = cp_manager.pre("checkpoint.png")(xbrz_processor)

        input_path = get_test_infile_path("RGB")
        input_img = PipeImage(path=input_path)
        stage(input_img)
        cp_manager.purge_unrecognized_files()

        assert input_img.path == cp_directory / input_img.name / "checkpoint.png"
        assert input_img.path.exists()
        assert (
            np.array(PipeImage(path=input_path).image)
            == np.array(PipeImage(path=input_img.path).image)
        ).all()


def test_pre_splitter(alpha_splitter: PipeStage) -> None:
    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)
        stage = cp_manager.pre("checkpoint.png")(alpha_splitter)

        input_path = get_test_infile_path("RGBA")
        input_img = PipeImage(path=input_path)
        stage(input_img)
        cp_manager.purge_unrecognized_files()

        assert input_img.path == cp_directory / input_img.name / "checkpoint.png"
        assert input_img.path.exists()
        assert (
            np.array(PipeImage(path=input_path).image)
            == np.array(PipeImage(path=input_img.path).image)
        ).all()


def test_purge_unrecognized_files() -> None:
    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)

        mkdir(cp_directory / "to_delete")
        open(cp_directory / "to_delete.png", "a").close()
        cp_manager.purge_unrecognized_files()

        assert not (cp_directory / "to_delete").exists()
        assert not (cp_directory / "to_delete.png").exists()
