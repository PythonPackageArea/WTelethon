import asyncio
from typing import Optional

from wtelethon import (
    TelegramClient,
    MemoryAttachment,
    helpers,
    storages,
    utils,
)

from api_mock import ApiMock
from handlers import connect_error_handler
from logging_config import get_logger

api_mock = ApiMock()
logger = get_logger(__name__)


async def client_process(client: TelegramClient) -> None:
    """Основной процесс работы с клиентом"""
    session_name = client.memory.session_file
    proxy_info = f"{client.current_proxy.host}:{client.current_proxy.port}"

    logger.info(f"Подключение клиента {session_name} через прокси {proxy_info}")

    await client.connect()
    logger.debug(f"Клиент {session_name} подключен, проверка авторизации")

    await client.check_authorization()
    logger.info(f"Клиент {session_name} авторизован")


async def get_client() -> Optional[TelegramClient]:
    """Создание клиента из API данных"""
    logger.debug("Запрос данных клиента из API")
    session_data = api_mock.get_session_data()
    if session_data is None:
        logger.warning("Нет доступных данных клиента")
        return None

    logger.debug(f"Создание клиента для сессии {session_data.slug}")
    client = TelegramClient(
        session_data.string_session,
        memory_attachment=MemoryAttachment(
            api_id=session_data.api_id,
            api_hash=session_data.api_hash,
            device_model=session_data.device_model,
            system_version=session_data.system_version,
            app_version=session_data.app_version,
            lang_code=session_data.lang_code,
            system_lang_code=session_data.system_lang_code,
            layer=session_data.layer,
            slug=session_data.slug,
        ),
    )

    client.add_exception_handler(utils.is_connection_error, connect_error_handler)
    logger.debug("Клиент подобран и настроен")
    return client


async def _process() -> None:
    """Внутренний процесс обработки клиента"""
    client = await get_client()
    if client is None:
        logger.debug("Пропуск итерации - нет доступного клиента")
        return

    session_name = client.memory.slug

    try:
        logger.debug(f"Установка прокси для клиента {session_name}")
        client.set_proxy_from_storage()
    except Exception as e:
        logger.warning(f"Не удалось установить прокси для {session_name}: {e}")
        return

    try:
        await client_process(client)
        logger.debug(f"Обработка клиента {session_name} завершена успешно")
    except Exception as exc:
        await client.disconnect()
        logger.debug(f"Клиент {session_name} отключен после ошибки")

        if utils.is_dead_error(exc):
            logger.error(f"Клиент {session_name} мертв: {exc.__class__.__name__}")
            await api_mock.update_session_data(client.memory.slug, dead=True)
        elif utils.is_connection_error(exc):
            logger.warning(
                f"Ошибка подключения для {session_name}: {exc.__class__.__name__}"
            )
        else:
            logger.error(
                f"Необработанная ошибка для {session_name}: {exc}", exc_info=True
            )
            raise exc


async def run_service() -> None:
    """Запуск основного цикла сервиса"""
    logger.info("Основной цикл сервиса запущен")
    iteration = 0

    while True:
        iteration += 1
        logger.debug(f"Начало итерации #{iteration}")

        try:
            await _process()
        except Exception as e:
            logger.error(f"Ошибка в итерации #{iteration}: {e}", exc_info=True)

        logger.debug(f"Окончание итерации #{iteration}, ожидание 1 сек")
        await asyncio.sleep(1)
