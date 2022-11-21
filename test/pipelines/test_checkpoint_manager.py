#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for CheckpointManager."""
from os import mkdir
from pathlib import Path
from tempfile import TemporaryDirectory

from pipescaler.core.pipelines import PipeImage, wrap_processor, wrap_splitter
from pipescaler.image.processors import XbrzProcessor
from pipescaler.image.splitters import AlphaSplitter
from pipescaler.pipelines import CheckpointManager
from pipescaler.testing import count_executions, get_test_infile_path


def test_post_file_processor() -> None:

    with TemporaryDirectory() as cp_directory:
        cp_directory = Path(cp_directory)
        cp_manager = CheckpointManager(cp_directory)

        @cp_manager.post_file_processor("checkpoint.png")
        def function(infile: Path, outfile: Path) -> None:
            outfile.write_bytes(infile.read_bytes())

        input_img = PipeImage(path=get_test_infile_path("RGB"))
        output_image = function(input_img)
        assert output_image.path == (cp_directory / input_img.name / "checkpoint.png")

        output_image = function(input_img)
        assert output_image.path == (cp_directory / input_img.name / "checkpoint.png")

        # touch an empty file
        mkdir(cp_directory / "to_delete")
        open(cp_directory / input_img.name / "to_delete.png", "a").close()

        cp_manager.purge_unrecognized_files()


def test_post_processor() -> None:
    process = count_executions(wrap_processor(XbrzProcessor()))

    with TemporaryDirectory() as cp_directory:
        cp_directory = Path(cp_directory)
        cp_manager = CheckpointManager(cp_directory)

        @cp_manager.post_processor("checkpoint.png")
        def function(input_img: PipeImage) -> PipeImage:
            output_img = process(input_img)
            return output_img

        input_img = PipeImage(path=get_test_infile_path("RGB"))
        output_image = function(input_img)
        assert output_image.path == (cp_directory / input_img.name / "checkpoint.png")

        output_image = function(input_img)
        assert output_image.path == (cp_directory / input_img.name / "checkpoint.png")
        assert process.count == 1

        # touch an empty file
        mkdir(cp_directory / "to_delete")
        open(cp_directory / input_img.name / "to_delete.png", "a").close()

        cp_manager.purge_unrecognized_files()


def test_post_splitter() -> None:
    split = count_executions(wrap_splitter(AlphaSplitter()))

    with TemporaryDirectory() as cp_directory:
        cp_directory = Path(cp_directory)
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

        cp_manager.purge_unrecognized_files()


def test_pre_processor() -> None:
    process = wrap_processor(XbrzProcessor())

    with TemporaryDirectory() as cp_directory:
        cp_directory = Path(cp_directory)
        cp_manager = CheckpointManager(cp_directory)

        @cp_manager.pre_processor("checkpoint.png")
        def function(input_img: PipeImage) -> PipeImage:
            output_img = process(input_img)
            return output_img

        input_path = get_test_infile_path("RGB")
        input_img = PipeImage(path=input_path)
        output_image = function(input_img)

        assert input_img.path == (cp_directory / input_img.name / "checkpoint.png")
        assert PipeImage(path=input_path).image == PipeImage(path=input_img.path).image

        cp_manager.purge_unrecognized_files()
