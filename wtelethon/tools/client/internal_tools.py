import inspect
from typing import TYPE_CHECKING

from telethon.client import UserMethods
from wtelethon import utils

if TYPE_CHECKING:
    from wtelethon import TelegramClient


class InternalTools:
    async def _call(
        self: "TelegramClient",
        sender,
        request,
        ordered=False,
        flood_sleep_threshold=None,
    ) -> "TelegramClient":
        try:
            self.memory.dead_error = False
            return await UserMethods._call(
                self, sender, request, ordered, flood_sleep_threshold
            )

        except Exception as exc:
            if utils.is_dead_error(exc):
                self.memory.dead_error = exc.__class__.__name__

            return await self.handle_exception(request, exc)
