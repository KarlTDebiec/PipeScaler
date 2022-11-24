#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for CheckpointManager."""
from os import mkdir
from pathlib import Path
from typing import Collection

import numpy as np
from PIL import Image

from pipescaler.common import get_temp_directory_path
from pipescaler.core.pipelines import PipeImage, PipeProcessor, PipeSplitter
from pipescaler.image.processors import XbrzProcessor
from pipescaler.image.splitters import AlphaSplitter
from pipescaler.pipelines import CheckpointManager
from pipescaler.testing import count_executions, get_test_infile_path

# TODO: internal_cpt should be a set
# TODO: internal_cpt tracking for PipeSplitter
# TODO: Test with heavier pipeline


def test_nested() -> None:
    process_1 = PipeProcessor(XbrzProcessor(scale=2))
    process_2 = PipeProcessor(XbrzProcessor(scale=2))
    process_3 = PipeProcessor(XbrzProcessor(scale=2))

    def run(cp_directory: Path) -> None:
        cp_manager = CheckpointManager(cp_directory)

        @cp_manager.pre_processor("pre_1.png")
        @cp_manager.post_processor("post_1.png")
        def stage_1(img: PipeImage) -> PipeImage:
            return process_1(img)

        @cp_manager.pre_processor("pre_2.png")
        @cp_manager.post_processor("post_2.png", calls=(stage_1,))
        def stage_2(img: PipeImage) -> PipeImage:
            return process_2(stage_1(img))

        @cp_manager.pre_processor("pre_3.png")
        @cp_manager.post_processor("post_3.png", calls=(stage_2,))
        def stage_3(img: PipeImage) -> PipeImage:
            return process_3(stage_2(img))

        input_img = PipeImage(path=get_test_infile_path("RGB"))
        stage_3(input_img)

        cp_manager.purge_unrecognized_files()
        assert (cp_directory / input_img.name / "pre_1.png").exists()
        assert (cp_directory / input_img.name / "post_1.png").exists()
        assert (cp_directory / input_img.name / "pre_2.png").exists()
        assert (cp_directory / input_img.name / "post_2.png").exists()
        assert (cp_directory / input_img.name / "pre_3.png").exists()
        assert (cp_directory / input_img.name / "post_3.png").exists()

    with get_temp_directory_path() as temp_directory:
        run(temp_directory)
        run(temp_directory)


def test_post_file_processor() -> None:

    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)

        @cp_manager.post_file_processor("checkpoint.png")
        def function(infile: Path, outfile: Path) -> None:
            outfile.write_bytes(infile.read_bytes())

        # Test image from file
        file_input_img = PipeImage(path=get_test_infile_path("RGB"))
        file_output_img = function(file_input_img)
        expected_path = cp_directory / file_input_img.name / "checkpoint.png"
        assert file_output_img.path == expected_path
        file_output_img = function(file_input_img)
        assert file_output_img.path == expected_path

        # Test image from code
        image_input_img = PipeImage(image=Image.new("RGB", (100, 100)), name="RGB_2")
        image_output_img = function(image_input_img)

        expected_path = cp_directory / image_input_img.name / "checkpoint.png"
        assert image_output_img.path == expected_path
        image_output_img = function(image_input_img)
        assert image_output_img.path == expected_path

        # Test purge
        mkdir(cp_directory / "to_delete")
        open(cp_directory / file_input_img.name / "to_delete.png", "a").close()
        cp_manager.purge_unrecognized_files()
        assert file_output_img.path.exists()
        assert image_output_img.path.exists()


def test_post_processor() -> None:
    process = count_executions(PipeProcessor(XbrzProcessor()))

    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)

        @cp_manager.post_processor("checkpoint.png")
        def function(img: PipeImage) -> PipeImage:
            return process(img)

        input_img = PipeImage(path=get_test_infile_path("RGB"))
        output_img = function(input_img)
        assert output_img.path == cp_directory / input_img.name / "checkpoint.png"

        output_img = function(input_img)
        assert output_img.path == cp_directory / input_img.name / "checkpoint.png"
        assert process.count == 1

        # Test purge
        mkdir(cp_directory / "to_delete")
        mkdir(cp_directory / input_img.name / "to_delete")
        open(cp_directory / input_img.name / "to_delete.png", "a").close()
        cp_manager.purge_unrecognized_files()
        assert output_img.path.exists()


def test_post_splitter() -> None:
    split = count_executions(PipeSplitter(AlphaSplitter()))

    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)

        @cp_manager.post_splitter("color.png", "alpha.png")
        def function(img: PipeImage) -> Collection[PipeImage]:
            return split(img)

        input_img = PipeImage(path=get_test_infile_path("RGBA"))
        color_img, alpha_img = function(input_img)
        assert color_img.path == cp_directory / input_img.name / "color.png"
        assert alpha_img.path == cp_directory / input_img.name / "alpha.png"

        color_img, alpha_img = function(input_img)
        assert color_img.path == cp_directory / input_img.name / "color.png"
        assert alpha_img.path == cp_directory / input_img.name / "alpha.png"
        assert split.count == 1

        # Test purge
        mkdir(cp_directory / "to_delete")
        open(cp_directory / input_img.name / "to_delete.png", "a").close()
        cp_manager.purge_unrecognized_files()
        assert color_img.path.exists()
        assert alpha_img.path.exists()


def test_pre_splitter() -> None:
    split = PipeSplitter(AlphaSplitter())

    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)

        @cp_manager.pre_processor("checkpoint.png")
        def function(img: PipeImage) -> Collection[PipeImage]:
            return split(img)

        input_path = get_test_infile_path("RGBA")
        input_img = PipeImage(path=input_path)
        function(input_img)
        cp_manager.purge_unrecognized_files()

        assert (cp_directory / input_img.name / "checkpoint.png").exists()
        assert input_img.path == cp_directory / input_img.name / "checkpoint.png"
        assert (
            np.array(PipeImage(path=input_path).image)
            == np.array(PipeImage(path=input_img.path).image)
        ).all()


def test_pre_processor() -> None:
    process = PipeProcessor(XbrzProcessor())

    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)

        @cp_manager.pre_processor("checkpoint.png")
        def function(img: PipeImage) -> PipeImage:
            return process(img)

        input_path = get_test_infile_path("RGB")
        input_img = PipeImage(path=input_path)
        function(input_img)
        cp_manager.purge_unrecognized_files()

        assert (cp_directory / input_img.name / "checkpoint.png").exists()
        assert input_img.path == cp_directory / input_img.name / "checkpoint.png"
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
