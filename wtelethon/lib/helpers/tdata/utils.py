import hashlib
import io
import os
import struct
from typing import Optional

from telethon.crypto import AuthKey
from telethon.sessions import StringSession

try:
    import cryptg  # type: ignore
except ImportError:
    cryptg = None


class QDataStream:
    """Поток данных для чтения TData файлов."""

    def __init__(self, data: bytes):
        self.stream = io.BytesIO(data)

    def read(self, n: Optional[int] = None) -> Optional[bytes]:
        if n is not None:
            n = max(n, 0)
        data = self.stream.read(n)
        if n != 0 and len(data) == 0:
            return None
        if n is not None and len(data) != n:
            raise ValueError("Unexpected EOF")
        return data

    def read_buffer(self) -> Optional[bytes]:
        length_bytes = self.read(4)
        if length_bytes is None:
            return None
        length = int.from_bytes(length_bytes, "big", signed=True)
        data = self.read(length)
        if data is None:
            raise ValueError("Unexpected EOF")
        return data

    def read_uint32(self) -> Optional[int]:
        return self._read_int(4, signed=False)

    def read_uint64(self) -> Optional[int]:
        return self._read_int(8, signed=False)

    def read_int32(self) -> Optional[int]:
        return self._read_int(4, signed=True)

    def _read_int(self, size: int, signed: bool = False) -> Optional[int]:
        data = self.read(size)
        if data is None:
            return None
        return int.from_bytes(data, "big", signed=signed)


def create_local_key(passcode: bytes, salt: bytes) -> bytes:
    """Создает локальный ключ для расшифровки TData.

    Args:
        passcode: Пароль (может быть пустым).
        salt: Соль для генерации ключа.

    Returns:
        Локальный ключ для расшифровки.
    """
    iterations = 100_000 if passcode else 1
    _hash = hashlib.sha512(salt + passcode + salt).digest()
    return hashlib.pbkdf2_hmac("sha512", _hash, salt, iterations, 256)


def prepare_aes_oldmtp(auth_key: bytes, msg_key: bytes, send: bool) -> tuple[bytes, bytes]:
    """Подготавливает AES ключи для старого MTProto.

    Args:
        auth_key: Ключ авторизации.
        msg_key: Ключ сообщения.
        send: Направление (отправка или получение).

    Returns:
        Кортеж (ключ, IV) для AES.
    """
    x = 0 if send else 8

    sha1 = hashlib.sha1()
    sha1.update(msg_key)
    sha1.update(auth_key[x:][:32])
    a = sha1.digest()

    sha1 = hashlib.sha1()
    sha1.update(auth_key[32 + x :][:16])
    sha1.update(msg_key)
    sha1.update(auth_key[48 + x :][:16])
    b = sha1.digest()

    sha1 = hashlib.sha1()
    sha1.update(auth_key[64 + x :][:32])
    sha1.update(msg_key)
    c = sha1.digest()

    sha1 = hashlib.sha1()
    sha1.update(msg_key)
    sha1.update(auth_key[96 + x :][:32])
    d = sha1.digest()

    key = a[:8] + b[8:] + c[4:16]
    iv = a[8:] + b[:8] + c[16:] + d[:8]
    return key, iv


def aes_decrypt_local(ciphertext: bytes, auth_key: bytes, key_128: bytes) -> bytes:
    """Расшифровывает данные с помощью AES в режиме IGE.

    Args:
        ciphertext: Зашифрованные данные.
        auth_key: Ключ авторизации.
        key_128: 128-битный ключ.

    Returns:
        Расшифрованные данные.

    Raises:
        ImportError: Если cryptg не установлен.
    """
    if cryptg is None:
        raise ImportError("cryptg is required for TData decryption")

    key, iv = prepare_aes_oldmtp(auth_key, key_128, False)
    return cryptg.decrypt_ige(ciphertext, key, iv)


def decrypt_local(data: bytes, key: bytes) -> QDataStream:
    """Расшифровывает локальные данные TData.

    Args:
        data: Зашифрованные данные.
        key: Ключ для расшифровки.

    Returns:
        Поток расшифрованных данных.

    Raises:
        ValueError: Если расшифровка не удалась.
    """
    encrypted_key = data[:16]
    data = aes_decrypt_local(data[16:], key, encrypted_key)

    sha1 = hashlib.sha1()
    sha1.update(data)
    if encrypted_key != sha1.digest()[:16]:
        raise ValueError("Failed to decrypt")

    length = int.from_bytes(data[:4], "little")
    data = data[4:length]
    return QDataStream(data)


