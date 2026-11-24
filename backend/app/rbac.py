
def effective_roles(user):
    roles = set(user.get("roles", []))
    roles.add("Employee")

    department = user.get("department")
    if department:
        roles.add(department)

    return roles


def can_access(user, metadata):
    if not user or not user.get("username"):
        return False

    username = user["username"].lower()

    # Private documents: allow only the owner or explicitly allowed users.
    if metadata.get("access_scope") == "private":
        owner = str(metadata.get("owner", "")).lower()
        allowed_users = {
            str(name).lower()
            for name in metadata.get("allowed_users", [])
        }

        return username == owner or username in allowed_users

    # Existing authenticated-document access.
    if metadata.get("access_scope") == "authenticated":
        return True

    # Existing role-based access.
    allowed_roles = set(metadata.get("allowed_roles", []))
    if not allowed_roles:
        return False

    user_roles = effective_roles(user)
    return bool(user_roles.intersection(allowed_roles))
