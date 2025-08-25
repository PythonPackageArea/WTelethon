import asyncio
import datetime
import os
from typing import Union, TYPE_CHECKING, Optional


from telethon_patch import tl_types, tl_functions, tl_errors
from telethon_patch import utils


if TYPE_CHECKING:
    from telethon_patch import TelegramClient


class AccountHelpTools:
    """Инструменты для получения справочной информации аккаунта."""
    async def load_premium_info(
        self: "TelegramClient",
    ) -> Optional[datetime.datetime]:
        """Загружает информацию о статусе Premium аккаунта.
        
        Returns:
            Дата окончания подписки Premium или None если подписки нет.
            
        Example:
            >>> premium_until = await client.load_premium_info()
            >>> if premium_until:
            >>>     print(f"Premium до {premium_until}")
            >>> else:
            >>>     print("Обычный аккаунт")
        """

        response: tl_types.help.PremiumPromo = await self(
            tl_functions.help.GetPremiumPromoRequest()
        )

        dt = utils.extract_datetime_from_text(response.status_text)
        self.memory.premium_status = True if dt is not None else False
        self.memory.premium_until_date = dt

        return self.memory.premium_until_date

    async def load_app_config_info(
        self: "TelegramClient",
    ) -> bool:
        """Загружает конфигурацию приложения включая информацию о заморозках аккаунта.
        
        Обновляет поля memory: freeze_since_date, freeze_until_date, freeze_appeal_url.
        
        Returns:
            True если конфигурация успешно загружена.
            
        Example:
            >>> await client.load_app_config_info()
            >>> if client.memory.freeze_since_date:
            >>>     print(f"Аккаунт заморожен с {client.memory.freeze_since_date}")
        """
        response: tl_types.help.AppConfig = await self(
            tl_functions.help.GetAppConfigRequest(0)
        )
        for json_config_item in response.config.value:
            key = json_config_item.key
            value = json_config_item.value.value

            match key:
                case "freeze_since_date":
                    self.memory.freeze_since_date = datetime.datetime.fromtimestamp(
                        value
                    )
                case "freeze_until_date":
                    self.memory.freeze_until_date = datetime.datetime.fromtimestamp(
                        value
                    )
                case "freeze_appeal_url":
                    self.memory.freeze_appeal_url = value

        return True

    async def get_contacts(
        self: "TelegramClient",
        req_hash: int = 0,
    ) -> list[tl_types.User]:
        """Получает список контактов аккаунта.
        
        Args:
            req_hash: Хэш для кеширования (по умолчанию 0).
            
        Returns:
            Список пользователей из контактов.
            
        Example:
            >>> contacts = await client.get_contacts()
            >>> print(f"Количество контактов: {len(contacts)}")
            >>> for contact in contacts[:5]:  # первые 5
            >>>     print(f"{contact.first_name} {contact.username}")
        """
        response: tl_types.contacts.Contacts = await self(
            tl_functions.contacts.GetContactsRequest(req_hash)
        )
        self.memory.contacts_count = response.saved_count
        return response.users
