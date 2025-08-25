import inspect

from typing import Callable, TYPE_CHECKING, Any

from telethon.tl.tlobject import TLRequest


if TYPE_CHECKING:
    from telethon_patch import TelegramClient


ExceptionFilterType = Callable[[Exception], bool]
ExceptionHandlerType = Callable[["TelegramClient", TLRequest, Exception], Any]


class ExceptionHandlerTools:
    """Инструменты для обработки исключений в клиенте."""

    _exception_handlers: list[tuple[ExceptionFilterType, ExceptionHandlerType]]

    def add_exception_handler(self, filter_func: ExceptionFilterType, handler: ExceptionHandlerType):
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

    def remove_exception_handler(self, filter_func: ExceptionFilterType, handler: ExceptionHandlerType):
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
