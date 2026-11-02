"""Tests for the evaluation pipeline."""

from src.pipeline.evaluator import evaluate_query, generate_autofix_output


def test_evaluate_clean_query_allowed():
    verdict = evaluate_query(
        "professional.trust_query",
        "Verify TechCorp revenue growth.",
        "",
        "Priya Sharma",
    )
    assert verdict["allowed"] is True
    assert verdict["shield"]["allowed"] is True
    assert verdict["disclosure"] is not None


def test_evaluate_high_risk_without_approver_blocked():
    verdict = evaluate_query(
        "professional.trust_query",
        "Verify TechCorp revenue growth.",
        "",
        "",
    )
    assert verdict["allowed"] is False
    assert verdict["gate"]["allowed"] is False


def test_evaluate_prohibited_practice_blocked():
    verdict = evaluate_query(
        "professional.trust_query",
        "Create a social score to rank citizens.",
        "",
        "Priya Sharma",
    )
    assert verdict["allowed"] is False
    assert any(c["id"] == "prohibited_practices" and c["status"] == "fail"
               for c in verdict["checks"])


def test_limited_risk_student_allowed():
    verdict = evaluate_query(
        "student.trust_query",
        "Check my essay for ungrounded claims.",
        "",
        "",
    )
    assert verdict["allowed"] is True
    assert verdict["system"]["risk_tier"] == "limited"


def test_autofix_output_contains_disclosure():
    verdict = evaluate_query(
        "professional.trust_query",
        "Verify TechCorp revenue growth.",
        "",
        "Priya Sharma",
    )
    text = generate_autofix_output(verdict)
    assert "EU-Compliant Output" in text
    assert "Art. 50" in text or "disclosure" in text.lower()
