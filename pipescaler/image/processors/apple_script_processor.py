#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Runs image through an AppleScript."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.core.image import Processor
from pipescaler.core.validation import validate_image_and_convert_mode
from pipescaler.runners import AppleScriptRunner


class AppleScriptProcessor(Processor):
    """Runs image through an AppleScript.

    See [AppleScript](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/introduction/ASLR_intro.html),
    and [Pixelmator Pro](https://www.pixelmator.com/support/guide/pixelmator-pro/1270/)
    """

    def __init__(self, script: Path, arguments: str = "") -> None:
        """Validate and store configuration and initialize.

        Arguments:
            script: AppleScript to run
            arguments: Command-line arguments to pass to AppleScript
        """
        self.apple_script_runner = AppleScriptRunner(script, arguments)

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
                self.apple_script_runner.run(temp_infile, temp_outfile)
                output_image = Image.open(temp_outfile)
        if output_image.mode != output_mode:
            output_image = output_image.convert(output_mode)

        return output_image

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Runs image through an [AppleScript]"
            "(https://developer.apple.com/library/archive/documentation/AppleScript/"
            "Conceptual/AppleScriptLangGuide/introduction/ASLR_intro.html), "
            "using an application such as [Pixelmator Pro]"
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
