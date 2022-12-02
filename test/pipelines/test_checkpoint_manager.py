#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for CheckpointManager."""
from os import mkdir
from pathlib import Path
from typing import Callable

import numpy as np
import pytest
from PIL import Image

from pipescaler.common import get_temp_directory_path
from pipescaler.core.pipelines import (
    MergerSegment,
    PipeImage,
    ProcessorSegment,
    Segment,
    SplitterSegment,
)
from pipescaler.image.mergers import AlphaMerger
from pipescaler.image.processors import XbrzProcessor
from pipescaler.image.splitters import AlphaSplitter
from pipescaler.pipelines import CheckpointManager
from pipescaler.testing import get_test_infile_path


@pytest.fixture
def xbrz_processor() -> ProcessorSegment:
    return ProcessorSegment(XbrzProcessor(scale=2))


@pytest.fixture
def alpha_splitter() -> SplitterSegment:
    return SplitterSegment(AlphaSplitter())


@pytest.fixture
def alpha_merger() -> MergerSegment:
    return MergerSegment(AlphaMerger())


@pytest.fixture
def copy_file() -> Callable[[Path, Path], None]:
    def function(infile: Path, outfile: Path) -> None:
        outfile.write_bytes(infile.read_bytes())

    return function


@pytest.mark.parametrize(
    ("segment_name", "infiles", "pre_checkpoints", "post_checkpoints"),
    [
        (
            "alpha_merger",
            ("split/RGBA_color_RGB", "split/RGBA_alpha_L"),
            ("color.png", "alpha.png"),
            ("merged.png",),
        ),
        (
            "alpha_splitter",
            ("RGBA",),
            ("pre.png",),
            ("color.png", "alpha.png"),
        ),
        (
            "xbrz_processor",
            ("RGB",),
            ("pre.png",),
            ("post.png",),
        ),
    ],
)
def test_load_save(
    segment_name: str,
    infiles: tuple[str],
    pre_checkpoints: tuple[str],
    post_checkpoints: tuple[str],
    request,
) -> None:
    segment = request.getfixturevalue(segment_name)
    assert isinstance(segment, Segment)

    def run(cp_directory: Path) -> None:
        cp_manager = CheckpointManager(cp_directory)

        input_paths = [get_test_infile_path(infile) for infile in infiles]
        inputs = tuple(
            PipeImage(path=input_path, name="test") for input_path in input_paths
        )
        inputs = cp_manager.save(inputs, pre_checkpoints, overwrite=False)
        if not (outputs := cp_manager.load(inputs, post_checkpoints)):
            outputs = segment(*inputs)
            assert outputs
            outputs = cp_manager.save(outputs, post_checkpoints)
        cp_manager.purge_unrecognized_files()

        for i, c, p in zip(inputs, pre_checkpoints, input_paths):
            assert i.path == cp_directory / i.name / c
            assert i.path.exists()
            assert (
                np.array(PipeImage(path=p).image)
                == np.array(PipeImage(path=i.path).image)
            ).all()

        for o, c in zip(outputs, post_checkpoints):
            assert o.path == cp_directory / o.name / c
            assert o.path.exists()

    with get_temp_directory_path() as temp_directory:
        run(temp_directory)
        run(temp_directory)


def test_split_merge(
    xbrz_processor: ProcessorSegment,
    alpha_splitter: SplitterSegment,
    alpha_merger: MergerSegment,
) -> None:
    def run(cp_directory: Path) -> None:
        cp_manager = CheckpointManager(cp_directory)

        @cp_manager.pre_segment("pre_color.png")
        @cp_manager.post_segment("post_color.png")
        def color_segment(*inputs: PipeImage) -> tuple[PipeImage, ...]:
            xbrz_outputs = xbrz_processor(*inputs)
            return xbrz_outputs

        @cp_manager.pre_segment("pre_alpha.png")
        @cp_manager.post_segment("post_alpha.png")
        def alpha_segment(*inputs: PipeImage) -> tuple[PipeImage, ...]:
            xbrz_outputs = xbrz_processor(*inputs)
            return xbrz_outputs

        @cp_manager.pre_segment("pre_split.png")
        @cp_manager.post_segment("post_merge.png", calls=[alpha_segment, color_segment])
        def split_merge_segment(*inputs: PipeImage) -> tuple[PipeImage, ...]:
            outputs = alpha_splitter(*inputs)
            color = color_segment(outputs[0])
            alpha = alpha_segment(outputs[1])
            merged = alpha_merger(*color, *alpha)
            return merged

        input_path = get_test_infile_path("RGBA")
        inputs = (PipeImage(path=input_path),)
        split_merge_segment(*inputs)
        cp_manager.purge_unrecognized_files()

        assert (cp_directory / inputs[0].name / "pre_split.png").exists()
        assert (cp_directory / inputs[0].name / "pre_color.png").exists()
        assert (cp_directory / inputs[0].name / "post_color.png").exists()
        assert (cp_directory / inputs[0].name / "pre_alpha.png").exists()
        assert (cp_directory / inputs[0].name / "post_alpha.png").exists()
        assert (cp_directory / inputs[0].name / "post_merge.png").exists()

    with get_temp_directory_path() as temp_directory:
        run(temp_directory)
        run(temp_directory)


