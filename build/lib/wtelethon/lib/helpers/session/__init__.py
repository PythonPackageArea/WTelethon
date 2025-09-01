from telethon.crypto import AuthKey
from telethon.sessions import StringSession


def build_session_string(dc, ip, port, key) -> str:
    """Создаёт строку сессии из параметров подключения.

    Args:
        dc: ID дата-центра.
        ip: IP-адрес сервера.
        port: Порт сервера.
        key: Ключ авторизации.

    Returns:
        Строковое представление сессии.

    Example:
        >>> # Создать сессию из параметров
        >>> session_str = build_session_string(2, "149.154.167.51", 443, auth_key)
        >>> print(f"Сессия: {session_str}")
    """
    session = StringSession()
    session.set_dc(dc, ip, port)
    session.auth_key = AuthKey(key)
    return str
