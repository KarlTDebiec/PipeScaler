#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""POSTs image to a defined URL, which responds with processed image."""
from __future__ import annotations

import requests
from PIL import Image

from pipescaler.common import get_temp_file_path, validate_int
from pipescaler.core.image import Processor


class WebProcessor(Processor):
    """POSTs image to a defined URL, which responds with processed image."""

    def __init__(self, url: str, timeout: int = 600) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            url: URL to which to POST image for processing
            timeout: Timeout for POSTed request
        """
        self.url = url
        self.timeout = validate_int(timeout, 0)

    def __call__(self, input_image: Image.Image) -> Image.Image:
        """Process an image.

        Arguments:
            input_image: Input image
        Returns:
            Processed output image
        """
        with get_temp_file_path(".png") as input_path:
            input_image.save(input_path)
            with open(input_path, "rb") as input_file:
                input_bytes = input_file.read()
            files = {"image": ("image", input_bytes, "multipart/form-data")}

        with requests.Session() as session:
            response = session.post(self.url, files=files, timeout=self.timeout)
            if response.status_code != 200:
                raise ValueError()
            output_bytes = response.content

        with get_temp_file_path(".png") as output_path:
            with open(output_path, "wb") as output_file:
                output_file.write(output_bytes)
            output_image = Image.open(output_path)
        return output_image
