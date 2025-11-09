import asyncio
from wtelethon import TelegramClient, MemoryAttachment, helpers


async def example_periodic_tasks():
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    async def check_updates():
        print("Checking account status...")
        await client.load_me_info()
        print(f"User: {client.memory.first_name}")

    await helpers.tasks.run_fetch_task(check_updates, interval=30)

    await asyncio.sleep(120)
    await client.disconnect()


async def example_platform_data():
    from wtelethon.attachments.platform.model import PlatformData

    platform = PlatformData()
    platform.api_id = 12345
    platform.api_hash = "your_hash"
    platform.system_versions_by_device_models = {"iPhone 14 Pro Max": {"iOS 16.3.1"}}
    platform.app_versions_by_layer = {162: {"9.5.2"}}
    platform.lang_codes = {"en"}
    platform.system_lang_codes = {"en-US"}

    client = TelegramClient("session.session", platform_data=platform)

    await client.connect()
    print(f"Device: {client.memory.device_model}")
    await client.disconnect()


async def example_update_platform():
    from wtelethon.attachments.platform.model import PlatformData

    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    new_platform = PlatformData()
    new_platform.api_id = 12345
    new_platform.api_hash = "your_hash"
    new_platform.system_versions_by_device_models = {"Samsung Galaxy S23 Ultra": {"Android 13"}}
    new_platform.app_versions_by_layer = {162: {"9.5.0"}}

    await client.update_client_platform(new_platform, reinit=True)
    print("Platform updated")

    await client.disconnect()


async def example_notification_registration():
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    from wtelethon import tl_functions

    await client(
        tl_functions.account.RegisterDeviceRequest(token_type=7, token="push_token_here", app_sandbox=False, other_uids=[])
    )

    print("Device registered for notifications")
    await client.disconnect()


async def example_glob_files():
    from wtelethon.lib.helpers.files import glob_files

    result = glob_files("./data/sessions")

    print(f"Total files: {len(result)}")

    for session_file, json_file in result.pairs():
        if session_file and json_file:
            print(f"Pair: {session_file} <-> {json_file}")


async def example_multiple_clients():
    clients = []

    for i in range(3):
        memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
        client = TelegramClient(f"session_{i}.session", memory_attachment=memory)
        await client.connect()
        clients.append(client)

    results = await asyncio.gather(*[client.get_me() for client in clients], return_exceptions=True)

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Client {i}: Error - {result}")
        else:
            print(f"Client {i}: {result.first_name}")

    for client in clients:
        await client.disconnect()


async def example_logging_setup():
    from wtelethon.lib.helpers.logging import set_telethon_log_level, set_telethon_logging

    set_telethon_log_level("INFO")

    handler = set_telethon_logging(mode="simple")

    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    await client.get_me()

    await client.disconnect()


if __name__ == "__main__":
    print("Choose advanced feature:")
    print("1. Periodic tasks")
    print("2. Platform data")
    print("3. Update platform")
    print("4. Notification registration")
    print("5. Glob files")
    print("6. Multiple clients")
    print("7. Logging setup")

    choice = input("Enter choice (1-7): ")

    examples = {
        "1": example_periodic_tasks,
        "2": example_platform_data,
        "3": example_update_platform,
        "4": example_notification_registration,
        "5": example_glob_files,
        "6": example_multiple_clients,
        "7": example_logging_setup,
    }

    if choice in examples:
        asyncio.run(examples[choice]())
    else:
        print("Invalid choice")
