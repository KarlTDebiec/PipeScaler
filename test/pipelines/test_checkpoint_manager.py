#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for CheckpointManager."""
from __future__ import annotations

from unittest.mock import Mock

from pipescaler.common import get_temp_directory_path
from pipescaler.core.pipelines import PipeObject
from pipescaler.pipelines import CheckpointManager


def test_load_save():

    with get_temp_directory_path() as cp_directory_path:
        # Mocks
        mock_pipe_object_input = Mock(spec=PipeObject)
        mock_pipe_object_input.location_name = "test"
        mock_pipe_object_output = Mock(spec=PipeObject)
        mock_pipe_object_output.location_name = "test"
        cp_manager = CheckpointManager(cp_directory_path)

        # Load unavailable checkpoint
        result = cp_manager.load((mock_pipe_object_input,), ("cpt.txt",))
        assert result == None

        # Save checkpoint
        cp_manager.save((mock_pipe_object_output,), ("cpt.txt",))

    # Test miscellaneous methods
    print(cp_manager)
    print(repr(cp_manager))
