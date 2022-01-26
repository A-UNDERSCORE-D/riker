from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, Awaitable, Callable, Sequence, TypeVar

from .command import Command

if TYPE_CHECKING:
    RETURNS = str | list[str] | None
    TAG_VALUE = tuple[
        str | list[str], str | list[str], str | list[str] | None, int | None
    ]

_F = TypeVar("_F", bound=Callable[..., Awaitable[RETURNS]] | Callable[..., RETURNS])

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
    for v in itertools.chain(x.__dict__.values(), x.__class__.__dict__.values()):
        if not hasattr(v, COMMAND_TAG):
            continue

        if not callable(v):
            raise ValueError(f"Decorator used on non-callable object {v} ({v!r})")

        res: TAG_VALUE = getattr(x, COMMAND_TAG)

        (name, help, permissions, arg_count) = res

        if isinstance(permissions, str):
            permissions = [permissions]

        out.append(Command(name, help, permissions, arg_count, v))

    return out
