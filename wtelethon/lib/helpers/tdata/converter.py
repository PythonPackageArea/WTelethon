import os
import struct
from typing import List, Tuple
from glob import glob

from wtelethon.lib.models import TGDC
from .utils import (
    QDataStream,
    create_local_key,
    decrypt_local,
    read_file,
    read_encrypted_file,
    account_data_string,
    write_tdata_file,
    encrypt_tdata,
    build_session_string
)
from .models import TDataAccount, TDataInfo


def read_user_auth(directory: str, local_key: bytes, index: int = 0) -> Tuple[int, bytes]:
    """Читает данные авторизации пользователя из TData.

    Args:
        directory: Путь к директории TData.
        local_key: Локальный ключ для расшифровки.
        index: Индекс аккаунта.

    Returns:
        Кортеж (DC ID, auth_key).
    """
    name = account_data_string(index)
    path = os.path.join(directory, f"{name}s")
    stream = read_encrypted_file(path, local_key)

    if stream.read_uint32() != 0x4B:
        raise ValueError("Unsupported user auth config")

    stream = QDataStream(stream.read_buffer())
    user_id = stream.read_uint32()
    main_dc = stream.read_uint32()

    if user_id == 0xFFFFFFFF and main_dc == 0xFFFFFFFF:
        user_id = stream.read_uint64()
        main_dc = stream.read_uint32()

    if main_dc not in TGDC:
        raise ValueError(f"Unsupported main DC: {main_dc}")

    length = stream.read_uint32()
    for _ in range(length):
        auth_dc = stream.read_uint32()
        auth_key = stream.read(256)
        if auth_dc == main_dc:
            return auth_dc, auth_key

    raise ValueError("Invalid user auth config")


def extract_tdata_info(path: str) -> TDataInfo:
    """Извлекает информацию и сессии из TData.

    Args:
        path: Путь к директории TData.

    Returns:
        Информация о TData со строками сессий.

    Example:
        >>> info = extract_tdata_info("./tdata")
        >>> print(f"Аккаунтов: {info.accounts_count}")
    """
    try:
        stream = read_file(os.path.join(path, "key_datas"))
    except FileNotFoundError:
        stream = read_file(os.path.join(path, "key_data"))

    salt = stream.read_buffer()
    if len(salt) != 32:
        raise ValueError("Invalid salt length")

    key_encrypted = stream.read_buffer()
    info_encrypted = stream.read_buffer()

    passcode_key = create_local_key(b"", salt)
    key_inner_data = decrypt_local(key_encrypted, passcode_key)
    local_key = key_inner_data.read(256)

    if len(local_key) != 256:
        raise ValueError("Invalid local key")

    info_data = decrypt_local(info_encrypted, local_key)
    count = info_data.read_uint32()

    accounts = []
    sessions = []

    for _ in range(count):
        index = info_data.read_uint32()
        try:
            dc, key = read_user_auth(path, local_key, index)
            accounts.append(TDataAccount(index=index, dc=dc))

            ip = TGDC[dc][0]
            sessions.append(build_session_string(dc, ip, 443, key))
        except (ValueError, FileNotFoundError):
            accounts.append(TDataAccount(index=index, dc=None, error=True))
            # Не добавляем сессию для поврежденных аккаунтов

    return TDataInfo(
        accounts_count=count,
        accounts=accounts,
        has_passcode=len(salt) > 0,
        sessions=sessions,
    )


def validate_tdata_creation(tdata_path: str) -> bool:
    """Проверяет успешность создания TData.

    Args:
        tdata_path: Путь к созданному TData.

    Returns:
        True если TData создан корректно.
    """
    if not os.path.exists(tdata_path) or not os.path.isdir(tdata_path):
        return False

    key_file = os.path.join(tdata_path, "key_datas")
    if not os.path.exists(key_file):
        return False

    account_files = glob(os.path.join(tdata_path, "*s"))
    account_files = [f for f in account_files if os.path.basename(f) != "key_datas"]

    return len(account_files) > 0


def _create_account_file(
    output_path: str,
    account_index: int,
    dc_id: int,
    auth_key: bytes,
    local_key: bytes,
) -> None:
    """Создает файл данных аккаунта.

    Args:
        output_path: Путь для сохранения TData.
        account_index: Индекс аккаунта.
        dc_id: ID дата-центра.
        auth_key: Ключ авторизации.
        local_key: Локальный ключ для шифрования.
    """
    account_name = account_data_string(account_index)
    auth_data = struct.pack(">I", 0x4B)

    user_data = struct.pack(">I", 0xFFFFFFFF)
    user_data += struct.pack(">I", dc_id)
    user_data += struct.pack(">I", 1)
    user_data += struct.pack(">I", dc_id)
    user_data += auth_key

    auth_data += struct.pack(">I", len(user_data)) + user_data
    encrypted_auth = encrypt_tdata(auth_data, local_key)

    account_file_path = os.path.join(output_path, f"{account_name}s")
    write_tdata_file(account_file_path, encrypted_auth)


def _create_tdata_files(
    output_path: str,
    accounts: List[Tuple[int, bytes]],
    passcode: str = "",
    active_index: int = 0,
) -> bool:
    """Создает файлы TData структуры для одного или нескольких аккаунтов.

    Args:
        output_path: Путь для сохранения TData.
        accounts: Список кортежей (dc_id, auth_key) для каждого аккаунта.
        passcode: Пароль для TData.
        active_index: Индекс активного аккаунта.

    Returns:
        True если создание прошло успешно.
    """
    if not accounts:
        raise ValueError("At least one account is required")

    for dc_id, _ in accounts:
        if dc_id not in TGDC:
            raise ValueError(f"Unsupported DC: {dc_id}")

    passcode_bytes = passcode.encode("utf-8")
    salt = os.urandom(32)
    passcode_key = create_local_key(passcode_bytes, salt)
    local_key = os.urandom(256)

    key_encrypted = encrypt_tdata(local_key, passcode_key)

    account_count = len(accounts)
    accounts_data = struct.pack(">I", account_count)

    for index in range(account_count):
        accounts_data += struct.pack(">I", index)

    accounts_data += struct.pack(">I", active_index)

    info_encrypted = encrypt_tdata(accounts_data, local_key)

    key_file_data = struct.pack(">I", len(salt)) + salt
    key_file_data += struct.pack(">I", len(key_encrypted)) + key_encrypted
    key_file_data += struct.pack(">I", len(info_encrypted)) + info_encrypted

    key_file_path = os.path.join(output_path, "key_datas")
    write_tdata_file(key_file_path, key_file_data)

    for index, (dc_id, auth_key) in enumerate(accounts):
        _create_account_file(output_path, index, dc_id, auth_key, local_key)

    return True
