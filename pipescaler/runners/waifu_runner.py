#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Runs waifu2x tool for upscaling and/or denoising images."""
from __future__ import annotations

from platform import system

from pipescaler.core import Runner


class WaifuRunner(Runner):
    """Runs waifu2x tool for upscaling and/or denoising images.

    See [waifu2x](https://github.com/nagadomi/waifu2x).

    On Windows, requires [waifu2x-caffe](https://github.com/lltcggie/waifu2x-caffe) in
    the executor's path.

    On macOS, requires [waifu2x-mac](https://github.com/imxieyi/waifu2x-mac) in the
    executor's path.
    """

    def __init__(self, arguments: str = "-s 2 -n 1", **kwargs) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            arguments: Command-line arguments to pass to pngquant
            kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.arguments = arguments

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(arguments={self.arguments!r})"

    @property
    def command_template(self) -> str:
        """String template with which to generate command."""
        return (
            f"{self.executable_path} {self.arguments} "
            f"{'-p gpu' if system()=='Windows' else ''}"
            ' -i "{infile}" -o "{outfile}"'
        )

    @classmethod
    def executable(cls) -> str:
        """Name of executable."""
        if system() == "Windows":
            return "waifu2x-caffe-cui.exe"
        return "waifu2x"

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Upscales and/or denoises image using [Waifu2x]"
            "(https://github.com/nagadomi/waifu2x) via an external executable."
        )
