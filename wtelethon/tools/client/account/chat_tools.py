import asyncio
import datetime
import os
from typing import Union, TYPE_CHECKING, Optional

from telethon.helpers import TotalList
from wtelethon import tl_types, tl_functions, tl_errors
from wtelethon import utils, helpers


if TYPE_CHECKING:
    from wtelethon import TelegramClient


class AccountChatTools:
    """Инструменты для работы с чатами аккаунта."""

    async def join_public_channel(self: "TelegramClient", link: str) -> tl_types.TypeChat:
        """Присоединяется к каналу по ссылке.

        Args:
            link: Ссылка на канал.

        Returns:
            Объект чата.

        Example:
            >>> channel = await client.join_channel("https://t.me/joinchat/ABC123")
            >>> print(f"Присоединились к каналу: {channel.title}")
        """
        if utils.is_private_chat_link(link):
            raise ValueError("Invalid chat link")

        entity: tl_types.Channel | tl_types.Chat = await self.get_entity(link)
        if not utils.is_chat_or_channel_entity(entity):
            raise ValueError("Invalid chat link")

        if entity.left is True:
            entity = (await self(tl_functions.channels.JoinChannelRequest(link))).chats[0]

        return entity

    async def check_private_link(self: "TelegramClient", link: str) -> tl_types.ChatInvite:
        """Проверяет, является ли ссылка на приватный чат.

        Args:
            link: Ссылка на чат.

        Returns:
            Объект tl_types.ChatInvite.

        Raises:
            ValueError: Если ссылка не является приватным чатом.

        Example:
            >>> invite = await client.check_private_chat_link("https://t.me/joinchat/ABC123")
            >>> print(f"Ссылка на приватный чат: {invite.title}")
        """
        if not utils.is_private_chat_link(link):
            raise ValueError("Invalid chat link")

        link_hash = utils.get_private_link_hash(link)

        invite_type = await self(tl_functions.messages.CheckChatInviteRequest(link_hash))
        return invite_type

    async def import_private_link(self: "TelegramClient", link: str) -> tl_types.TypeChat:
        """Импортирует приватный чат по ссылке.

        Args:
            link: Ссылка на чат.


        Returns:
            Объект чата.

        Raises:
            ValueError: Если ссылка не является приватным чатом.

        Example:
            >>> chat = await client.import_private_link("https://t.me/joinchat/ABC123")
            >>> print(f"Импортированный чат: {chat.title}")
        """
        if not utils.is_private_chat_link(link):
            raise ValueError("Invalid chat link")

        link_hash = utils.get_private_link_hash(link)

        return (await self(tl_functions.messages.ImportChatInviteRequest(link_hash))).chats[0]

    async def subscribe(
        self: "TelegramClient",
        link: str,
        invite_requests_enabled: bool = True,
        invite_requests_timeout: int = 10,
    ) -> Union[tl_types.TypeChat, bool]:
        """Подписывается на канал по ссылке.

        Args:
            link: Ссылка на канал/чат (приватный или публичный).
            invite_requests_enabled: Флаг разрешения запросов на присоединение.
            invite_requests_timeout: Таймаут запросов на присоединение.

        Returns:
            Объект чата или False если не удалось подписаться.

        Example:
            >>> chat = await client.subscribe("https://t.me/joinchat/ABC123")
            >>> print(f"Подписан на канал: {chat.title}")
        """
        if not utils.is_private_chat_link(link):
            return await self.join_public_channel(link)

        for retry in [1, 2]:
            try:
                invite_type = await self.check_private_link(link)
                if isinstance(invite_type, tl_types.ChatInviteAlready):
                    return invite_type.chat

                if any(
                    [
                        retry == 2,
                        (isinstance(invite_type, tl_types.ChatInvite) and invite_requests_enabled is False),
                    ]
                ):
                    return False

                return await self.import_private_link(link)

            except Exception as exc:
                if isinstance(exc, tl_errors.InviteRequestSentError):
                    await asyncio.sleep(invite_requests_timeout)
                    continue

                raise exc

        return False
