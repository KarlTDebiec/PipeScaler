#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Check the README's processor listings against the public package exports."""

from __future__ import annotations

import re
from inspect import getfile
from pathlib import Path
from types import ModuleType

import pytest

import pipescaler.image.operators.processors as image_processors
import pipescaler.video.processors as video_processors


@pytest.mark.parametrize(
    ("domain", "processors"), [("Image", image_processors), ("Video", video_processors)]
)
def test_readme_lists_public_processors(domain: str, processors: ModuleType):
    """Link every public processor to its defining module in its own section.

    Arguments:
        domain: README processing section prefix
        processors: package that exports the public processors
    """
    root_path = Path(__file__).resolve().parents[1]
    readme = (root_path / "README.md").read_text(encoding="utf-8")
    section = re.search(
        rf"^# {domain} Processing\n(.*?)(?=^# |\Z)", readme, re.M | re.S
    )
    assert section is not None, f"Missing {domain} Processing section"
    listing = re.search(
        r"^\*\*Processors\*\*[^\n]*\n(.*?)(?=^\*\*|\Z)", section[1], re.M | re.S
    )
    links = []
    if listing is not None:
        links = re.findall(r"^[*-] \[([^\]]+)\]\(([^)\s]+)\)", listing[1], re.M)

    github_prefix = "https://github.com/KarlTDebiec/PipeScaler/tree/master/"
    documented = {(name, target.removeprefix(github_prefix)) for name, target in links}
    expected = {
        (
            name,
            Path(getfile(getattr(processors, name)))
            .resolve()
            .relative_to(root_path)
            .as_posix(),
        )
        for name in processors.__all__
    }
    missing = sorted(expected - documented)
    stale = sorted(documented - expected)
    assert documented == expected, (
        f"{domain} processor links differ from public exports.\n"
        f"Missing expected links: {missing}\n"
        f"Unexpected links: {stale}"
    )
