import asyncio
from wtelethon import TelegramClient, MemoryAttachment


async def example_get_session_string():
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    session_string = client.get_session_string()
    print(f"Session string: {session_string[:50]}...")

    await client.disconnect()


async def example_get_auth_key_hex():
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    auth_key = client.get_auth_key_hex()
    print(f"Auth key hex: {auth_key[:50]}...")

    await client.disconnect()


async def example_create_sqlite_from_memory():
    from telethon.sessions import MemorySession

    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient(MemorySession(), memory_attachment=memory)
    await client.connect()

    await client.create_sqlite_session("./sessions", "converted_session")
    print("SQLite session created")

    await client.disconnect()


async def example_load_sqlite_to_memory():
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    memory.source_dir = "./sessions"
    memory.session_file = "account.session"

    client = TelegramClient("./sessions/account.session", memory_attachment=memory)

    await client.load_sqlite_session()
    print("SQLite loaded as StringSession")

    await client.connect()
    await client.disconnect()


async def example_convert_auth_key_to_sqlite():
    auth_key_hex = "a1b2c3d4e5f6...512_char_hex..."
    dc_id = 2

    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient(auth_key_hex, dc_id=dc_id, memory_attachment=memory)
    await client.connect()

    await client.create_sqlite_session("./sessions", "from_auth_key")
    print("Created SQLite from auth key")

    await client.disconnect()


if __name__ == "__main__":
    print("Choose conversion operation:")
    print("1. Get session string")
    print("2. Get auth key hex")
    print("3. Create SQLite from memory")
    print("4. Load SQLite to memory")
    print("5. Convert auth key to SQLite")

    choice = input("Enter choice (1-5): ")

    examples = {
        "1": example_get_session_string,
        "2": example_get_auth_key_hex,
        "3": example_create_sqlite_from_memory,
        "4": example_load_sqlite_to_memory,
        "5": example_convert_auth_key_to_sqlite,
    }

    if choice in examples:
        asyncio.run(examples[choice]())
    else:
        print("Invalid choice")