def test_nested(
    xbrz_processor: ProcessorSegment,
    alpha_splitter: SplitterSegment,
    alpha_merger: AlphaMerger,
) -> None:
    def run(cp_directory: Path) -> None:
        cp_manager = CheckpointManager(cp_directory)

        @cp_manager.pre_segment("pre_inner.png")
        @cp_manager.post_segment("post_inner.png")
        def inner_segment(*inputs: PipeImage) -> tuple[PipeImage, ...]:
            xbrz_outputs = xbrz_processor(*inputs)
            return xbrz_outputs

        @cp_manager.pre_segment("pre_outer.png")
        @cp_manager.post_segment("post_outer.png", calls=[inner_segment])
        def outer_segment(*inputs: PipeImage) -> tuple[PipeImage, ...]:
            xbrz_outputs = xbrz_processor(*inputs)
            return inner_segment(*xbrz_outputs)

        input_path = get_test_infile_path("RGB")
        inputs = (PipeImage(path=input_path),)
        outer_segment(*inputs)
        cp_manager.purge_unrecognized_files()

        assert (cp_directory / inputs[0].name / "pre_inner.png").exists()
        assert (cp_directory / inputs[0].name / "post_inner.png").exists()
        assert (cp_directory / inputs[0].name / "pre_outer.png").exists()
        assert (cp_directory / inputs[0].name / "post_outer.png").exists()

    with get_temp_directory_path() as temp_directory:
        run(temp_directory)
        run(temp_directory)


def test_post_runner(copy_file: Callable[[Path, Path], None]) -> None:

    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)
        segment = cp_manager.post_runner("checkpoint.png")(copy_file)

        # Test image from file
        file_input_path = get_test_infile_path("RGB")
        inputs = (PipeImage(path=file_input_path),)

        outputs = segment(*inputs)
        cp_manager.purge_unrecognized_files()
        assert outputs[0].path == cp_directory / inputs[0].name / "checkpoint.png"
        assert outputs[0].path.exists()

        outputs = segment(*inputs)
        cp_manager.purge_unrecognized_files()
        assert outputs[0].path == cp_directory / inputs[0].name / "checkpoint.png"
        assert outputs[0].path.exists()

        # Test image from code
        inputs = (PipeImage(image=Image.new("RGB", (100, 100)), name="RGB_2"),)

        outputs = segment(*inputs)
        cp_manager.purge_unrecognized_files()
        assert outputs[0].path == cp_directory / inputs[0].name / "checkpoint.png"
        assert outputs[0].path.exists()

        outputs = segment(*inputs)
        cp_manager.purge_unrecognized_files()
        assert outputs[0].path == cp_directory / inputs[0].name / "checkpoint.png"
        assert outputs[0].path.exists()


@pytest.mark.parametrize(
    ("segment_name", "infiles", "checkpoints"),
    [
        (
            "alpha_merger",
            ("split/RGBA_color_RGB", "split/RGBA_alpha_L"),
            ("post.png",),
        ),
        (
            "alpha_splitter",
            ("RGBA",),
            ("color.png", "alpha.png"),
        ),
        (
            "xbrz_processor",
            ("RGB",),
            ("post.png",),
        ),
    ],
)
def test_post_segment(
    segment_name: str, infiles: tuple[str], checkpoints: tuple[str], request
) -> None:
    segment = request.getfixturevalue(segment_name)
    assert isinstance(segment, Segment)

    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)
        segment = cp_manager.post_segment(*checkpoints)(segment)
        input_paths = [get_test_infile_path(infile) for infile in infiles]
        inputs = [PipeImage(path=input_path, name="test") for input_path in input_paths]
        outputs = segment(*inputs)
        cp_manager.purge_unrecognized_files()

        for o, c in zip(outputs, checkpoints):
            assert o.path == cp_directory / o.name / c
            assert o.path.exists()


@pytest.mark.parametrize(
    ("segment_name", "infiles", "checkpoints"),
    [
        (
            "alpha_merger",
            ("split/RGBA_color_RGB", "split/RGBA_alpha_L"),
            ("color.png", "alpha.png"),
        ),
        (
            "alpha_splitter",
            ("RGBA",),
            ("pre.png",),
        ),
        (
            "xbrz_processor",
            ("RGB",),
            ("pre.png",),
        ),
    ],
)
def test_pre_segment(
    segment_name: str, infiles: tuple[str], checkpoints: tuple[str], request
) -> None:
    segment = request.getfixturevalue(segment_name)
    assert isinstance(segment, Segment)

    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)
        segment = cp_manager.pre_segment(*checkpoints)(segment)
        input_paths = [get_test_infile_path(infile) for infile in infiles]
        inputs = [PipeImage(path=input_path, name="test") for input_path in input_paths]
        outputs = segment(*inputs)
        cp_manager.purge_unrecognized_files()

        for i, c, p in zip(inputs, checkpoints, input_paths):
            assert i.path == cp_directory / i.name / c
            assert i.path.exists()
            assert (
                np.array(PipeImage(path=p).image)
                == np.array(PipeImage(path=i.path).image)
            ).all()


def test_purge_unrecognized_files() -> None:
    with get_temp_directory_path() as cp_directory:
        cp_manager = CheckpointManager(cp_directory)

        mkdir(cp_directory / "to_delete")
        open(cp_directory / "to_delete.png", "a").close()
        cp_manager.purge_unrecognized_files()

        assert not (cp_directory / "to_delete").exists()
        assert not (cp_directory / "to_delete.png").exists()
