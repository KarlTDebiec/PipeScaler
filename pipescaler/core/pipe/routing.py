#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Functions for routing."""
from itertools import tee
from typing import Iterator

from PIL import Image

from pipescaler.core import PipeImage, Stage


def route(
    stage: Stage, inlets: dict[str, Iterator[PipeImage]]
) -> dict[str, Iterator[PipeImage]]:
    def generator() -> Iterator[PipeImage]:
        for input_pipe_images in zip(*inlets.values()):
            input_images = tuple(image.image for image in input_pipe_images)
            output_images = stage(*input_images)
            if isinstance(output_images, Image.Image):
                yield [PipeImage(output_images, input_pipe_images)]
            else:
                yield [
                    PipeImage(output_image, input_pipe_images)
                    for output_image in output_images
                ]

    generator_of_all_outlets = generator()
    generators_of_individual_outlets = {}
    if len(stage.outputs) == 1:
        generators_of_individual_outlets[next(iter(stage.outputs.keys()))] = (
            elem[0] for elem in generator_of_all_outlets
        )
    else:
        tees = tee(generator_of_all_outlets)
        for i, outlet in enumerate(stage.outputs.keys()):
            generators_of_individual_outlets[outlet] = eval(
                f"(elem[{i}] for elem in tees[{i}])"
            )
    return generators_of_individual_outlets
