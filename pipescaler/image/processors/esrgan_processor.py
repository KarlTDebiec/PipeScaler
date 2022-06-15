#!/usr/bin/env python
#   pipescaler/processors/esrgan_processor.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
"""Upscales and/or denoises image using ESRGAN."""
from __future__ import annotations

from collections import OrderedDict
from logging import warning
from typing import Any

import torch

from pipescaler.core.image import PyTorchProcessor
from pipescaler.models.esrgan import Esrgan1x, Esrgan4x
from pipescaler.utilities.esrgan_serializer import EsrganSerializer


class EsrganProcessor(PyTorchProcessor):
    """Upscales and/or denoises image using ESRGAN.

    See [ESRGAN](https://github.com/xinntao/ESRGAN). Supports both old and new
    architectures.

    Adapted from [ESRGAN](https://github.com/xinntao/ESRGAN) and
    [Colab-ESRGAN](https://github.com/styler00dollar/Colab-ESRGAN), both licensed under
    the [Apache 2.0 License]
    (https://raw.githubusercontent.com/xinntao/ESRGAN/master/LICENSE)
    """

    def __init__(self, device: str = "cuda", **kwargs: Any) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            device: Device on which to compute
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        model = torch.load(self.model_infile)

        if isinstance(model, OrderedDict):
            model = EsrganSerializer().get_model(model)

        if isinstance(model, Esrgan1x):
            self.scale = 1
        elif isinstance(model, Esrgan4x):
            self.scale = 4
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

    @classmethod
    @property
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Upscales and/or denoises image using "
            "[ESRGAN](https://github.com/xinntao/ESRGAN) via PyTorch."
        )