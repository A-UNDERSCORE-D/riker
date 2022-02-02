from __future__ import annotations

import itertools
from ast import Call
from typing import Any, Awaitable, Callable, Sequence, TypeVar

from riker.command_args import Argument

from .command import Command

RETURNS = str | list[str] | None
TAG_VALUE = tuple[str | list[str], str | list[str], str | list[str] | None, int | None]
CALLABLE_METH = Callable[[Any, Argument], RETURNS]
CALLABLE = Callable[[Argument], RETURNS]
ACALLABLE_METH = Callable[[Any, Argument], Awaitable[RETURNS]]
ACALLABLE = Callable[[Argument], Awaitable[RETURNS]]


_F = TypeVar("_F", bound=CALLABLE | CALLABLE_METH | ACALLABLE | ACALLABLE_METH)

COMMAND_TAG = "__riker_command_marker"


def command(
    name: str | Sequence[str],
    help: list[str] | str | None = None,
    required_permissions: str | list[str] | None = None,
    required_args: int | None = None,
) -> Callable[[_F], _F]:
    """Mark command callbacks."""

    def decorate(f: _F) -> _F:
        if hasattr(f, COMMAND_TAG):
            raise ValueError(
                f"Command {name} defined twice? ({f} has attribute already)"
            )
        nonlocal help
        if help is None:
            help = f.__doc__

        if help == "":
            raise ValueError("Commands must have help responses")

        setattr(f, COMMAND_TAG, (name, help, required_permissions, required_args))
        return f

    return decorate


def scan_for_commands(x: object) -> list[Command]:
    """Find marked functions."""
    out = []
    for attr_name in itertools.chain(dir(x), dir(x.__class__)):
        attr = getattr(x, attr_name)
        if not hasattr(attr, COMMAND_TAG):
            continue

        if not callable(attr):
            raise ValueError(
                f"Decorator used on non-callable object {attr} ({attr!r} -- {x!r})"
            )

        res: TAG_VALUE = getattr(attr, COMMAND_TAG)

        (name, help, permissions, arg_count) = res

        if isinstance(permissions, str):
            permissions = [permissions]

        out.append(Command(name, help, permissions, arg_count, attr))

    return out
