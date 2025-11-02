import asyncio
from wtelethon import TelegramClient, MemoryAttachment, tl_types
from wtelethon.tools.client.auth import QRAuthTools, WebAuthTools, SMSAuthTools


async def example_qr_auth():
    new_memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    old_memory = MemoryAttachment(api_id=12345, api_hash="your_hash")

    new_client = TelegramClient("new.session", memory_attachment=new_memory)
    old_client = TelegramClient("old.session", memory_attachment=old_memory)

    await new_client.connect()
    await old_client.connect()

    try:
        await QRAuthTools.ensure_qr_login(new_client, old_client)
        print("QR auth completed")
    finally:
        await new_client.disconnect()
        await old_client.disconnect()


async def example_web_auth():
    new_memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    old_memory = MemoryAttachment(api_id=12345, api_hash="your_hash")

    new_client = TelegramClient("new.session", memory_attachment=new_memory)
    old_client = TelegramClient("old.session", memory_attachment=old_memory)

    await new_client.connect()
    await old_client.connect()

    try:
        await WebAuthTools.ensure_web_login(new_client, old_client)
        print("Web auth completed")
    finally:
        await new_client.disconnect()
        await old_client.disconnect()


async def example_sms_auth():
    new_memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    old_memory = MemoryAttachment(api_id=12345, api_hash="your_hash", phone="+1234567890")

    new_client = TelegramClient("new.session", memory_attachment=new_memory)
    old_client = TelegramClient("old.session", memory_attachment=old_memory)

    await new_client.connect()
    await old_client.connect()

    try:
        auth = await SMSAuthTools.ensure_app_code_login(new_client, old_client, timeout=30)
        if auth:
            print("SMS auth completed")
    finally:
        await new_client.disconnect()
        await old_client.disconnect()


async def example_manual_sms_auth():
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    phone = "+1234567890"
    sent_code = await client.send_code_request(phone, auto_success_response_login=True)

    if isinstance(sent_code, tl_types.auth.SentCode):
        code = input("Enter code from SMS: ")

        auth = await client.sign_in(phone, sent_code.phone_code_hash, code)

        print("Authorized successfully")
        await client.disconnect()

    elif isinstance(sent_code, tl_types.auth.SentCodeSuccess):
        print("Authorized successfully")
        await client.disconnect()

    elif isinstance(sent_code, tl_types.auth.SentCodePaymentRequired):
        print("Payment required")
        await client.disconnect()

    else:
        print("Failed to send code")
        await client.disconnect()


if __name__ == "__main__":
    print("Choose authentication method:")
    print("1. QR auth")
    print("2. Web auth")
    print("3. SMS auth (automatic)")
    print("4. SMS auth (manual)")

    choice = input("Enter choice (1-4): ")

    examples = {
        "1": example_qr_auth,
        "2": example_web_auth,
        "3": example_sms_auth,
        "4": example_manual_sms_auth,
    }

    if choice in examples:
        asyncio.run(examples[choice]())
    else:
        print("Invalid choice")
