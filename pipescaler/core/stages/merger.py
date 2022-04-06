#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for mergers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from logging import info
from typing import Any, Optional

from PIL import Image

from pipescaler.core.stage import Stage
from pipescaler.core.validation import validate_image


class Merger(Stage, ABC):
    """Abstract base class for mergers."""

    def __init__(
        self,
        suffix: Optional[str] = None,
        trim_suffixes: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Validate and store configuration.

        Arguments:
            suffix: Suffix to add to merged outfiles
            trim_suffixes: Suffixes to trim from merged outfiles
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Store configuration
        if suffix is not None:
            self.suffix = suffix
        else:
            self.suffix = "merge"
        if trim_suffixes is not None:
            self.trim_suffixes = trim_suffixes
        else:
            self.trim_suffixes = self.inlets

    def __call__(self, outfile: str, **kwargs: Any) -> None:
        """Merge infiles into an outfile.

        Arguments:
            outfile: Path to output file
            **kwargs: Additional keyword arguments; including one argument for each
              inlet, whose key is the name of that inlet and whose value is the path to
              the associated infile
        """
        infiles = {k: kwargs.get(k) for k in self.inlets}
        input_images = []
        for inlet in self.inlets:
            input_images.append(
                validate_image((infiles[inlet]), self.supported_input_modes[inlet])
            )

        output_image = self.merge(*input_images)

        output_image.save(outfile)
        info(f"'{self}: '{outfile}' saved")

    @property
    def outlets(self) -> list[str]:
        """Outlets that flow out of stage."""
        return ["outlet"]

    @classmethod
    @property
    @abstractmethod
    def supported_input_modes(self) -> dict[str, list[str]]:
        """Supported modes for input images."""
        raise NotImplementedError()

    @abstractmethod
    def merge(self, *input_images: Image.Image) -> Image.Image:
        """Merge images.

        Arguments:
            *input_images: Input images to merge
        Returns:
            Merged output image
        """
        raise NotImplementedError()
