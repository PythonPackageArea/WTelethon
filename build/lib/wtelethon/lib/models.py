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

COUNTRY_LANG_CODES = {
    "RU": ["ru"],
    "BY": ["be", "ru"],
    "KZ": ["ru"],
    "KG": ["ru"],
    "MD": ["ru"],
    "UZ": ["uz", "ru"],
    "UA": ["uk", "ru"],
    "US": ["en"],
    "GB": ["en"],
    "CA": ["en", "fr"],
    "AU": ["en"],
    "NZ": ["en"],
    "DE": ["de"],
    "AT": ["de"],
    "CH": ["de", "fr", "it"],
    "ES": ["es", "ca"],
    "MX": ["es"],
    "AR": ["es"],
    "CO": ["es"],
    "CL": ["es"],
    "PE": ["es"],
    "IT": ["it"],
    "AM": ["am"],
    "FR": ["fr"],
    "BE": ["fr", "nl"],
    "NL": ["nl"],
    "PL": ["pl"],
    "PT": ["pt"],
    "BR": ["pt"],
    "TR": ["tr"],
    "ID": ["id"],
    "MY": ["ms"],
    "KR": ["ko"],
    "SA": ["ar"],
    "IR": ["fa"],
}

FALLBACK_LANG_CODES = {
        "es": ["ca"],
        "ru": ["uk", "be"],
        "en": ["de", "fr"],
        "ar": ["fa"],
        "pt": ["es"],
        "fr": ["en"],
        "de": ["en"],
        "it": ["es"],
        "tr": ["de"],
        "pl": ["ru"],
    }
