import asyncio
from wtelethon import TelegramClient, MemoryAttachment, helpers
from wtelethon.tools.session.convert_tools import ConvertTools


async def example_create_tdata_single():
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    client.create_tdata("./output/tdata", passcode="")
    print("TData created from session")

    is_valid = helpers.tdata.validate_tdata_creation("./output/tdata")
    print(f"TData is valid: {is_valid}")

    await client.disconnect()


async def example_create_tdata_multiple():
    memory1 = MemoryAttachment(api_id=12345, api_hash="your_hash")
    memory2 = MemoryAttachment(api_id=12345, api_hash="your_hash")
    memory3 = MemoryAttachment(api_id=12345, api_hash="your_hash")

    clients = [
        TelegramClient("session1.session", memory_attachment=memory1),
        TelegramClient("session2.session", memory_attachment=memory2),
        TelegramClient("session3.session", memory_attachment=memory3),
    ]

    for client in clients:
        await client.connect()

    ConvertTools.create_tdata_from_clients(clients=clients, tdata_output_path="./output/multi_tdata", passcode="", active_index=0)

    print(f"Multi-account TData created with {len(clients)} accounts")

    for client in clients:
        await client.disconnect()


async def example_extract_tdata_info():
    info = helpers.tdata.extract_tdata_info("./tdata")

    print(f"Total accounts: {info.accounts_count}")
    print(f"Extracted sessions: {len(info.sessions)}")

    for acc in info.accounts:
        print(f"Account {acc.index}: DC {acc.dc}")
        if acc.error:
            print(f"  Error: {acc.error}")


def example_convert_tdata_to_sessions():
    info = helpers.tdata.extract_tdata_info("./tdata")

    from telethon.sessions import StringSession, SQLiteSession

    for i, session_string in enumerate(info.sessions):
        temp_session = StringSession(session_string)

        sqlite_session = SQLiteSession(f"./output/account_{i}.session")
        sqlite_session.set_dc(temp_session.dc_id, temp_session.server_address, temp_session.port)
        sqlite_session.auth_key = temp_session.auth_key
        sqlite_session.save()

        print(f"Created account_{i}.session")


if __name__ == "__main__":
    print("Choose TData operation:")
    print("1. Create TData from single session")
    print("2. Create TData from multiple sessions")
    print("3. Extract TData info")
    print("4. Convert TData to sessions")

    choice = input("Enter choice (1-4): ")

    examples = {
        "1": example_create_tdata_single,
        "2": example_create_tdata_multiple,
        "3": example_extract_tdata_info,
        "4": example_convert_tdata_to_sessions,
    }

    if choice in examples:
        if choice in ["3", "4"]:
            examples[choice]()
        else:
            asyncio.run(examples[choice]())
    else:
        print("Invalid choice")
