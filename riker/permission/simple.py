from __future__ import annotations

from fnmatch import fnmatch

from base import BasePermissionHandler
from irctokens.line import Line

# spell-checker: words oper


class DefaultPermissionHandler(BasePermissionHandler):
    def __init__(self) -> None:
        self.mask_permissions: dict[str, list[str]] = {}
        self.enable_oper = True
        self.oper_permissions: dict[str, list[str]] = {}
        super().__init__()

    def check_masks(self, to_check: str) -> list[str]:
        out: list[str] = []

        for mask in self.mask_permissions:
            if fnmatch(to_check, mask):
                out.extend(self.mask_permissions[mask])

        return out

    def check_oper(self, oper_name: str) -> list[str]:
        if not self.enable_oper:
            return []

        out = []

        for name in self.oper_permissions:
            if fnmatch(oper_name, name):
                out.extend(self.oper_permissions[name])

        return out

    def check_permissions(self, line: Line) -> list[str]:
        """
        Return the permissions the sender of a given line has

        :param line: The line to check
        :return: a list of permission strings
        """
        out: list[str] = []
        out.extend(self.check_masks(str(line.hostmask)))

        if self.enable_oper and line.tags is not None and "oper" in line.tags:
            out.append("oper")

            if line.tags["oper"] != "":
                out.extend(self.check_oper(line.tags["oper"]))

        return super().check_permissions(line)
