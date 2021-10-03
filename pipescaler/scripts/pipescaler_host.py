#!/usr/bin/env python
#   pipescaler/scripts/pipescaler_host.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
from argparse import ArgumentParser
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from inspect import cleandoc
from os import environ
from os.path import expandvars, normpath
from pprint import pformat, pprint
from typing import Any, Dict

import yaml
from flask import Flask, flash, redirect, request, url_for

from pipescaler.common import CLTool, validate_input_path
from pipescaler.core import Stage


class PipescalerHost(CLTool):
    """"""

    def __init__(
        self, stages: Dict[str, Dict[str, Dict[str, Any]]], **kwargs: Any
    ) -> None:
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

        # Initialize stages
        self.stages: Dict[str, Stage] = {}
        for stage_name, stage_conf in stages.items():
            # Get stage's class name
            stage_cls_name = next(iter(stage_conf))  # get first key

            # Get stage's configuration
            stage_args = stage_conf.get(stage_cls_name)
            if stage_args is None:
                stage_args = {}

            # Get stage's class
            stage_cls = None
            for module in stage_modules:
                try:
                    stage_cls = getattr(module, stage_cls_name)
                except AttributeError:
                    continue
            if stage_cls is None:
                if "infile" in stage_args:
                    module_infile = validate_input_path(stage_args.pop("infile"))
                    spec = spec_from_file_location(stage_cls_name, module_infile)
                    module = module_from_spec(spec)
                    spec.loader.exec_module(module)
                    stage_cls = getattr(module, stage_cls_name)
                else:
                    raise KeyError(f"Class '{stage_cls_name}' not found")

            # Initialize stage
            self.stages[stage_name] = stage_cls(name=stage_name, **stage_args)

    def __call__(self, *args, **kwargs):
        app = Flask(__name__, instance_relative_config=True)

        @app.route("/<stage_name>", methods=["GET", "POST"])
        def stage(stage_name):
            if stage_name in self.stages and request.method == "GET":
                return pformat(self.stages[stage_name])
            elif stage_name in self.stages and request.method == "POST":
                if "file" not in request.files:
                    flash("No file part")
                    return redirect(url_for("entry_point"))
                file = request.files["file"]
                print(file)
            else:
                return redirect(url_for("entry_point"))

        @app.route("/")
        def entry_point():
            text = "<h4>Available Stages:</h4>"
            for stage_name in self.stages.keys():
                link_url = url_for("stage", stage_name=stage_name)
                text += f"<p><a href='{link_url}'>{stage_name}</a></p>"
            return text

        app.run()

    @classmethod
    def construct_argparser(cls, **kwargs: Any) -> ArgumentParser:
        """
        Constructs argument parser.

        Args:
            kwargs (Any): Additional keyword arguments

        Returns:
            parser (ArgumentParser): Argument parser
        """
        description = kwargs.pop("description", cleandoc(cls.__doc__))
        parser = super().construct_argparser(description=description, **kwargs)

        # Input
        parser.add_argument(
            "conf_file", type=cls.input_path_arg(), help="configuration file"
        )

        return parser

    @classmethod
    def main(cls) -> None:
        """Parses arguments, constructs tool, and calls tool."""
        parser = cls.construct_argparser()
        kwargs = vars(parser.parse_args())

        conf_file = kwargs.pop("conf_file")
        with open(validate_input_path(conf_file), "r") as f:
            conf = yaml.load(f, Loader=yaml.SafeLoader)

        # Set environment variables
        for key, value in conf.pop("environment", {}).items():
            environ[key] = normpath(expandvars(value))

        tool = cls(**{**kwargs, **conf})
        tool()


if __name__ == "__main__":
    PipescalerHost.main()
