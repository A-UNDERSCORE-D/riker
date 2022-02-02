from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeGuard, Union

from .command_args import Argument

if TYPE_CHECKING:
    from irctokens.line import Line

    CALLBACK = Union[
        Callable[[Argument], str | list[str] | None],
        Callable[[Argument], Awaitable[str | list[str] | None]],
    ]

# spell-checker: words iscoroutinefunction


@dataclass
class Command:
    """Command represents a single command with a callback function."""

    name: str | list[str]
    help: str | list[str]
    permissions: list[str] | None
    arg_count: int | None

    callback: CALLBACK
    allow_inspection: bool = True
    override_params: list[str] | None = None

    async def fire(
        self,
        args: str,
        raw_line: Line | None,
        bot_nick: str | None,
        command: str,
        **extra: dict[str, Any]
    ) -> str | list[str] | None:
        """
        Execute self.callback, creating the argument object as requested.
        """

        args_to_send = Argument(
            line=raw_line,
            args_str=args,
            command=command,
            bot_nick=bot_nick,
            extra_data=extra,
        )

        return await self._call(args_to_send)

    @staticmethod
    def _awaitable(
        c: CALLBACK,
    ) -> TypeGuard[Callable[[Argument], Awaitable[str | None]]]:
        return inspect.iscoroutinefunction(c)

    async def _call(self, args: Argument) -> str | list[str] | None:
        cb = self.callback
        if self._awaitable(self.callback):
            return await self.callback(args)

        return cb(args)  # type: ignore -- blame mypy
