from enum import StrEnum


class Stage(StrEnum):
    IDEA = "IDEA"
    BRIEF_APPROVED = "BRIEF_APPROVED"
    RESEARCHING = "RESEARCHING"
    RESEARCH_GATE = "RESEARCH_GATE"
    THESIS_DEVELOPMENT = "THESIS_DEVELOPMENT"
    THESIS_APPROVAL = "THESIS_APPROVAL"
    OUTLINE_DEVELOPMENT = "OUTLINE_DEVELOPMENT"
    OUTLINE_APPROVAL = "OUTLINE_APPROVAL"
    DRAFTING = "DRAFTING"
    ADVERSARIAL_REVIEW = "ADVERSARIAL_REVIEW"
    CLAIM_AUDIT = "CLAIM_AUDIT"
    REVISION = "REVISION"
    VENUE_REVIEW = "VENUE_REVIEW"
    FINAL_REVIEW = "FINAL_REVIEW"
    APPROVED = "APPROVED"
    FORMATTED = "FORMATTED"
    SUBMISSION_READY = "SUBMISSION_READY"


ORDER = list(Stage)
FORWARD = {stage: ORDER[index + 1] for index, stage in enumerate(ORDER[:-1])}


def validate_transition(current: Stage, target: Stage, reason: str | None = None) -> None:
    if target == current:
        return
    if FORWARD.get(current) == target:
        return
    if ORDER.index(target) < ORDER.index(current) and reason and reason.strip():
        return
    raise ValueError("Forward transitions must advance one gate; backward transitions require a reason")
