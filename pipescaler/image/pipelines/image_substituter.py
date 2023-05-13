#!/usr/bin/env python
#  Copyright 2020-2023 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Replaces image with an alternative sourced from a defined directory."""
from __future__ import annotations

from logging import info

from PIL import Image

from pipescaler.common import PathLike, validate_input_directory
from pipescaler.image.core.pipelines import PipeImage


class ImageSubstituter:
    """Replaces image with an alternative sourced from a defined directory."""

    def __init__(
        self,
        directory: PathLike,
        required: bool = False,
        match_input_mode: bool = True,
    ) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            directory: Directory from which to source alternative images
            required: Raise error if alternative image not found
            match_input_mode: Convert image to match input image's mode
        """
        self.directory = validate_input_directory(directory)
        self.substitutes = {f.stem: f for f in self.directory.iterdir()}
        self.required = required
        self.match_input_mode = match_input_mode

    def __call__(self, pipe_image: PipeImage) -> PipeImage:
        """Substitute image with an alternative sourced from a defined directory.

        Arguments:
            pipe_image: Image to substitute
        Returns:
            Alternate image
        """
        if pipe_image.name in self.substitutes:
            image = Image.open(self.substitutes[pipe_image.name])
            if self.match_input_mode and image.mode != pipe_image.image.mode:
                image = image.convert(pipe_image.image.mode)
                image.save(self.substitutes[pipe_image.name])
                info(
                    f"{self}: {self.substitutes[pipe_image.name].name} updated to mode "
                    f"{image.mode}"
                )
            return PipeImage(image=image, parents=pipe_image)
        if self.required:
            raise FileNotFoundError()
        return pipe_image
