#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Hosts stages on a web API."""
from importlib import import_module
from io import BytesIO
from os.path import splitext
from typing import Any

from flask import Flask, redirect, request, send_file, url_for

from pipescaler.common import temporary_filename
from pipescaler.core import initialize_stage
from pipescaler.core.stages import Processor


class Host:
    """Hosts stages on a web API."""

    def __init__(
        self, stages: dict[str, dict[str, dict[str, Any]]], **kwargs: Any
    ) -> None:
        """Validate and store configuration and initialize.

        Args:
            stages: Stages to make available
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        # Load configuration
        stage_modules = [
            import_module(f"pipescaler.{package}")
            for package in [
                "mergers",
                "processors",
                "sorters",
                "sources",
                "splitters",
                "termini",
            ]
        ]
        self.stages: dict[str, Processor] = {}
        for stage_name, stage_conf in stages.items():
            self.stages[stage_name] = initialize_stage(
                stage_name, stage_conf, stage_modules
            )

    def __call__(self, *args, **kwargs) -> None:
        """Perform operations.

        Args:
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        app = Flask(__name__, instance_relative_config=True)
        app.secret_key = "super secret key"

        @app.route("/<stage_name>", methods=["POST"])
        def stage(stage_name):
            if stage_name not in self.stages or "image" not in request.files:
                return redirect(url_for("entry_point"))

            # Receive image
            image_file = request.files["image"]
            extension = splitext(request.files["image"].filename)[-1]

            # Process image
            processor = self.stages[stage_name]
            with temporary_filename(extension) as infile:
                image_file.save(infile)
                with temporary_filename(extension) as outfile:
                    processor(infile, outfile)
                    with open(outfile, "rb") as output_file:
                        output_bytes = output_file.read()

            # Return image
            return send_file(
                BytesIO(output_bytes),
                download_name=f"response{extension}",
                mimetype="multipart/form-data",
            )

        @app.route("/")
        def entry_point():
            text = "<h4>Available Stages:</h4>"
            for stage_name in self.stages.keys():
                link_url = url_for("stage", stage_name=stage_name)
                text += f"<p><a href='{link_url}'>{stage_name}</a></p>"
            return text

        app.run(host="0.0.0.0")
