def effective_roles(user):
    """
    Return all roles applicable to an authenticated user.

    Every authenticated user receives the Employee role.
    The user's department is also treated as a role.
    """
    roles = set(user.get("roles", []))
    roles.add("Employee")

    department = user.get("department")
    if department:
        roles.add(department)

    return roles


def can_access(user, metadata):
    """
    Check whether an authenticated user can access a document.

    Access is granted when:
    1. The document is available to all authenticated users, or
    2. The user has at least one role listed in allowed_roles.
    """
    if not user or not user.get("username"):
        return False

    if metadata.get("access_scope") == "authenticated":
        return True

    allowed_roles = set(metadata.get("allowed_roles", []))

    if not allowed_roles:
        return False

    user_roles = effective_roles(user)

    return bool(user_roles.intersection(allowed_roles))