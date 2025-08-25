from telethon_patch._version import __version__
from telethon_patch.patches.patch import patched

if patched is False:
    raise RuntimeError("Telethon patch is not applied")


from telethon import types as tl_types
from telethon import functions as tl_functions
from telethon import errors as tl_errors
from telethon import events as tl_events

from telethon_patch.lib import models
from telethon_patch.lib import utils
from telethon_patch.lib import helpers

from telethon_patch.attachments import (
    PlatformAttachment,
    MemoryAttachment,
    JsonAttachment,
)

from telethon_patch.client import TelegramClient

from telethon_patch.storages import (
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
