from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from telethon_patch import TelegramClient


class AccountTwofaTools:
    """Инструменты для работы с двухфакторной авторизацией."""

    async def check_twofa(
        self: "TelegramClient",
        twofa: Optional[str] = None,
    ) -> bool:
        """Проверяет двухфакторную авторизацию.

        Args:
            twofa: Текущий пароль двухфакторной авторизации.

        Returns:
            True если авторизация прошла успешно.

        Example:
            >>> await client.check_twofa("123456")
            >>> if client.memory.unknown_twofa is True:
            >>>     print("Двухфакторная авторизация неизвестна")
        """
        twofa = (twofa or "").strip(" ")

        try:
            assert await self.edit_2fa(current_password=twofa)
            self.memory.twofa = twofa
            self.memory.twofa_unknown = False

        except Exception:
            if self.memory.twofa and twofa != self.memory.twofa:
                return await self.check_twofa(self.memory.twofa)

        return True
