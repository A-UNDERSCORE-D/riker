from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeGuard, Union

if TYPE_CHECKING:
    from irctokens.line import Line

    CALLBACK = Union[
        Callable[..., str | list[str] | None],
        Callable[..., Awaitable[str | list[str] | None]],
    ]

# spell-checker: words iscoroutinefunction


@dataclass
class Command:
    """Command represents a single command with a callback function."""

    name: str | list[str]
    help: str | list[str]
    permissions: list[str] | None
    arg_count: int | None

    callback: Callable[..., Awaitable[str | None]] | Callable[..., str | None]
    allow_inspection: bool = True
    override_params: list[str] | None = None

    async def fire(
        self,
        args_str: str,
        args: list[str],
        raw_line: Line | None,
        **kwargs: dict[str, Any]
    ) -> str | list[str] | None:
        """
        Execute self.callback, dynamically provide any extra data it requests.

        Note that this does not do *ANY* permission checking.
        Its expected that callers verify perms.
        """
        if not self.allow_inspection:
            return await self._call(args_str)

        passable = {
            "args": args,
            "args_str": args_str,
            "raw_line": raw_line,
        }

        if self.override_params is not None:
            return await self._call(
                *(passable[n] for n in self.override_params if n in passable)
            )

        # inspect the signature to find what we want to pass

        to_pass: dict[str, Any] = {}
        to_pass.update(kwargs)

        sig = inspect.signature(self.callback)

        params = sig.parameters

        for name in params.keys():
            if name in passable:
                to_pass[name] = passable[name]

        return await self._call(**to_pass)

    @staticmethod
    def _awaitable(
        c: Callable[..., Awaitable[str | None]] | Callable[..., str | None]
    ) -> TypeGuard[Callable[..., Awaitable[str | None]]]:
        return inspect.iscoroutinefunction(c)

    async def _call(self, *args: Any, **kwargs: Any) -> str | list[str] | None:
        if self._awaitable(self.callback):
            return await self.callback(*args, **kwargs)

        # It must be the non-async version
        cb: Callable[..., str | list[str] | None] = self.callback  # type: ignore
        return cb(*args, **kwargs)
