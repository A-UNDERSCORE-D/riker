from __future__ import annotations

import abc

from irctokens.line import Line


class BasePermissionHandler(abc.ABC):
    """BasePermissionManager defines the interface for permission managers."""

    @abc.abstractmethod
    def check_permissions(self, line: Line) -> set[str]:
        """
        Return the permissions available to the sender of a given line.

        Do NOT modify line.

        :param line: The line to check permissions on
        :return: Any and all permissions a user on a given line may have
        """
        ...
