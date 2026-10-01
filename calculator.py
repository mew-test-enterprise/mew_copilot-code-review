"""Simple arithmetic calculator with helper functions and CLI support."""

from __future__ import annotations

import argparse
import ast
import sys
from typing import Union

Number = Union[int, float]


def _coerce_number(value: Number | str, name: str) -> Number:
    """Return a numeric value from a supported input."""
    if isinstance(value, bool):
        raise TypeError(f"{name} must be numeric, not boolean")
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError as exc:  # pragma: no cover - defensive branch
            raise TypeError(f"{name} must be numeric") from exc
    raise TypeError(f"{name} must be numeric")


def _normalize_result(value: Number) -> Number:
    """Keep integers human-friendly while preserving floating-point values."""
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def add(a: Number | str, b: Number | str) -> Number:
    """Return the sum of two numeric values."""
    left = _coerce_number(a, "a")
    right = _coerce_number(b, "b")
    return _normalize_result(left + right)


def subtract(a: Number | str, b: Number | str) -> Number:
    """Return the difference of two numeric values."""
    left = _coerce_number(a, "a")
    right = _coerce_number(b, "b")
    return _normalize_result(left - right)


def multiply(a: Number | str, b: Number | str) -> Number:
    """Return the product of two numeric values."""
    left = _coerce_number(a, "a")
    right = _coerce_number(b, "b")
    return _normalize_result(left * right)


def divide(a: Number | str, b: Number | str) -> Number:
    """Return the quotient of two numeric values."""
    left = _coerce_number(a, "a")
    right = _coerce_number(b, "b")
    if right == 0:
        raise ZeroDivisionError("division by zero")
    return _normalize_result(left / right)


def evaluate(expression: str) -> Number:
    """Safely evaluate a simple arithmetic expression.

    Supported operations: +, -, *, /, //, %, **, parentheses, and unary +/-.
    """
    if expression is None:
        raise ValueError("expression cannot be None")

    text = str(expression).strip()
    if not text:
        raise ValueError("expression cannot be empty")

    text = text.replace("^", "**")
    try:
        parsed = ast.parse(text, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"invalid expression: {expression!r}") from exc

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                if right == 0:
                    raise ZeroDivisionError("division by zero")
                return left / right
            if isinstance(node.op, ast.FloorDiv):
                if right == 0:
                    raise ZeroDivisionError("division by zero")
                return left // right
            if isinstance(node.op, ast.Mod):
                if right == 0:
                    raise ZeroDivisionError("division by zero")
                return left % right
            if isinstance(node.op, ast.Pow):
                return left ** right
            raise ValueError(f"unsupported operator: {type(node.op).__name__}")
        if isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            if isinstance(node.op, ast.USub):
                return -operand
            raise ValueError(f"unsupported unary operator: {type(node.op).__name__}")
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                return node.value
            raise ValueError("only numeric constants are allowed")
        if isinstance(node, ast.Num):
            return node.n
        raise ValueError(f"unsupported expression element: {type(node).__name__}")

    result = _eval(parsed)
    return _normalize_result(result)


def main(argv: list[str] | None = None) -> int:
    """Cli entry point for the calculator."""
    parser = argparse.ArgumentParser(description="Evaluate a simple arithmetic expression.")
    parser.add_argument(
        "expression",
        nargs="*",
        help="Arithmetic expression, for example: 2 + 3 * 4",
    )
    args = parser.parse_args(argv)

    if not args.expression:
        parser.error("an expression is required")

    expr = " ".join(args.expression)
    try:
        result = evaluate(expr)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
