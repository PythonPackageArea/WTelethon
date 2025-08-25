import asyncio
import contextlib
from typing import Awaitable, Callable


async def run_fetch_task(
    fetch_task: Callable[[], Awaitable],
    interval: int = 60,
    *args,
    **kwargs,
) -> None:
    """Запускает периодическую задачу с указанным интервалом.

    Создаёт фоновую задачу, которая выполняет переданную функцию
    с заданным интервалом, игнорируя любые исключения.

    Args:
        fetch_task: Асинхронная функция для выполнения.
        interval: Интервал между выполнениями в секундах (по умолчанию 60).
        *args: Позиционные аргументы для функции.
        **kwargs: Именованные аргументы для функции.

    Example:
        >>> async def check_updates():
        >>>     print("Проверка обновлений...")
        >>>     # логика проверки
        >>>
        >>> # Запускать каждые 30 секунд
        >>> await run_fetch_task(check_updates, interval=30)
    """

    async def wrap_fetch_task():
        while True:
            with contextlib.suppress(Exception):
                await fetch_task(*args, **kwargs)

            await asyncio.sleep(interval)

    asyncio.create_task(wrap_fetch_task())
