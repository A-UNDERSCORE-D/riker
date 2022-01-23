import irctokens
import pytest

from riker.permission import BasePermissionHandler, SimplePermissionHandler


# spell-checker: words oper nooper
class TestSimplePermissionHandler:
    """Verify that PermissionHandlers are behaving as expected."""

    @staticmethod
    def _get_handler() -> BasePermissionHandler:
        return SimplePermissionHandler(
            oper_permissions={"ad": ["dergon"]},
            mask_permissions={"*!*@test/staff/*": ["staff"]},
        )
        ...

    @pytest.mark.parametrize(
        ("line", "expected"),
        [
            [":nobody!test@test PRIVMSG theBot :!some_command", set()],
            ["@oper :someOper!magic@host PRIVMSG thebot :!some_command", {"oper"}],
            [
                "@oper :someOper!magic@test/staff/someone PRIVMSG thebot :!some_command",
                {"oper", "staff"},
            ],
            [
                "@oper=ad :someOper!magic@test/staff/someone PRIVMSG thebot :!some_command",
                {"oper", "oper.ad", "staff", "dergon"},
            ],
        ],
    )
    def test_normal(self, line: str, expected: set[str]) -> None:
        """Test that a normally configured SimplePermissionHandler behaves as expected."""
        parsed = irctokens.line.tokenise(line)
        handler = self._get_handler()

        perms = handler.check_permissions(parsed)

        assert set(perms) == expected

    def test_no_oper(self) -> None:
        """Test that a SimplePermissionHandler with oper support disabled does so."""
        handler = SimplePermissionHandler({}, enable_oper=False)

        assert (
            handler.check_permissions(
                irctokens.line.tokenise("@oper :test PRIVMSG asd :asdf")
            )
            == set()
        )
