#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for pipelines"""
from itertools import tee
from typing import Iterator

from PIL import Image

from pipescaler.core import PipeImage, Stage
from pipescaler.mergers import AlphaMerger
from pipescaler.pipe.sources import DirectorySource
from pipescaler.processors import XbrzProcessor
from pipescaler.splitters import AlphaSplitter
from pipescaler.testing import get_sub_directory


def route(
    stage: Stage, inlets: dict[str, Iterator[PipeImage]]
) -> dict[str, Iterator[PipeImage]]:
    def generator() -> Iterator[PipeImage]:
        for input_pipe_images in zip(*inlets.values()):
            input_images = tuple(image.image for image in input_pipe_images)
            output_images = stage(*input_images)
            if isinstance(output_images, Image.Image):
                output_images = (output_images,)
            output_pipe_images = {
                outlet: PipeImage(output_images[i], input_pipe_images)
                for i, outlet in enumerate(stage.outputs)
            }
            yield output_pipe_images

    generator_for_all_outlets = generator()
    generators_for_individual_outlets = {}
    if len(stage.outputs) == 1:
        key = next(iter(stage.outputs.keys()))
        generators_for_individual_outlets[key] = (
            elem[key] for elem in generator_for_all_outlets
        )
    else:
        tees = tee(generator_for_all_outlets)
        for i, key in enumerate(stage.outputs.keys()):
            generators_for_individual_outlets[key] = eval(
                f"(elem['{key}'] for elem in tees[{i}])"
            )
    return generators_for_individual_outlets


def test() -> None:
    print()

    directory_source = DirectorySource(get_sub_directory("basic_temp"))

    xbrz_processor = XbrzProcessor()
    alpha_splitter = AlphaSplitter()
    alpha_merger = AlphaMerger()

    source_outlets = directory_source.get_outlets()
    alpha_splitter_outlets = route(alpha_splitter, source_outlets)
    color_outlets = route(xbrz_processor, {"color": alpha_splitter_outlets["color"]})
    alpha_outlets = route(xbrz_processor, {"alpha": alpha_splitter_outlets["alpha"]})

    alpha_merger_outlets = route(
        alpha_merger,
        {
            "color": color_outlets["outlet"],
            "alpha": alpha_outlets["outlet"],
        },
    )
    for image in alpha_merger_outlets["outlet"]:
        print(image)
        image.image.show()
