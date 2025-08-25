from telethon.network.connection import tcpfull
from telethon.network import mtprotosender
from telethon.client import telegrambaseclient

from .client import telegrambaseclient as telegrambaseclient_patch
from .network import mtprotosender as mtprotosender_patch
from .network.connection import tcpfull as tcpfull_patch

patched = False

if patched is False:
    tcpfull.FullPacketCodec.read_packet = tcpfull_patch.FullPacketCodec.read_packet
    mtprotosender.MTProtoSender._disconnect = mtprotosender_patch.MTProtoSender._disconnect
    telegrambaseclient.TelegramBaseClient.connect = telegrambaseclient_patch.TelegramBaseClient.connect
    patched = True
