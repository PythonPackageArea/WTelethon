import asyncio
from wtelethon import TelegramClient, MemoryAttachment


async def example_simple_client():
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    if await client.is_user_authorized():
        print("Client authorized")

    await client.disconnect()


async def example_memory_session():
    from telethon.sessions import MemorySession

    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient(MemorySession(), memory_attachment=memory)
    await client.connect()
    await client.disconnect()


async def example_string_session():
    session_string = "1BVtsOK4Bu...your_session_string..."
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient(session_string, memory_attachment=memory)
    await client.connect()
    await client.disconnect()


async def example_auth_key_hex():
    auth_key = "a1b2c3d4e5f6...512_char_hex_string..."
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient(auth_key, dc_id=2, memory_attachment=memory)
    await client.connect()
    await client.disconnect()


async def example_with_memory_attachment():
    memory = MemoryAttachment(
        api_id=12345,
        api_hash="your_hash",
        device_model="Custom Device",
        system_version="Android 12",
        app_version="9.0.1",
        lang_code="en",
        system_lang_code="en-US",
    )

    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    print(f"Device: {client.memory.device_model}")
    print(f"System: {client.memory.system_version}")

    await client.disconnect()


async def example_with_proxy():
    proxy = ("socks5", "127.0.0.1", 1080, True, "username", "password")
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")

    client = TelegramClient("session.session", memory_attachment=memory, proxy=proxy)
    await client.connect()
    await client.disconnect()


if __name__ == "__main__":
    print("Choose example:")
    print("1. Simple client")
    print("2. Memory session")
    print("3. String session")
    print("4. Auth key hex")
    print("5. With memory attachment")
    print("6. With proxy")

    choice = input("Enter choice (1-6): ")

    examples = {
        "1": example_simple_client,
        "2": example_memory_session,
        "3": example_string_session,
        "4": example_auth_key_hex,
        "5": example_with_memory_attachment,
        "6": example_with_proxy,
    }

    if choice in examples:
        asyncio.run(examples[choice]())
    else:
        print("Invalid choice")
