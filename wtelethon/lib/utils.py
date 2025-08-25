import datetime
import base64
import random
import re
import os
import struct
import phonenumbers
from phonenumbers import timezone as phonenumbers_timezone
from typing import Optional, TYPE_CHECKING
import pytz
from wtelethon import tl_errors, models, tl_types
import urllib.parse

if TYPE_CHECKING:
    from wtelethon import TelegramClient


def get_dc_address(dc_id: int) -> Optional[str]:
    """Получает случайный IP-адрес для указанного дата-центра.

    Args:
        dc_id: ID дата-центра Telegram (1-5).

    Returns:
        IP-адрес дата-центра или None если ID неверный.

    Example:
        >>> ip = get_dc_address(2)
        >>> print(f"DC2 IP: {ip}")  # "149.154.167.51"
    """
    return random.choice(models.TGDC.get(dc_id, [None]))


def get_push_token_type(api_id: int) -> Optional[int]:
    """Определяет тип push-токена по API ID.

    Args:
        api_id: API ID приложения.

    Returns:
        Тип push-токена или None если не найден.

    Example:
        >>> token_type = get_push_token_type(8)
        >>> print(f"Push token type: {token_type}")  # 1
    """
    return next(
        (
            token_type
            for token_type, api_ids in models.API_IDS_BY_PUSH_TOKEN_TYPE.items()
            if api_id in api_ids
        ),
        None,
    )


def get_voip_token_type(api_id: int) -> Optional[int]:
    """Определяет тип VoIP-токена по API ID.

    Args:
        api_id: API ID приложения.

    Returns:
        Тип VoIP-токена или None если не найден.

    Example:
        >>> voip_type = get_voip_token_type(8)
        >>> print(f"VoIP token type: {voip_type}")  # 9
    """
    return next(
        (
            token_type
            for token_type, api_ids in models.API_IDS_BY_VOIP_TOKEN_TYPE.items()
            if api_id in api_ids
        ),
        None,
    )


def find_code_in_text(text: str) -> Optional[str]:
    """Извлекает код авторизации из текста сообщения.

    Ищет 5-значный код после символа ':' в тексте сообщения от Telegram.

    Args:
        text: Текст сообщения для поиска кода.

    Returns:
        Найденный код или None если код не найден.

    Example:
        >>> message = "Ваш код: 12345. Никому его не сообщайте."
        >>> code = find_code_in_text(message)
        >>> print(f"Код: {code}")  # "12345"
    """
    start_index = text.find(":")

    if start_index != -1:
        return text[start_index + 2 : start_index + 7]


def extract_datetime_from_text(
    text, date_pattern: str = r"\b(\d{2})\.(\d{2})\.(\d{4})\b"
) -> Optional[datetime.datetime]:
    """Извлекает дату из текста с помощью регулярного выражения.

    Args:
        text: Текст для поиска даты.
        date_pattern: Шаблон поиска даты (по умолчанию DD.MM.YYYY).

    Returns:
        Объект datetime или None если дата не найдена.

    Example:
        >>> text = "Аккаунт заблокирован до 25.12.2024"
        >>> date = extract_datetime_from_text(text)
        >>> print(f"Дата: {date}")  # 2024-12-25 00:00:00+00:00
    """
    match = re.search(date_pattern, text)
    if match:
        day, month, year = map(int, match.groups())
        return datetime.datetime(year, month, day, tzinfo=datetime.UTC)


def is_dead_error(exc: Exception) -> bool:
    """Проверяет, является ли исключение критической ошибкой авторизации.

    Args:
        exc: Исключение для проверки.

    Returns:
        True если исключение означает "мёртвую" сессию.

    Example:
        >>> try:
        >>>     await client.get_me()
        >>> except Exception as e:
        >>>     if is_dead_error(e):
        >>>         print("Сессия недействительна, требуется повторная авторизация")
    """
    return isinstance(exc, models.DEAD_EXCEPTIONS)


