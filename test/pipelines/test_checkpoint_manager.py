#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for CheckpointManager."""
from os import mkdir
from pathlib import Path

from PIL import Image

from pipescaler.common import get_temp_directory_path
from pipescaler.core.pipelines import PipeImage, wrap_processor, wrap_splitter
from pipescaler.image.processors import XbrzProcessor
from pipescaler.image.splitters import AlphaSplitter
from pipescaler.pipelines import CheckpointManager
from pipescaler.testing import count_executions, get_test_infile_path

# TODO: ContextManager for CheckpointManager
# TODO: Test with heavier pipeline


def copy(infile: Path, outfile: Path) -> None:
    """Copies a file.

    Arguments:
        infile: Input file
        outfile: Output file
    """
    outfile.write_bytes(infile.read_bytes())


def test_nested() -> None:
    process_1 = wrap_processor(XbrzProcessor(scale=2))
    process_2 = wrap_processor(XbrzProcessor(scale=2))
    process_3 = wrap_processor(XbrzProcessor(scale=2))

    def run(cp_directory: Path) -> None:
        cp_manager = CheckpointManager(cp_directory)

        @cp_manager.pre_processor("pre_1.png")
        @cp_manager.post_processor("post_1.png")
        def stage_1(input_img: PipeImage) -> PipeImage:
            output_img = process_1(input_img)
            return output_img

        @cp_manager.pre_processor("pre_2.png")
        @cp_manager.post_processor("post_2.png", stage_1)
        def stage_2(input_img: PipeImage) -> PipeImage:
            img = stage_1(input_img)
            output_img = process_2(img)
            return output_img

        @cp_manager.pre_processor("pre_3.png")
        @cp_manager.post_processor("post_3.png", stage_2)
        def stage_3(input_img: PipeImage) -> PipeImage:
            img = stage_2(input_img)
            output_img = process_3(img)
            return output_img

        input_img = PipeImage(path=get_test_infile_path("RGB"))

        cp_manager.purge_unrecognized_files()
        assert (cp_directory / input_img.name / "pre_1.png").exists()
        assert (cp_directory / input_img.name / "post_1.png").exists()
        assert (cp_directory / input_img.name / "pre_2.png").exists()
        assert (cp_directory / input_img.name / "post_2.png").exists()
        assert (cp_directory / input_img.name / "pre_3.png").exists()
        assert (cp_directory / input_img.name / "post_3.png").exists()

    with get_temp_directory_path() as cp_directory:
        run(cp_directory)
        run(cp_directory)


def test_post_file_processor() -> None:

    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)

        @cp_manager.post_file_processor("checkpoint.png")
        def function(infile: Path, outfile: Path) -> None:
            outfile.write_bytes(infile.read_bytes())

        # Test image from file
        file_input_img = PipeImage(path=get_test_infile_path("RGB"))
        file_output_img = function(file_input_img)
        assert file_output_img.path == (
            cp_directory / file_input_img.name / "checkpoint.png"
        )
        file_output_img = function(file_input_img)
        assert file_output_img.path == (
            cp_directory / file_input_img.name / "checkpoint.png"
        )

        # Test image from code
        image_input_img = PipeImage(image=Image.new("RGB", (100, 100)), name="RGB_2")
        image_output_img = function(image_input_img)
        assert image_output_img.path == (
            cp_directory / image_input_img.name / "checkpoint.png"
        )
        image_output_img = function(image_input_img)
        assert image_output_img.path == (
            cp_directory / image_input_img.name / "checkpoint.png"
        )

        # Test purge
        mkdir(cp_directory / "to_delete")
        open(cp_directory / file_input_img.name / "to_delete.png", "a").close()
        cp_manager.purge_unrecognized_files()
        assert file_output_img.path.exists()
        assert image_output_img.path.exists()


def test_post_processor() -> None:
    process = count_executions(wrap_processor(XbrzProcessor()))

    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)

        @cp_manager.post_processor("checkpoint.png")
        def function(input_img: PipeImage) -> PipeImage:
            output_img = process(input_img)
            return output_img

        input_img = PipeImage(path=get_test_infile_path("RGB"))
        output_img = function(input_img)
        assert output_img.path == (cp_directory / input_img.name / "checkpoint.png")

        output_img = function(input_img)
        assert output_img.path == (cp_directory / input_img.name / "checkpoint.png")
        assert process.count == 1

        # Test purge
        mkdir(cp_directory / "to_delete")
        mkdir(cp_directory / input_img.name / "to_delete")
        open(cp_directory / input_img.name / "to_delete.png", "a").close()
        cp_manager.purge_unrecognized_files()
        assert output_img.path.exists()


def test_post_splitter() -> None:
    split = count_executions(wrap_splitter(AlphaSplitter()))

    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)

        @cp_manager.post_splitter("color.png", "alpha.png")
        def function(image: PipeImage) -> tuple[PipeImage, ...]:
            color_img, alpha_img = split(image)
            return color_img, alpha_img

        input_img = PipeImage(path=get_test_infile_path("RGBA"))
        color_img, alpha_img = function(input_img)
        assert color_img.path == (cp_directory / input_img.name / "color.png")
        assert alpha_img.path == (cp_directory / input_img.name / "alpha.png")

        color_img, alpha_img = function(input_img)
        assert color_img.path == (cp_directory / input_img.name / "color.png")
        assert alpha_img.path == (cp_directory / input_img.name / "alpha.png")
        assert split.count == 1

        # Test purge
        mkdir(cp_directory / "to_delete")
        open(cp_directory / input_img.name / "to_delete.png", "a").close()
        cp_manager.purge_unrecognized_files()
        assert color_img.path.exists()
        assert alpha_img.path.exists()


def test_pre_processor() -> None:
    process = wrap_processor(XbrzProcessor())

    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)

        @cp_manager.pre_processor("checkpoint.png")
        def function(input_img: PipeImage) -> PipeImage:
            output_img = process(input_img)
            return output_img

        input_path = get_test_infile_path("RGB")
        input_img = PipeImage(path=input_path)
        output_img = function(input_img)

        assert input_img.path == (cp_directory / input_img.name / "checkpoint.png")
        assert PipeImage(path=input_path).image == PipeImage(path=input_img.path).image

        # Test purge
        mkdir(cp_directory / "to_delete")
        open(cp_directory / input_img.name / "to_delete.png", "a").close()
        cp_manager.purge_unrecognized_files()
        assert input_img.path.exists()
