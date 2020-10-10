def get_scope_list_from_string(scope_string: str):
    """Returns a list of scopes from space-seperated scope string.

    Args:
        scope_string (str): Space-seperated scopes string (ie. "user:edit+user:read:email")

    Returns:
        list: List containing strings of each scope specified.

    """
    scope_string.replace("+", " ")
    return scope_string.split(" ")
