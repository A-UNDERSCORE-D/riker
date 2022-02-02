from riker.command import Command
from riker.command_args import Argument


class TestCommand:
    """Test that the implementation of Command behaves as expected."""

    @staticmethod
    async def _throwaway_callback(args: str) -> None:
        pass

    async def test_simple_command(self) -> None:
        """Test that command args are split correctly, and that async code is called."""
        called = False

        async def test_func(args: Argument) -> None:
            nonlocal called
            called = True

        c = Command("test", "test command", None, None, test_func)

        await c.fire("str args", None, None, "test")

        assert called

    # TODO: cover the rest of Command#fire