def is_connection_error(exc: Exception) -> bool:
    """Проверяет, является ли исключение ошибкой соединения.

    Args:
        exc: Исключение для проверки.

    Returns:
        True если это ошибка соединения.

    Example:
        >>> try:
        >>>     await client.connect()
        >>> except Exception as e:
        >>>     if is_connection_error(e):
        >>>         print("Проблемы с подключением к серверу")
    """
    return isinstance(exc, ConnectionError)


def is_recaptcha_error(exc: Exception) -> bool:
    """Проверяет, требует ли исключение решения reCAPTCHA.

    Args:
        exc: Исключение для проверки.

    Returns:
        True если требуется решение reCAPTCHA.

    Example:
        >>> try:
        >>>     await client.send_message(chat, "Hello")
        >>> except Exception as e:
        >>>     if is_recaptcha_error(e):
        >>>         print("Требуется решить капчу")
    """
    return isinstance(exc, tl_errors.ForbiddenError) and "RECAPTCHA_CHECK_" in str(exc)


def parse_url_auth(url: str) -> tuple[str, int]:
    """Извлекает токен и DC ID из URL веб-авторизации.

    Args:
        url: URL с параметрами веб-авторизации.

    Returns:
        Кортеж (token, dc_id) из URL.

    Example:
        >>> url = "https://web.telegram.org/k/#tgWebAuthToken=ABC&tgWebAuthDcId=2"
        >>> token, dc_id = parse_url_auth(url)
        >>> print(f"Токен: {token}, DC: {dc_id}")
    """
    params = urllib.parse.parse_qs(urllib.parse.urlparse(url).fragment)

    token = params.get("tgWebAuthToken", [None])[0]
    dc_id = int(params.get("tgWebAuthDcId", [None])[0])

    return token, dc_id


def ensure_dir(dir_path: str) -> None:
    """Создаёт директорию, если она не существует.

    Args:
        dir_path: Путь к директории для создания.

    Example:
        >>> ensure_dir("./sessions/backup")
        >>> # Директория будет создана если её нет
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def is_private_chat_link(link: str) -> bool:
    """Проверяет, является ли ссылка на приватный чат.

    Args:
        link: Ссылка на чат.

    Returns:
        True если ссылка на приватный чат.
    """
    return "joinchat" in link or "+" in link


def is_chat_or_channel_entity(entity: tl_types.TypePeer) -> bool:
    """Проверяет, является ли объект чатом или каналом.

    Args:
        entity: Объект для проверки.

    Returns:
        True если объект является чатом или каналом.
    """
    return isinstance(entity, (tl_types.Chat, tl_types.Channel))


def get_private_link_hash(link: str) -> str:
    """Извлекает хэш из ссылки на приватный чат.

    Args:
        link: Ссылка на чат.

    Returns:
        Хэш из ссылки.
    """
    return link.split("+" if "+" in link else "/")[-1]


def match_tz_offset_by_number(phone_number: str) -> int:
    """Получает смещение часового пояса по номеру телефона. с помощью phonenumbers

    Args:
        phone_number: Номер телефона.

    Returns:
        Смещение часового пояса.
    """

    if not (phone_number := str(phone_number)):
        return None

    if not phone_number.startswith("+"):
        phone_number = "+" + phone_number.lstrip("+0")

    parsed = phonenumbers.parse(phone_number)
    if not phonenumbers.is_valid_number(parsed):
        raise ValueError(f"Invalid phone number: {phone_number}")

    if not (tz_name := phonenumbers_timezone.time_zones_for_number(parsed)):
        return None

    tz_offset = int(datetime.datetime.now(tz=tz_name[0]).utcoffset().total_seconds())

    if tz_offset < 0:
        tz_offset += 24 * 3600

    return tz_offset


def hex_to_base64(hex_string: str) -> str:
    """Преобразует hex строку в base64.

    Args:
        hex_string: Строка для преобразования.

    Returns:
        Строка в base64.
    """
    return base64.b64encode(bytes.fromhex(hex_string)).decode()
