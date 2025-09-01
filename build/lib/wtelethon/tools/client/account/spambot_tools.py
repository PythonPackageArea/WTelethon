import asyncio
import datetime
import os
from typing import Union, TYPE_CHECKING, Optional

from wtelethon import tl_types, tl_functions, tl_errors
from wtelethon import utils

from wtelethon.attachments.memory.types import Types as memory_types


if TYPE_CHECKING:
    from wtelethon import TelegramClient


class AccountSpambotTools:
    """Инструменты для проверки статуса блокировки через @spambot."""

    _spambot_id = "@spambot"

    async def load_spamblock_info(
        self: "TelegramClient",
        delete_dialog: bool = False,
    ) -> bool:
        """Проверяет статус блокировки аккаунта через @spambot.

        Анализирует ответ спамбота и определяет тип блокировки:
        - FREE: аккаунт не заблокирован
        - TEMPORARY: временная блокировка с датой окончания
        - PERMANENT: постоянная блокировка

        Args:
            delete_dialog: Если True, удаляет диалог с @spambot после проверки.

        Returns:
            True если проверка выполнена успешно.

        Example:
            >>> await client.load_spamblock_info()
            >>> if client.memory.spamblock_type == memory_types.spamblock_type.FREE:
            >>>     print("Аккаунт не заблокирован")
            >>> elif client.memory.spamblock_until_date:
            >>>     print(f"Блокировка до {client.memory.spamblock_until_date}")
        """

        message = None
        async with self.conversation(self._spambot_id) as conv:
            for _ in range(2):
                try:
                    await conv.send_message("/start")
                    message = await conv.get_response()
                    break

                except tl_errors.YouBlockedUserError:
                    await self(
                        tl_functions.contacts.UnblockRequest(id=self._spambot_id)
                    )

        if delete_dialog:
            await self.delete_dialog("@spambot")

        if message is None:
            raise ValueError("Message not found")

        is_reply_markup = message.reply_markup
        is_two_rows = len(message.reply_markup.rows) == 2
        message_has_url = any(
            [
                isinstance(_, tl_types.MessageEntityTextUrl)
                for _ in message.entities or []
            ]
        )

        if not all(
            [
                is_reply_markup,
                is_two_rows,
                not message_has_url,
            ]
        ):

            date = utils.extract_datetime_from_text(message.text)

            if date is None:
                self.memory.spamblock_type = memory_types.spamblock_type.PERMANENT
                self.memory.spamblock_until_date = None

            elif datetime.datetime.now(datetime.UTC) < date:
                self.memory.spamblock_type = memory_types.spamblock_type.TEMPORARY
                self.memory.spamblock_until_date = date

            else:
                raise ValueError("Spamblock type not correct")

        else:
            self.memory.spamblock_type = memory_types.spamblock_type.FREE
            self.memory.spamblock_until_date = None

        return True
