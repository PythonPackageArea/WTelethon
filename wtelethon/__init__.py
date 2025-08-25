from wtelethon._version import __version__
from wtelethon.patches.patch import patched

if patched is False:
    raise RuntimeError("Telethon patch is not applied")


from telethon import types as tl_types
from telethon import functions as tl_functions
from telethon import errors as tl_errors
from telethon import events as tl_events

from wtelethon.lib import models
from wtelethon.lib import utils
from wtelethon.lib import helpers

from wtelethon.attachments import (
    PlatformAttachment,
    MemoryAttachment,
    JsonAttachment,
)

from wtelethon.client import TelegramClient

from wtelethon.storages import (
    client_holds_storage,
    proxy_storage,
)

__ALL__ = [
    TelegramClient,
    tl_types,
    tl_functions,
    tl_errors,
    tl_events,
    utils,
    helpers,
    client_holds_storage,
    proxy_storage,
    PlatformAttachment,
    MemoryAttachment,
    JsonAttachment,
    __version__,
]
