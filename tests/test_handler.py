import pytest
from irctokens.line import Line, tokenise

from riker import Beard, SimplePermissionHandler
from riker.command import Command

# spell-checker: words noperms oper derg blarg


async def _simple(args: list[str]) -> str:
    return " ".join(args)


@pytest.fixture(scope="session")
def command_handler() -> Beard:
    """Pytest fixture that returns a CommandHandler instance."""
    b = Beard("~")

    b.add_command(Command("noperms", "test", None, None, _simple))
    b.add_command(Command("oper", "test", ["oper"], None, _simple))
    b.add_command(Command("operad", "test", ["oper.ad"], None, _simple))
    b.add_command(Command("simplePerm", "test", ["test"], None, _simple))

    b.permissions = SimplePermissionHandler(
        mask_permissions={"*!*@derg": ["test"]},
        oper_permissions={"derg": ["test"]},
    )

    b.reply = lambda target, msg: setattr(b, "response", [target, msg])

    return b


_PFX = ":test!test@test PRIVMSG bot :"


def _id(x: Line) -> str:
    print(x)
    if isinstance(x, Line):
        return x.params[-1]

    return str(x)


_t = tokenise


class TestHandler:
    """Test that CommandHandler behaves as expected."""

    @pytest.mark.parametrize(
        ("line", "expected"),
        (
            (tokenise(_PFX + "~test this is a test"), ("test", "this is a test")),
            (tokenise(_PFX + "bot: this is a test"), ("this", "is a test")),
            (tokenise(_PFX + "asdf"), ("", "")),
            (tokenise(_PFX + "notbot: bad"), ("", "")),
            (tokenise(_PFX + "!this shouldn't work"), ("", "")),
        ),
        ids=_id,
    )
    def test_handler_extract_params(
        self, line: Line, expected: tuple[str, str], command_handler: Beard
    ) -> None:
        """Test that handler correctly extracts params."""
        cmd, args = command_handler.extract_cmd(line, "bot")

        assert (cmd, args) == expected

    @pytest.mark.parametrize(
        ("line", "expected"),
        (
            (_t(_PFX + "~noperms noperms test"), (["test", "noperms test"])),
            (_t(_PFX + "~oper test"), ["test", "Access Denied."]),
            (
                _t("@oper :someOper!ahh@blarg PRIVMSG bot :~oper test but results!"),
                ["someOper", "test but results!"],
            ),
        ),
    )
    async def test_on_command(
        self,
        command_handler: Beard,
        line: Line,
        expected: list[str] | None,
    ) -> None:
        """Ensure that commands are correctly dispatched."""

        await command_handler.on_line(line, current_nick="bot")

        resp: list[str] | None = getattr(command_handler, "response", None)

        assert resp == expected
