#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Upscales and/or denoises image using Waifu2x via PyTorch."""
from __future__ import annotations

from logging import warning
from typing import Any

import torch

from pipescaler.core.image import PyTorchProcessor


class WaifuProcessor(PyTorchProcessor):
    """Upscales and/or denoises image using Waifu2x via PyTorch.

    See [waifu2x](https://github.com/nagadomi/waifu2x).
    """

    def __init__(self, device: str = "cuda", **kwargs: Any) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            device: Device on which to compute
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        model = torch.load(self.model_infile)
        model.eval()
        try:
            self.model = model.to(device)
            self.device = device
        except AssertionError as error:
            device = "cpu"
            self.model = model.to(device)
            self.device = device
            warning(
                f"{self}: Torch raised '{error}' with device '{device}', "
                f"falling back to cpu"
            )

    def __repr__(self) -> str:
        """Representation."""
        return (
            f"{self.__class__.__name__}("
            f"device={self.device},"
            f"model_infile={self.model_infile})"
        )

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Upscales and/or denoises image using [Waifu2x]"
            "(https://github.com/nagadomi/waifu2x) via PyTorch."
        )
