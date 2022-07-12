#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Functions for routing."""
from logging import info
from typing import Callable

from pipescaler.core.image import Merger, Processor, Splitter
from pipescaler.core.pipelines.pipe_image import PipeImage


def wrap_merger(merger: Merger) -> Callable[[PipeImage, ...], PipeImage]:
    """Wrap a merger.

    Arguments:
        merger: Merger to wrap
    """

    def wrapped(*input_pipe_images: PipeImage) -> PipeImage:
        """Wrapped merger.

        Arguments:
            *input_pipe_images: Input pipe images
        Returns:
            Output pipe image
        """
        input_images = tuple(image.image for image in input_pipe_images)

        output_image = merger(*input_images)
        output_pipe_image = PipeImage(output_image, parents=input_pipe_images)
        info(f"{merger}: '{output_pipe_image.name}' merged")

        return output_pipe_image

    return wrapped


def wrap_processor(processor: Processor) -> Callable[[PipeImage], PipeImage]:
    """Wrap a processor.

    Arguments:
        processor: Processor to wrap
    Returns:
        Wrapped processor
    """

    def wrapped(input_pipe_image: PipeImage) -> PipeImage:
        """Wrapped processor.

        Arguments:
            input_pipe_image: Input pipe image
        Returns:
            Output pipe image
        """
        input_image = input_pipe_image.image

        output_image = processor(input_image)
        output_pipe_image = PipeImage(output_image, parents=input_pipe_image)
        info(f"{processor}: '{output_pipe_image.name}' processed")

        return output_pipe_image

    return wrapped


def wrap_splitter(splitter: Splitter) -> Callable[[PipeImage], tuple[PipeImage, ...]]:
    """Wrap a splitter.

    Arguments:
        splitter: Splitter to wrap
    Returns:
        Wrapped splitter
    """

    def wrapped(input_pipe_image: PipeImage) -> tuple[PipeImage, ...]:
        """Wrapped splitter.

        Arguments:
            input_pipe_image: Input pipe image
        Returns:
            Output pipe images
        """
        input_image = input_pipe_image.image

        output_images = splitter(input_image)
        output_pipe_images = tuple(
            PipeImage(output_image, parents=input_pipe_image)
            for output_image in output_images
        )
        info(f"{splitter}: '{output_pipe_images[0].name}' split")

        return output_pipe_images

    return wrapped
