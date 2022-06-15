#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Exceptions."""


class TerminusReached(Exception):
    """Pipeline terminus has been reached."""


class UnsupportedImageModeError(Exception):
    """Mode of image is not supported."""