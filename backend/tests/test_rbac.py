from app.rbac import effective_roles, can_access


def test_effective_roles():
    user = {
        "username": "john",
        "department": "Finance",
        "roles": ["Manager"],
    }

    roles = effective_roles(user)

    assert roles == {
        "Employee",
        "Finance",
        "Manager",
    }


def test_employee_role_is_added():
    user = {
        "username": "john",
        "department": "",
        "roles": [],
    }

    assert "Employee" in effective_roles(user)


def test_authenticated_document_access():
    user = {
        "username": "john",
        "department": "Finance",
        "roles": [],
    }

    metadata = {
        "access_scope": "authenticated",
        "allowed_roles": [],
    }

    assert can_access(user, metadata)


def test_department_document_access():
    user = {
        "username": "john",
        "department": "Finance",
        "roles": [],
    }

    metadata = {
        "access_scope": "restricted",
        "allowed_roles": ["Finance"],
    }

    assert can_access(user, metadata)


def test_unauthorized_document_access():
    user = {
        "username": "john",
        "department": "Finance",
        "roles": [],
    }

    metadata = {
        "access_scope": "restricted",
        "allowed_roles": ["HR"],
    }

    assert not can_access(user, metadata)


def test_anonymous_user_cannot_access():
    assert not can_access(
        None,
        {"access_scope": "authenticated"},
    )

def test_private_document_owner_access():
    user = {
        "username": "shaikh",
        "department": "Private",
        "roles": ["Owner"],
    }

    metadata = {
        "access_scope": "private",
        "owner": "shaikh",
        "allowed_users": ["shaikh"],
        "allowed_roles": [],
    }

    assert can_access(user, metadata)


def test_private_document_denies_other_user():
    user = {
        "username": "john",
        "department": "Finance",
        "roles": ["Manager"],
    }

    metadata = {
        "access_scope": "private",
        "owner": "shaikh",
        "allowed_users": ["shaikh"],
        "allowed_roles": [],
    }

    assert not can_access(user, metadata)


def test_private_document_allows_explicit_user():
    user = {
        "username": "john",
        "department": "Finance",
        "roles": [],
    }

    metadata = {
        "access_scope": "private",
        "owner": "shaikh",
        "allowed_users": ["shaikh", "john"],
        "allowed_roles": [],
    }

    assert can_access(user, metadata)