def read_file(name: str) -> QDataStream:
    """Читает TData файл с проверкой целостности.

    Args:
        name: Путь к файлу.

    Returns:
        Поток данных файла.

    Raises:
        ValueError: Если файл поврежден или имеет неверный формат.
    """
    with open(name, "rb") as f:
        magic = f.read(4)
        if magic != b"TDF$":
            raise ValueError("Invalid magic")
        version_bytes = f.read(4)
        data = f.read()

    data, digest = data[:-16], data[-16:]
    data_len_bytes = len(data).to_bytes(4, "little")

    md5 = hashlib.md5()
    md5.update(data)
    md5.update(data_len_bytes)
    md5.update(version_bytes)
    md5.update(magic)

    if md5.digest() != digest:
        raise ValueError("Invalid digest")

    return QDataStream(data)


def read_encrypted_file(name: str, key: bytes) -> QDataStream:
    """Читает и расшифровывает зашифрованный TData файл.

    Args:
        name: Путь к файлу.
        key: Ключ для расшифровки.

    Returns:
        Поток расшифрованных данных.
    """
    stream = read_file(name)
    encrypted_data = stream.read_buffer()
    return decrypt_local(encrypted_data, key)


def account_data_string(index: int = 0) -> str:
    """Генерирует строку данных аккаунта по индексу.

    Args:
        index: Индекс аккаунта (0 для основного).

    Returns:
        Хеш-строка для данных аккаунта.
    """
    s = "data"
    if index > 0:
        s += f"#{index+1}"

    md5 = hashlib.md5()
    md5.update(bytes(s, "utf-8"))
    digest = md5.digest()
    return digest[:8][::-1].hex().upper()[::-1]


def write_tdata_file(file_path: str, data: bytes) -> None:
    """Записывает TData файл с заголовком.

    Args:
        file_path: Путь к файлу.
        data: Данные для записи.
    """
    with open(file_path, "wb") as f:
        f.write(b"TDF$")  # magic
        f.write(struct.pack("<I", 0x01000000))  # version
        f.write(data)

        # MD5 checksum
        data_len_bytes = len(data).to_bytes(4, "little")
        md5 = hashlib.md5()
        md5.update(data)
        md5.update(data_len_bytes)
        md5.update(struct.pack("<I", 0x01000000))
        md5.update(b"TDF$")
        f.write(md5.digest())


def encrypt_tdata(data: bytes, key: bytes) -> bytes:
    """Шифрует данные для TData.

    Args:
        data: Данные для шифрования.
        key: Ключ шифрования.

    Returns:
        Зашифрованные данные.

    Raises:
        ImportError: Если cryptg не установлен.
    """
    if cryptg is None:
        raise ImportError("cryptg is required for TData creation")

    # Создаем случайный ключ для шифрования
    msg_key = os.urandom(16)

    # Подготавливаем данные
    data_with_length = struct.pack("<I", len(data)) + data

    # Добавляем случайные байты до размера, кратного 16
    padding_size = 16 - (len(data_with_length) % 16)
    if padding_size != 16:
        data_with_length += os.urandom(padding_size)

    # Вычисляем SHA1 для проверки
    sha1 = hashlib.sha1()
    sha1.update(data_with_length)

    # Подготавливаем к шифрованию
    final_data = data_with_length

    aes_key, iv = prepare_aes_oldmtp(key, msg_key, True)
    encrypted = cryptg.encrypt_ige(final_data, aes_key, iv)

    return msg_key + encrypted


def build_session_string(dc: int, ip: str, port: int, key: bytes) -> str:
    """Создаёт строку сессии из параметров подключения.

    Args:
        dc: ID дата-центра.
        ip: IP-адрес сервера.
        port: Порт сервера.
        key: Ключ авторизации.
    """
    session = StringSession()
    session.set_dc(dc, ip, port)
    session.auth_key = AuthKey(key)
    return session.save()
