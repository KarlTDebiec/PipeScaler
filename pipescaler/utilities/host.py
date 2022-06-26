#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Hosts stages on a web API."""
from io import BytesIO
from pathlib import Path

from flask import Flask, redirect, request, send_file, url_for
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.core import Utility
from pipescaler.core.image import Processor


class Host(Utility):
    """Hosts stages on a web API."""

    def __init__(self, processors: dict[str, Processor]) -> None:
        """Validate and store configuration and initialize.

        Arguments:
            processors: Processors to host and names under which to host them
        """
        self.processors = processors

    def __call__(self) -> None:
        """Host web API."""
        app = Flask(__name__, instance_relative_config=True)
        app.secret_key = "super secret key"

        @app.route("/<stage_name>", methods=["POST"])
        def stage(stage_name):
            if stage_name not in self.processors or "image" not in request.files:
                return redirect(url_for("entry_point"))

            # Receive image
            image_file = request.files["image"]
            extension = Path(request.files["image"].filename).suffix

            # Process image
            processor = self.processors[stage_name]
            with temporary_filename(extension) as infile:
                image_file.save(infile)
                input_image = Image.open(infile)
                with temporary_filename(".png") as outfile:
                    output_image = processor(input_image)
                    output_image.save(outfile)
                    with open(outfile, "rb") as output_file:
                        output_bytes = output_file.read()

            # Return image
            return send_file(
                BytesIO(output_bytes),
                download_name="response.png",
                mimetype="multipart/form-data",
            )

        @app.route("/")
        def entry_point():
            text = "<h4>Available Stages:</h4>"
            for stage_name in self.processors.keys():
                link_url = url_for("stage", stage_name=stage_name)
                text += f"<p><a href='{link_url}'>{stage_name}</a></p>"
            return text

        app.run(host="0.0.0.0")
