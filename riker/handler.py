from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from irctokens.line import Line

    from .command import Command
    from .permission import BasePermissionHandler


class Beard:
    """Handler for incoming PRIVMSGs that allows for command execution."""

    def __init__(
        self,
        prefix: str,
        reply: Callable[[str, str], None] | None = None,
        permissions: BasePermissionHandler | None = None,
    ) -> None:
        self._commands: dict[str, Command] = {}
        self.prefix: str = prefix
        self.reply: Callable[[str, str], None] = (
            reply if reply is not None else self._no_reply
        )

        self.logger = logging.getLogger("command_handler")
        self.permissions = permissions

    async def on_line(self, line: Line, current_nick: str | None = None) -> None:
        """
        Handle incoming PRIVMSG lines.

        If the line is not a PRIVMSG, on_line returns quickly.

        :param line: the irctokens.Line to handle
        :param current_nick: The current nick of the connection,
                             for use with nick: style command handling, defaults to None
        """
        if line.command != "PRIVMSG":
            return

        cmd, args = self.extract_cmd(line, current_nick)
        if cmd == "":
            return

        c = self._commands.get(cmd.upper(), None)
        if c is None:
            return

        target: str = line.params[0]
        if target[0] != "#":
            target = line.hostmask.nickname

        if c.permissions is not None and len(c.permissions) > 0:
            if self.permissions is None:
                raise ValueError(
                    "Cannot check permissions on a command with no permission handler"
                )

            perms = self.permissions.check_permissions(line)
            if perms != set(c.permissions):
                self.logger.info(
                    f"Denied access to command {cmd!r} for {line.source}"
                    f"(want {c.permissions}, got {perms})"
                )
                self.reply(target, "Access Denied.")
                return

        # at this point, permissions have passed etc.
        self.logger.info(f"Allowed access to {cmd!r} for {line.source}")
        split_args: list[str] = args.split(" ")

        res = await c.fire(args, split_args, line)

        if res is None:
            self.logger.debug(
                f"Command {cmd} returned no results (did it reply on its own?)"
            )
            return

        self.reply(target, res)

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

    def add_command(self, cmd: Command, name: str | None = None) -> None:
        """
        Add a command to this Handler instance.

        :param cmd: The command instance to add
        :param name: an override for the command name, used internally,
                     probably dont use this, defaults to None
        :raises ValueError: If the command already exists on the handler
        """
        cmd_name = name if name is not None else cmd.name

        if isinstance(cmd_name, list):
            for name in cmd_name:
                self.add_command(cmd, name=name)

            return

        if cmd_name.upper() in self._commands:
            raise ValueError(f"Command {cmd.name} already exists!")

        self._commands[cmd_name.upper()] = cmd
