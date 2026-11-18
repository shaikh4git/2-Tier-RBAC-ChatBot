import re

from .rbac import effective_roles


SSN_PATTERN = re.compile(
    r"\b\d{3}-\d{2}-\d{4}\b"
)

CREDIT_CARD_PATTERN = re.compile(
    r"\b(?:\d[ -]*?){13,19}\b"
)


def apply_output_guardrails(answer, user):
    """
    Prevent unauthorized users from receiving responses containing
    apparent Social Security numbers or credit card numbers.
    """
    if not answer:
        return answer

    contains_sensitive_data = bool(
        SSN_PATTERN.search(answer)
        or CREDIT_CARD_PATTERN.search(answer)
    )

    if not contains_sensitive_data:
        return answer

    roles = effective_roles(user)

    if roles.intersection({"HR", "C-Level"}):
        return answer

    return (
        "I’m sorry, but I cannot provide this response because "
        "it may contain sensitive personal or financial information."
    )