#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared scalar and iterable contracts for numeric validators."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import nullcontext
from typing import Any

import pytest

from pipescaler.common.exceptions import ArgumentConflictError
from pipescaler.common.validation import val_float, val_int


@pytest.mark.parametrize("validator", [val_int, val_float])
@pytest.mark.parametrize(
    "value, options, expected, error",
    [
        pytest.param(5, {}, 5, None, id="integer"),
        pytest.param(5.0, {}, 5, None, id="float"),
        pytest.param("5", {}, 5, None, id="string"),
        pytest.param(-3, {}, -3, None, id="negative"),
        pytest.param([1, 2, 3], {}, [1, 2, 3], None, id="list"),
        pytest.param((1.0, 2.0, 3.0), {}, [1, 2, 3], None, id="tuple"),
        pytest.param(["1", "2", "3"], {}, [1, 2, 3], None, id="string-list"),
        pytest.param([], {"n_values": 0}, [], None, id="empty"),
        pytest.param(
            [1, 2, 3],
            {"n_values": 3, "min_value": 0, "max_value": 4},
            [1, 2, 3],
            None,
            id="bounded-list",
        ),
        pytest.param(None, {}, None, (TypeError, None), id="none"),
        pytest.param("invalid", {}, None, (TypeError, None), id="invalid-string"),
        pytest.param(
            [1, "invalid", 3], {}, None, (TypeError, None), id="invalid-element"
        ),
        pytest.param(
            5,
            {"min_value": 5, "max_value": 5},
            None,
            (ArgumentConflictError, "min_value must be less than"),
            id="conflicting-bounds",
        ),
        pytest.param(
            -1,
            {"min_value": 0},
            None,
            (ValueError, "less than minimum"),
            id="below-minimum",
        ),
        pytest.param(
            11,
            {"max_value": 10},
            None,
            (ValueError, "greater than maximum"),
            id="above-maximum",
        ),
        pytest.param(
            [1, -1, 3],
            {"min_value": 0},
            None,
            (ValueError, "less than minimum"),
            id="element-below-minimum",
        ),
        pytest.param(
            [1, 11, 3],
            {"max_value": 10},
            None,
            (ValueError, "greater than maximum"),
            id="element-above-maximum",
        ),
        pytest.param(
            [1, 2],
            {"n_values": 3},
            None,
            (ValueError, "is of length"),
            id="wrong-length",
        ),
    ],
)
def test_numeric_validation(
    validator: Callable[..., Any],
    value: Any,
    options: dict[str, Any],
    expected: object,
    error: tuple[type[Exception], str | None] | None,
):
    """Apply shared conversion and constraint rules with independent failure cases.

    Arguments:
        validator: numeric validator under test
        value: valid or intentionally invalid input
        options: validation constraints
        expected: converted value on success
        error: expected exception and diagnostic fragment, or none for success
    """
    with pytest.raises(error[0], match=error[1]) if error else nullcontext():
        result = validator(value, **options)
        assert result == expected
        values = result if isinstance(result, list) else [result]
        scalar_type = int if validator is val_int else float
        assert all(type(item) is scalar_type for item in values)


@pytest.mark.parametrize("validator", [val_int, val_float])
def test_numeric_generator(validator: Callable[..., Any]):
    """Consume one-shot iterable input into a list of converted values.

    Arguments:
        validator: numeric validator under test
    """
    assert validator(value for value in [1, 2, 3]) == [1, 2, 3]


@pytest.mark.parametrize("value", [11, [1, 5]])
def test_integer_acceptable_values(value: int | list[int]):
    """Reject disallowed scalar and iterable integer values.

    Arguments:
        value: input containing a disallowed integer
    """
    with pytest.raises(ValueError, match="is not one of"):
        val_int(value, acceptable_values=[1, 2, 3])
