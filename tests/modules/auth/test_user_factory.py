from tests.factories import make_user


def test_make_user_returns_isolated_mutable_fields() -> None:
    first = make_user(groups=["admins"], permissions=["spec:read"])
    second = make_user(groups=["admins"], permissions=["spec:read"])

    first.groups.append("editors")
    first.permissions.append("spec:write")

    assert second.groups == ["admins"]
    assert second.permissions == ["spec:read"]
