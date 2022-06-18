#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""POSTs image to a defined URL, which responds with processed image."""
from __future__ import annotations

import requests
from PIL import Image

from pipescaler.common import temporary_filename, validate_int
from pipescaler.core.image import Processor


class WebProcessor(Processor):
    """POSTs image to a defined URL, which responds with processed image."""

    def __init__(self, url: str, timeout: int = 600) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            url: URL to which to POST image for processing
        """
        self.url = url
        self.timeout = validate_int(timeout, 0)

    def __call__(self, input_image: Image.Image) -> Image.Image:
        with temporary_filename(".png") as temp_file:
            input_image.save(temp_file)
            with open(temp_file, "rb") as input_file:
                input_bytes = input_file.read()
            files = {"image": ("image", input_bytes, "multipart/form-data")}

        with requests.Session() as session:
            response = session.post(self.url, files=files, timeout=self.timeout)
            if response.status_code != 200:
                raise ValueError()
            output_bytes = response.content

        with temporary_filename(".png") as temp_file:
            with open(temp_file, "wb") as output_file:
                output_file.write(output_bytes)
            output_image = Image.open(temp_file)
        return output_image
