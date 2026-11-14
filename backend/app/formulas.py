"""Safe evaluator for structured game formulas.

Dataset records describe formula trees as JSON. This module never executes Python
or JavaScript from data files.
"""
from __future__ import annotations

import math
from typing import Any, Mapping

_ALLOWED_OPERATIONS = {"add", "sub", "mul", "div", "min", "max"}


def evaluate_expression(expression: Mapping[str, Any], stats: Mapping[str, float]) -> float:
    """Evaluate a small, validated expression tree against a stat mapping.

    Examples:
      {"const": 120}
      {"stat": "physical_attack"}
      {"op": "add", "args": [{"const": 100}, {"op": "mul", "args": [
          {"stat": "physical_attack"}, {"const": 0.8}
      ]}]}
    """
    if not isinstance(expression, Mapping):
        raise ValueError("Each expression node must be an object")

    if set(expression) == {"const"}:
        value = _finite_number(expression["const"])
        return value

    if set(expression) == {"stat"}:
        name = expression["stat"]
        if not isinstance(name, str) or name not in stats:
            raise ValueError(f"Unknown stat: {name!r}")
        return _finite_number(stats[name])

    if set(expression) != {"op", "args"}:
        raise ValueError("Expression node must contain const, stat, or op and args")

    operation = expression["op"]
    args = expression["args"]
    if operation not in _ALLOWED_OPERATIONS or not isinstance(args, list) or len(args) < 2:
        raise ValueError("Unsupported operation or invalid argument list")

    values = [evaluate_expression(arg, stats) for arg in args]
    if operation == "add":
        result = sum(values)
    elif operation == "sub":
        if len(values) != 2:
            raise ValueError("sub requires exactly two arguments")
        result = values[0] - values[1]
    elif operation == "mul":
        result = math.prod(values)
    elif operation == "div":
        if len(values) != 2:
            raise ValueError("div requires exactly two arguments")
        if values[1] == 0:
            raise ValueError("Division by zero")
        result = values[0] / values[1]
    elif operation == "min":
        result = min(values)
    else:
        result = max(values)

    return _finite_number(result)


def _finite_number(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Formula values and stats must be numbers")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Formula values must be finite")
    return result
