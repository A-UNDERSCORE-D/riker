from contextlib import ExitStack

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

    b.add_command(Command("noperms", "noperms test", None, None, _simple))
    b.add_command(Command("oper", "oper test", ["oper"], None, _simple))
    b.add_command(Command("operad", "oper ad test", ["oper.ad"], None, _simple))
    b.add_command(
        Command("simplePerm", "simple permissions test", ["test"], None, _simple)
    )

    b.permissions = SimplePermissionHandler(
        mask_permissions={"*!*@derg": ["test"]},
        oper_permissions={"derg": ["test"]},
    )

    def _reply(target: str, message: str) -> None:
        current = getattr(b, "response", [])
        current.append([target, message])
        setattr(b, "response", current)

    b.reply = _reply

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

        print(id(command_handler))

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
        with ExitStack() as e:
            e.callback(self._clean_handler, command_handler)

            await command_handler.on_line(line, current_nick="bot")

            resp: list[list[str]] | None = getattr(command_handler, "response", None)

            assert resp == [expected]

    @staticmethod
    def _clean_handler(h: Beard) -> None:
        if hasattr(h, "response"):
            delattr(h, "response")

    async def test_help(self, command_handler: Beard) -> None:
        """Ensure that help commands return the expected data."""
        await command_handler.on_line(tokenise(_PFX + "~help"))

        assert getattr(command_handler, "response") == [
            [
                "test",
                "\x02HELP\x02, \x02NOPERMS\x02, \x02OPER\x02, \x02OPERAD\x02, \x02SIMPLEPERM\x02",
            ]
        ]

        self._clean_handler(command_handler)

        await command_handler.on_line(tokenise(_PFX + "~help help"))

        assert getattr(command_handler, "response") == [
            [
                "test",
                "Help for \x02HELP\x02: help [command_name] -- Provides help on other commands.",
            ]
        ]
