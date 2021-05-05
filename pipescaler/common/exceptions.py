#!/usr/bin/env python
#   common/exceptions.py
#
#   Copyright (C) 2017-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
"""
General-purpose exceptions not tied to a particular project.

Last updated 2020-10-10.
"""
####################################### MODULES ########################################
from inspect import currentframe, getframeinfo


####################################### CLASSES ########################################
class ArgumentConflictError(Exception):
    pass


class DirectoryExistsError(OSError):
    pass


class DirectoryNotFoundError(OSError):
    pass


class ExecutableNotFoundError(OSError):
    pass


class GetterError(TypeError):
    pass


class IsAFileError(OSError):
    pass


class NotAFileError(OSError):
    pass


class NotAFileOrDirectoryError(OSError):
    pass


class SetterError(TypeError):
    def __init__(self, cls: object, value: object):
        cls_type_name = type(cls).__name__
        # noinspection Mypy
        prop_name = getframeinfo(currentframe().f_back).function
        value_type_name = type(value).__name__
        prop_docstring = getattr(type(cls), prop_name).__doc__
        prop_docstring = prop_docstring.split(":")[0]

        self.message = (
            f"Property '{cls_type_name}.{prop_name}' was passed invalid value "
            f"'{value}' of type '{value_type_name}'. Expects '{prop_docstring}'."
        )

    def __str__(self) -> str:
        return self.message
