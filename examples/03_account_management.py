import asyncio
from wtelethon import TelegramClient, MemoryAttachment, utils


async def example_check_authorization():
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    try:
        await client.check_authorization(provoke_error=True)
        print("Account is authorized")
    except Exception as exc:
        if utils.is_dead_error(exc):
            print("Session is dead")
        else:
            print(f"Authorization error: {exc}")

    await client.disconnect()


async def example_load_user_info():
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    await client.load_me_info()

    print(f"ID: {client.memory.account_id}")
    print(f"Name: {client.memory.first_name} {client.memory.last_name}")
    print(f"Username: @{client.memory.username}")
    print(f"Phone: {client.memory.phone}")
    print(f"Has photo: {client.memory.has_profile_pic}")

    await client.disconnect()


async def example_check_spambot():
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    await client.load_spamblock_info(delete_dialog=True)

    from wtelethon.attachments.memory.types import Types

    if client.memory.spamblock_type == Types.spamblock_type.FREE:
        print("Account is not blocked")
    elif client.memory.spamblock_type == Types.spamblock_type.TEMPORARY:
        print(f"Temporary block until: {client.memory.spamblock_until_date}")
    elif client.memory.spamblock_type == Types.spamblock_type.PERMANENT:
        print("Permanent block")

    await client.disconnect()


async def example_twofa_check():
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    await client.check_twofa("your_2fa_password")

    if client.memory.twofa_unknown:
        print("2FA password is unknown")
    else:
        print("2FA is valid")

    await client.disconnect()


async def example_twofa_change():
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    await client.edit_2fa(
        current_password="old_password", new_password="new_password", email="recovery@email.com", hint="my hint"
    )

    print("2FA password updated")
    await client.disconnect()


if __name__ == "__main__":
    print("Choose operation:")
    print("1. Check authorization")
    print("2. Load user info")
    print("3. Check spambot status")
    print("4. Check 2FA")
    print("5. Change 2FA")

    choice = input("Enter choice (1-5): ")

    examples = {
        "1": example_check_authorization,
        "2": example_load_user_info,
        "3": example_check_spambot,
        "4": example_twofa_check,
        "5": example_twofa_change,
    }

    if choice in examples:
        asyncio.run(examples[choice]())
    else:
        print("Invalid choice")
