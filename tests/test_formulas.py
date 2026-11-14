import pytest

from app.formulas import evaluate_expression


def test_constant_and_stat():
    assert evaluate_expression({"const": 125}, {}) == 125
    assert evaluate_expression({"stat": "magic_power"}, {"magic_power": 80}) == 80


def test_nested_scaling_expression():
    expression = {
        "op": "add",
        "args": [
            {"const": 100},
            {"op": "mul", "args": [{"stat": "physical_attack"}, {"const": 0.8}]},
        ],
    }
    assert evaluate_expression(expression, {"physical_attack": 200}) == 260


def test_unknown_stat_is_rejected():
    with pytest.raises(ValueError, match="Unknown stat"):
        evaluate_expression({"stat": "not_a_stat"}, {})


def test_division_by_zero_is_rejected():
    with pytest.raises(ValueError, match="Division by zero"):
        evaluate_expression({"op": "div", "args": [{"const": 1}, {"const": 0}]})


def test_arbitrary_expression_is_rejected():
    with pytest.raises(ValueError):
        evaluate_expression({"python": "__import__('os').system('echo no')"}, {})
