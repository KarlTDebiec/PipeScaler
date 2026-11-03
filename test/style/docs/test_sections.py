#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.

"""Tests of docstring section formatting."""

from __future__ import annotations

from itertools import permutations

import pytest

from test.style.docs.checks import get_sample_docstring_violations


@pytest.mark.parametrize("section_name", ["Arguments", "Raises", "Returns", "Yields"])
@pytest.mark.parametrize("has_blank_line", [False, True])
@pytest.mark.parametrize("has_details", [False, True])
def test_description_is_separated_from_first_section(
    section_name: str, has_blank_line: bool, has_details: bool
):
    """Require a blank line before the first section after short or long descriptions.

    Arguments:
        section_name: structured section following the description
        has_blank_line: whether the description and section are separated
        has_details: whether the description includes an explanatory paragraph
    """
    content, signature, body = {
        "Arguments": ("        value: sample value", "value", "    pass"),
        "Raises": ("        ValueError: always", "", "    raise ValueError"),
        "Returns": ("        returned value", "", "    return 1"),
        "Yields": ("        generated value", "", "    yield 1"),
    }[section_name]
    details = "\n\n    Further explanation of the callable." if has_details else ""
    separator = "\n" if has_blank_line else ""

    violations = get_sample_docstring_violations(
        f'''
def sample({signature}):
    """Sample function.{details}
{separator}    {section_name}:
{content}
    """
{body}
'''
    )

    expected_rules = [] if has_blank_line else ["description-section-spacing"]
    assert [violation.rule_id for violation in violations] == expected_rules


@pytest.mark.parametrize(
    ("first_section_name", "second_section_name"),
    list(permutations(("Arguments", "Raises", "Returns", "Yields"), 2)),
)
def test_docstring_section_spacing_is_enforced(
    first_section_name: str, second_section_name: str
):
    """Test adjacent structured sections reject a preceding blank line.

    Arguments:
        first_section_name: first section name
        second_section_name: second section name
    """
    section_content_by_name = {
        "Arguments": "        value: sample value",
        "Raises": "        ValueError: always",
        "Returns": "        returned value",
        "Yields": "        generated value",
    }
    section_names = {first_section_name, second_section_name}
    signature = ""
    if "Arguments" in section_names:
        signature = "value"
    body_lines = []
    if "Raises" in section_names:
        body_lines.extend(("    if False:", "        raise ValueError"))
    if "Yields" in section_names:
        body_lines.append("    yield 1")
    if "Returns" in section_names:
        body_lines.append("    return 1")

    violations = get_sample_docstring_violations(
        f'''
def sample({signature}):
    """Sample function.

    {first_section_name}:
{section_content_by_name[first_section_name]}

    {second_section_name}:
{section_content_by_name[second_section_name]}
    """
{"\n".join(body_lines)}
'''
    )

    assert [violation.rule_id for violation in violations] == ["section-spacing"]
