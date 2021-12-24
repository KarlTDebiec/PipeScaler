#!/usr/bin/env python
#   pipescaler/core/exception.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""Core pipescaler exceptions"""


class TerminusReached(Exception):
    """Pipeline terminus has been reached"""

    pass


class UnsupportedImageModeError(Exception):
    """Mode of image is not supported"""

    pass
