def effective_roles(user):
    """
    Calculate the roles a user effectively possesses.

    Every authenticated user receives Employee.
    The user's department is also treated as a role.
    Explicitly assigned roles are retained.
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