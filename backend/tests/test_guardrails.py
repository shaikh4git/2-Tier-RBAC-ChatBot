from app.guardrails import apply_output_guardrails


def test_normal_answer_is_returned():
    answer = "The school office opens at 9 AM."

    user = {
        "username": "john",
        "department": "Finance",
        "roles": [],
    }

    assert apply_output_guardrails(answer, user) == answer


def test_sensitive_answer_blocked_for_employee():
    answer = "The SSN is 123-45-6789."

    user = {
        "username": "john",
        "department": "Finance",
        "roles": [],
    }

    result = apply_output_guardrails(answer, user)

    assert "cannot provide this response" in result


def test_sensitive_answer_allowed_for_hr():
    answer = "The SSN is 123-45-6789."

    user = {
        "username": "hruser",
        "department": "HR",
        "roles": [],
    }

    assert apply_output_guardrails(answer, user) == answer


def test_empty_answer():
    assert apply_output_guardrails("", {}) == ""