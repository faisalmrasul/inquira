"""Pipeline module — evaluation orchestration."""

from .evaluator import evaluate_query, generate_autofix_output, simulate_output

__all__ = ["evaluate_query", "generate_autofix_output", "simulate_output"]
