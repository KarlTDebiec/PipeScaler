#!/usr/bin/env python
#   pipescaler/processors/ESRGANProcessor.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

from os.path import expandvars
from typing import Any

import cv2
import numpy as np
import torch
import sys

sys.path.append(expandvars("$HOME/OneDrive/code/external/ESRGAN"))

from pipescaler.processors.Processor import Processor


################################### CLASSES ###################################
class ESRGANProcessor(Processor):

    @classmethod
    def process_file(cls, infile: str, outfile: str, **kwargs: Any) -> None:
        import RRDBNet_arch as arch
        model = expandvars("$HOME/OneDrive/code/external/ESRGAN/models/"
                           "RRDB_ESRGAN_x4.pth")
        print(model)

        device = torch.device("cpu")
        model = arch.RRDBNet(3, 3, 64, 23, gc=32)
        model.load_state_dict(torch.load(model), strict=True)
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


#################################### MAIN #####################################
if __name__ == "__main__":
    ESRGANProcessor.main()
