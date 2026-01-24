#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Upscales and/or denoises image using ESRGAN."""

from __future__ import annotations

from collections import OrderedDict
from logging import warning
from typing import Any

from pipescaler.image.core.operators.processors import PyTorchImageProcessor
from pipescaler.image.models.esrgan import Esrgan1x, Esrgan4x
from pipescaler.image.utilities import EsrganSerializer


class EsrganProcessor(PyTorchImageProcessor):
    """Upscales and/or denoises image using ESRGAN.

    See [ESRGAN](https://github.com/xinntao/ESRGAN). Supports both old and new
    architectures.

    Adapted from [ESRGAN](https://github.com/xinntao/ESRGAN) and
    [Colab-ESRGAN](https://github.com/styler00dollar/Colab-ESRGAN), both licensed under
    the [Apache 2.0 License]
    (https://raw.githubusercontent.com/xinntao/ESRGAN/master/LICENSE)
    """

    def __init__(self, **kwargs: Any):
        """Validate and store configuration and initialize.

        Arguments:
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        if isinstance(self.model, OrderedDict):
            self.model = EsrganSerializer().get_model(self.model)
        if isinstance(self.model, Esrgan1x):
            self.scale = 1
        elif isinstance(self.model, Esrgan4x):
            self.scale = 4
        self.model.eval()

        try:
            self.model = self.model.to(self.device)
        except AssertionError as exc:
            device = "cpu"
            self.model = self.model.to(device)
            self.device = device
            warning(
                f"{self}: Torch raised '{exc}' with device '{device}', "
                f"falling back to cpu"
            )

    def __repr__(self) -> str:
        """Representation."""
        return (
            f"{self.__class__.__name__}("
            f"model_input_path={self.model_input_path!r}, "
            f"device={self.device})"
        )

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Upscales and/or denoises image using "
            "[ESRGAN](https://github.com/xinntao/ESRGAN) via PyTorch."
        )
