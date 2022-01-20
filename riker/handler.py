from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from irctokens.line import Line

    from .command import Command


class CommandHandler:
    """Handler for incoming PRIVMSGs that allows for command execution."""

    def __init__(
        self, prefix: str, reply: Callable[[str, str], None] | None = None
    ) -> None:
        self.commands: dict[str, Command] = {}
        self.prefix: str = prefix
        self.reply: Callable[[str, str], None] = (
            reply if reply is not None else self._no_reply
        )

        self.logger = logging.getLogger("command_handler")

    def on_line(self, line: Line, current_nick: str | None = None) -> None:
        """Handle incoming PRIVMSG lines.

        If the line is not a PRIVMSG, on_line returns quickly.

        :param line: the irctokens.Line to handle
        :param current_nick: The current nick of the connection,
                             for use with nick: style command handling, defaults to None
        """
        if line.command != "PRIVMSG":
            return

    def extract_cmd(self, line: Line, current_nick: str | None) -> tuple[str, str]:
        """
        Extract the command and arguments from a given line.

        This does not check the command. It simply blindly uses it.

        :param line: The line to check
        :param current_nick: The nick to use for `nick:` style command execution
        :return: the command and arguments, if any
        """
        msg: str = line.params[-1]

        cmd, _, args = msg.partition(" ")

        if not cmd.startswith(self.prefix):
            if (
                current_nick is None
                or not cmd.startswith(current_nick)
                or not len(cmd) < len(current_nick) + 2
            ):
                return "", ""

            cmd, _, args = args.partition(" ")

        else:
            try:
                cmd = cmd.removeprefix(self.prefix)

            except AttributeError:
                cmd = cmd[len(self.prefix) :]

        return cmd, args

    def _no_reply(self, target: str, msg: str) -> None:
        self.logger.warning(
            f"No reply function for command. reply was to {target!r}: {msg!r}"
        )
