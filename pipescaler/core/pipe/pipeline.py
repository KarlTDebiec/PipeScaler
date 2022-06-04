#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Pipeline."""

from __future__ import annotations


class Pipeline:
    def __init__(self, *pipes):
        self.pipes = pipes[0]

    def flow_into(self, *pipes) -> Pipeline:
        return Pipeline()

    def flow_until_empty(self):
        pass

    def __iter__(self):
        """Yield next image."""
        for filename in self.pipes:
            yield
