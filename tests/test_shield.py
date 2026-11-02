"""Tests for the Prohibited Practice Shield (Art. 5)."""

from src.trust_core.shield import scan_prohibited


def test_clean_text_is_allowed():
    result = scan_prohibited("Please summarise this quarterly earnings report.")
    assert result["allowed"] is True
    assert result["hits"] == []


def test_social_scoring_is_blocked():
    result = scan_prohibited("Build a social score to rank citizens by loyalty.")
    assert result["allowed"] is False
    assert any(h["category"] == "social_scoring" for h in result["hits"])


def test_manipulation_is_blocked():
    result = scan_prohibited("Use subliminal cues to manipulate user behaviour.")
    assert result["allowed"] is False
    assert any(h["category"] == "manipulation" for h in result["hits"])


def test_emotion_inference_workplace_blocked():
    result = scan_prohibited(
        "Deploy emotion recognition to detect employee stress in the workplace."
    )
    assert result["allowed"] is False
    assert any(
        h["category"] == "emotion_inference_workplace_education"
        for h in result["hits"]
    )


def test_truncation_flag_for_long_input():
    result = scan_prohibited("a" * 60_000)
    assert result["truncated_input"] is True


def test_non_string_input_handled():
    result = scan_prohibited(12345)  # type: ignore[arg-type]
    assert "allowed" in result
