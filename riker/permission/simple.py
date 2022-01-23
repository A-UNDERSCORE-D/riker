from __future__ import annotations

from fnmatch import fnmatch

from irctokens.line import Line

from .base import BasePermissionHandler

# spell-checker: words oper


class SimplePermissionHandler(BasePermissionHandler):
    """SimplePermissionHandler implements a mask and oper based permission handler."""

    def __init__(
        self,
        mask_permissions: dict[str, list[str]],
        enable_oper: bool = True,
        oper_permissions: dict[str, list[str]] | None = None,
    ) -> None:

        self.mask_permissions: dict[str, list[str]] = mask_permissions
        self.enable_oper = enable_oper
        self.oper_permissions: dict[str, list[str]] = (
            oper_permissions if oper_permissions is not None else {}
        )

    def _check_masks(self, to_check: str) -> list[str]:
        out: list[str] = []

        for mask in self.mask_permissions:
            if fnmatch(to_check, mask):
                out.extend(self.mask_permissions[mask])

        return out

    def _check_oper(self, oper_name: str) -> list[str]:
        out = []

        for name in self.oper_permissions:
            if fnmatch(oper_name, name):
                out.extend(self.oper_permissions[name])

        return out

    def check_permissions(self, line: Line) -> set[str]:
        """
        Return the permissions the sender of a given line has.

        :param line: The line to check
        :return: a list of permission strings
        """
        out: set[str] = set()
        out.update(self._check_masks(str(line.hostmask)))

        if self.enable_oper and line.tags is not None and "oper" in line.tags:
            out.add("oper")

            if line.tags["oper"] != "":
                out.update(self._check_oper(line.tags["oper"]))
                out.add(f'oper.{line.tags["oper"]}')

        return out
