"""Модели данных и константы для Telegram API."""

import struct

from wtelethon import tl_errors


DEAD_EXCEPTIONS = (
    tl_errors.UnauthorizedError,
    tl_errors.UserDeactivatedBanError,
    tl_errors.SessionRevokedError,
    tl_errors.AuthKeyNotFound,
    tl_errors.AuthKeyDuplicatedError,
    tl_errors.ConnectionLayerInvalidError,
    tl_errors.BotMethodInvalidError,
    struct.error,
)


TGDC = {
    1: ["149.154.175.53"],
    2: ["149.154.167.51"],
    3: ["149.154.175.100"],
    4: ["149.154.167.91"],
    5: ["149.154.171.5"],
}


API_IDS_BY_PUSH_TOKEN_TYPE = {
    1: [8, 1],
    2: [4, 6],
}
API_IDS_BY_VOIP_TOKEN_TYPE = {
    9: [8, 1],
}
