import pytest
from irctokens.line import Line, tokenise

from riker import CommandHandler


@pytest.fixture
def command_handler() -> CommandHandler:
    """Pytest fixture that returns a CommandHandler instance."""
    return CommandHandler("~")


_PFX = ":test!test@test PRIVMSG bot :"


def _id(x: Line) -> str:
    print(x)
    if isinstance(x, Line):
        return x.params[-1]

    return str(x)


class TestHandler:
    """Test that CommandHandler behaves as expected."""

    @pytest.mark.parametrize(
        ("line", "expected"),
        (
            (tokenise(_PFX + "~test this is a test"), ("test", "this is a test")),
            (tokenise(_PFX + "bot: this is a test"), ("this", "is a test")),
            (tokenise(_PFX + "asdf"), ("", "")),
            (tokenise(_PFX + "notbot: bad"), ("", "")),
            (tokenise(_PFX + "!this shouldnt work"), ("", "")),
        ),
        ids=_id,
    )
    def test_handler_extract_params(
        self, line: Line, expected: tuple[str, str], command_handler: CommandHandler
    ) -> None:
        """Test that handler correctly extracts params."""
        cmd, args = command_handler.extract_cmd(line, "bot")

        assert (cmd, args) == expected
