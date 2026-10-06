import pytest
from app.workflow import Stage, validate_transition


def test_allows_single_forward_step():
    validate_transition(Stage.IDEA, Stage.BRIEF_APPROVED)


def test_rejects_skipped_gate():
    with pytest.raises(ValueError):
        validate_transition(Stage.IDEA, Stage.RESEARCHING)


def test_backward_requires_reason():
    with pytest.raises(ValueError):
        validate_transition(Stage.VENUE_REVIEW, Stage.THESIS_DEVELOPMENT)
    validate_transition(Stage.VENUE_REVIEW, Stage.THESIS_DEVELOPMENT, "Insufficient novelty")
