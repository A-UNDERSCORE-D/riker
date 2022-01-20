from riker.command import Command


class TestCommand:
    """Test that the implementation of Command behaves as expected."""

    @staticmethod
    async def _throwaway_callback(args: str) -> None:
        pass

    async def test_simple_command(self) -> None:
        """Test that command args are split correctly, and that async code is called."""
        called = False

        async def test_func(args: list[str]) -> None:
            nonlocal called
            called = True

        c = Command("test", "test command", None, None, test_func)

        await c.fire("str args", ["str", "args"], None)

        assert called
