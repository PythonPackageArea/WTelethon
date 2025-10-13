import inspect
import traceback

from typing import Awaitable, Callable, TYPE_CHECKING, Any, Optional, Union

from telethon.tl.tlobject import TLRequest


if TYPE_CHECKING:
    from wtelethon import TelegramClient


ExceptionFilterType = Callable[[Exception], bool]
ExceptionHandlerType = Callable[["TelegramClient", Optional[TLRequest], Exception], Optional[TLRequest]]


class ExceptionHandlerTools:
    """Инструменты для обработки исключений в клиенте."""

    _exception_handlers: list[tuple[ExceptionFilterType, ExceptionHandlerType]]

    async def handle_exception(
        self: "TelegramClient",
        request: Optional[TLRequest],
        exception: Exception,
    ):
        """Обрабатывает исключение."""
        for filter_func, handler in self._exception_handlers:
            if not filter_func(exception):
                continue

            coro = handler(self, request, exception)

            if inspect.iscoroutinefunction(handler):
                try:
                    coro = await coro
                except Exception as exc:
                    pass

            if coro and isinstance(coro, TLRequest):
                return await self(coro)

        if request:
            raise exception

    def add_exception_handler(
        self: "TelegramClient",
        filter_func: ExceptionFilterType,
        handler: ExceptionHandlerType,
    ):
        """Добавляет обработчик исключений.

        Args:
            filter_func: Функция фильтра, принимающая Exception и возвращающая bool.
            handler: Обработчик с сигнатурой (client, request, exception).

        Example:
            >>> def is_flood_error(exc):
            >>>     return isinstance(exc, FloodWaitError)
            >>>
            >>> def handle_flood(client, request, exc):
            >>>     print(f"Flood wait: {exc.seconds} seconds")
            >>>     raise exc
            >>>
            >>> client.add_exception_handler(is_flood_error, handle_flood)
        """
        if len(inspect.signature(handler).parameters) != 3:
            raise ValueError("Handler must have 3 arguments")

        if len(inspect.signature(filter_func).parameters) != 1:
            raise ValueError("Filter function must have 1 argument")

        self._exception_handlers.append((filter_func, handler))

    def remove_exception_handler(
        self: "TelegramClient",
        filter_func: ExceptionFilterType,
        handler: ExceptionHandlerType,
    ):
        """Удаляет обработчик исключений.

        Args:
            filter_func: Функция фильтра для поиска обработчика.
            handler: Функция обработчика для удаления.

        Raises:
            ValueError: Если обработчик не найден.

        Example:
            >>> client.remove_exception_handler(is_flood_error, handle_flood)
        """
        tuple_to_remove = (filter_func, handler)
        if tuple_to_remove not in self._exception_handlers:
            raise ValueError("Handler not found")

        self._exception_handlers.remove(tuple_to_remove)
