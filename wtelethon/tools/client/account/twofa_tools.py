from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from wtelethon import TelegramClient


class AccountTwofaTools:
    """Инструменты для работы с двухфакторной авторизацией."""

    async def edit_2fa(
        self: "TelegramClient",
        current_password: Optional[str] = None,
        new_password: Optional[str] = None,
        email: Optional[str] = None,
        hint: str = "",
    ) -> bool:
        """Изменяет настройки двухфакторной авторизации и обновляет memory.

        Args:
            current_password: Текущий пароль 2FA.
            new_password: Новый пароль 2FA.
            email: Email для восстановления.
            hint: Подсказка для пароля.

        Returns:
            True если изменения прошли успешно.
        """
        result = await super().edit_2fa(
            current_password=current_password,
            new_password=new_password,
            email=email,
            hint=hint,
        )

        if result:
            self.memory.twofa = new_password or current_password
            self.memory.twofa_unknown = False

        return result

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
