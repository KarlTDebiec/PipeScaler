#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Replaces image with an alternative sourced from a defined directory."""
from __future__ import annotations

from logging import info
from pathlib import Path
from typing import Union

from PIL import Image

from pipescaler.common import validate_input_directory
from pipescaler.core.pipelines import PipeImage


class Substituter:
    """Replaces image with an alternative sourced from a defined directory."""

    def __init__(
        self,
        directory: Union[str, Path],
        match_input_mode: bool = True,
    ) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            directory: Directory from which to load alternative images
            clean_suffix: Suffix to remove from alternative images
            match_input_mode: Ensure output image mode matches input image mode
        """
        self.directory = Path(
            validate_input_directory(directory, create_directory=True)
        )
        self.substitutes = {f.stem: f for f in self.directory.iterdir()}
        self.match_input_mode = match_input_mode

    def __call__(self, pipe_image: PipeImage) -> PipeImage:
        if pipe_image.name in self.substitutes:
            image = Image.open(self.substitutes[pipe_image.name])
            if self.match_input_mode and image.mode != pipe_image.image.mode:
                image = image.convert()
                image.save(self.substitutes[pipe_image.name])
                info(
                    f"{self}: {self.substitutes[pipe_image.name].name} updated to mode "
                    f"{image.mode}"
                )
            return PipeImage(image, parents=pipe_image)
        return pipe_image
