#!python
# -*- coding: utf-8 -*-
#   lauhseuisin/processors/ESRGANProcessor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from os.path import expandvars
from typing import Any, Optional

import cv2
import numpy as np
import torch

from lauhseuisin.processors.Processor import Processor


################################### CLASSES ###################################
class ESRGANProcessor(Processor):
    executable_name = "waifu2x"

    def __init__(self, model: str, device: str = "cpu",
                 module_path: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.model = expandvars(model)
        self.device = device
        if module_path is not None:
            import sys
            sys.path.append(expandvars(module_path))
        import RRDBNet_arch as arch  # type:ignore
        self.arch = arch

    def process_file(self, infile: str, outfile: str) -> None:
        device = torch.device(self.device)
        model = self.arch.RRDBNet(3, 3, 64, 23, gc=32)
        model.load_state_dict(torch.load(self.model), strict=True)
        model.eval()
        model = model.to(device)

        image = cv2.imread(infile, cv2.IMREAD_COLOR)
        image = image * 1.0 / 255
        image = torch.from_numpy(
            np.transpose(image[:, :, [2, 1, 0]], (2, 0, 1))).float()
        image2 = image.unsqueeze(0)
        image2 = image2.to(device)

        with torch.no_grad():
            output = model(
                image2).data.squeeze().float().cpu().clamp_(0, 1).numpy()
        output = np.transpose(output[[2, 1, 0], :, :], (1, 2, 0))
        output = (output * 255.0).round()

        cv2.imwrite(outfile, output)
