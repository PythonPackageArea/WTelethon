import asyncio
from wtelethon import TelegramClient, JsonAttachment, MemoryAttachment


async def example_json_attachment():
    json_attach = JsonAttachment("./data/account.json")
    await json_attach.load()

    print(f"API ID: {json_attach.api_id}")
    print(f"Phone: {json_attach.phone}")
    print(f"First name: {json_attach.first_name}")

    client = TelegramClient("session.session", json_attachment=json_attach)

    await client.connect()
    print(f"Client device: {client.memory.device_model}")
    await client.disconnect()


async def example_create_json_attachment():
    import os

    os.makedirs("./data", exist_ok=True)

    json_attach = JsonAttachment(
        "./data/new_account.json",
        include_data={
            "api_id": 12345,
            "api_hash": "your_hash",
            "phone": "+1234567890",
            "device_model": "iPhone 14 Pro",
            "system_version": "iOS 16.0",
        },
    )

    await json_attach.save()
    print("JSON attachment created")


async def example_memory_attachment():
    memory = MemoryAttachment(
        api_id=12345,
        api_hash="your_hash",
        phone="+1234567890",
        device_model="Samsung Galaxy S23",
        system_version="Android 13",
        app_version="9.5.0",
        lang_code="en",
        system_lang_code="en-US",
    )

    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    print(f"Phone: {client.memory.phone}")
    print(f"Device: {client.memory.device_model}")

    await client.disconnect()


async def example_update_json_from_memory():
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    await client.load_me_info()

    json_attach = JsonAttachment("./data/account.json")
    await json_attach.load()

    client.memory.fill_json(json_attach)
    await json_attach.save()

    print("JSON updated from memory")
    await client.disconnect()


async def example_json_helpers():
    json_attach = JsonAttachment("./data/account.json")
    await json_attach.load()

    first_value = json_attach.first("first_name", "username", "phone", default="Unknown")
    print(f"First non-empty: {first_value}")

    from datetime import datetime

    freeze_date = json_attach.to_dt(json_attach.freeze_until_date)
    if freeze_date:
        print(f"Freeze until: {freeze_date}")


async def example_combined_attachments():
    json_attach = JsonAttachment("./data/account.json")
    await json_attach.load()

    memory = MemoryAttachment(twofa="secret_password", spam_count=5, last_check_time=1234567890)

    client = TelegramClient("session.session", json_attachment=json_attach, memory_attachment=memory)

    await client.connect()
    print(f"API ID: {client.memory.api_id}")
    print(f"2FA: {client.memory.twofa}")
    await client.disconnect()


if __name__ == "__main__":
    print("Choose attachment operation:")
    print("1. Load JSON attachment")
    print("2. Create JSON attachment")
    print("3. Use memory attachment")
    print("4. Update JSON from memory")
    print("5. JSON helper methods")
    print("6. Combined attachments")

    choice = input("Enter choice (1-6): ")

    examples = {
        "1": example_json_attachment,
        "2": example_create_json_attachment,
        "3": example_memory_attachment,
        "4": example_update_json_from_memory,
        "5": example_json_helpers,
        "6": example_combined_attachments,
    }

    if choice in examples:
        asyncio.run(examples[choice]())
    else:
        print("Invalid choice")
