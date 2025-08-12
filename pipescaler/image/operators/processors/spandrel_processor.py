#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processes image using Pytorch models loaded through Spandrel."""

from __future__ import annotations

from logging import warning
from pathlib import Path
from typing import Any

import torch
from spandrel import ModelLoader

from pipescaler.common.validation import val_input_path


class SpandrelProcessor:
    """Processes image using Pytorch models loaded through Spandrel."""

    def __init__(
        self, model_input_path: Path | str, *, channel_order: str = "RGB", **kwargs: Any
    ):
        self.channel_order = channel_order
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model_input_path = val_input_path(model_input_path)
        self.model = ModelLoader.load_model(model_input_path)
        try:
            self.model.eval()
            self.model.to(self.device)
        except Exception as exc:
            warning(f"Failed to call model.eval() and model.to(device): {exc}")

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Processes image using Pytorch models loaded through "
            "[Spandrel](https://github.com/chaiNNer-org/spandrel)."
        )

    @classmethod
    def inputs(cls) -> dict[str, tuple[str, ...]]:
        """Inputs to this operator."""
        return {
            "input": ("1", "L", "RGB"),
        }

    @classmethod
    def outputs(cls) -> dict[str, tuple[str, ...]]:
        """Outputs of this operator."""
        return {
            "output": ("1", "L", "RGB"),
        }
