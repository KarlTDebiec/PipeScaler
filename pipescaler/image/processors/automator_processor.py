#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Applies an Automator QuickAction to an image."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.core.image import Processor
from pipescaler.core.validation import validate_image_and_convert_mode
from pipescaler.runners import AutomatorRunner


class AutomatorProcessor(Processor):
    """Applies an Automator QuickAction to an image.

    See [Automator QuickAction](https://support.apple.com/guide/automator/welcome/mac)
    and [Pixelmator Pro](https://www.pixelmator.com/support/guide/pixelmator-pro/1270/)
    """

    def __init__(self, workflow: Path) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            workflow: Workflow to run
        """
        self.automator_runner = AutomatorRunner(workflow)

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_image: Input image
        Returns:
            Processed output image
        """
        input_image, output_mode = validate_image_and_convert_mode(
            input_image, self.inputs["input"], "RGB"
        )

        with temporary_filename(".png") as temp_infile:
            with temporary_filename(".png") as temp_outfile:
                input_image.save(temp_infile)
                self.automator_runner.run(temp_infile, temp_outfile)
                output_image = Image.open(temp_outfile)
        if output_image.mode != output_mode:
            output_image = output_image.convert(output_mode)

        return output_image

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Applies an [Automator QuickAction]"
            "(https://support.apple.com/guide/automator/welcome/mac) "
            "to an image; for example using [Pixelmator Pro]"
            "(https://www.pixelmator.com/support/guide/pixelmator-pro/1270/)."
        )

    @classmethod
    @property
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        """Inputs to this operator."""
        return {
            "input": ("RGB",),
        }

    @classmethod
    @property
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("RGB",),
        }
