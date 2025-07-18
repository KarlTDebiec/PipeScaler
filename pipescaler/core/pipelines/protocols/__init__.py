# Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Protocols for pipeline components."""

from __future__ import annotations

from pipescaler.core.pipelines.protocols.pipe_object_protocol import PipeObjectProtocol
from pipescaler.core.pipelines.protocols.segment_protocol import SegmentProtocol
from pipescaler.core.pipelines.protocols.sorter_protocol import SorterProtocol
from pipescaler.core.pipelines.protocols.source_protocol import SourceProtocol
from pipescaler.core.pipelines.protocols.terminus_protocol import TerminusProtocol

__all__ = [
    "PipeObjectProtocol",
    "SegmentProtocol",
    "SourceProtocol",
    "SorterProtocol",
    "TerminusProtocol",
]
