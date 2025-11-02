import asyncio
from wtelethon import TelegramClient, MemoryAttachment, tl_errors, utils


async def example_dead_error_check():
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    try:
        await client.check_authorization(provoke_error=True)
        print("Account is alive")
    except Exception as exc:
        if utils.is_dead_error(exc):
            print("Session is dead - account banned or session invalidated")
            print(f"Error type: {type(exc).__name__}")
            print(f"Error: {exc}")

    await client.disconnect()


async def example_flood_wait_handling():
    from wtelethon import tl_functions

    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    try:
        await client(
            tl_functions.messages.GetDialogsRequest(
                offset_date=None, offset_id=0, offset_peer=tl_functions.InputPeerEmpty(), limit=100, hash=0
            )
        )
    except tl_errors.FloodWaitError as exc:
        print(f"Flood wait: need to wait {exc.seconds} seconds")
        await asyncio.sleep(exc.seconds)
        print("Can retry now")

    await client.disconnect()


async def example_session_password_needed():
    from wtelethon import tl_functions

    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    phone = "+1234567890"

    try:
        sent_code = await client.send_code_request(phone)
        code = input("Enter code: ")

        await client(
            tl_functions.auth.SignInRequest(phone_number=phone, phone_code_hash=sent_code.phone_code_hash, phone_code=code)
        )
    except tl_errors.SessionPasswordNeededError:
        print("2FA password required")
        password = input("Enter 2FA password: ")

        await client.sign_in(password=password)
        print("Signed in with 2FA")

    await client.disconnect()


async def example_phone_number_banned():
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    try:
        await client.send_code_request("+1234567890")
    except tl_errors.PhoneNumberBannedError:
        print("Phone number is banned")
    except tl_errors.PhoneNumberInvalidError:
        print("Phone number is invalid")

    await client.disconnect()


async def example_custom_error_handler():
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)

    def error_handler(exc: Exception):
        if isinstance(exc, tl_errors.FloodWaitError):
            print(f"Flood wait: {exc.seconds}s")
            return True

        if utils.is_dead_error(exc):
            print("Session is dead")
            client.memory.dead_status = True
            return True

        return False

    client.add_exception_handler(error_handler)

    await client.connect()

    try:
        await client.get_messages("channel", limit=100)
    except Exception as exc:
        print(f"Unhandled error: {exc}")

    await client.disconnect()


async def example_common_errors():
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    errors_to_check = [
        tl_errors.AuthKeyUnregisteredError,
        tl_errors.UserDeactivatedError,
        tl_errors.UserDeactivatedBanError,
        tl_errors.PhoneNumberBannedError,
        tl_errors.SessionRevokedError,
    ]

    try:
        await client.get_me()
    except tuple(errors_to_check) as exc:
        print(f"Dead error detected: {type(exc).__name__}")
        print(f"Is dead: {utils.is_dead_error(exc)}")
    except Exception as exc:
        print(f"Other error: {type(exc).__name__}")

    await client.disconnect()


if __name__ == "__main__":
    print("Choose exception handling example:")
    print("1. Check dead errors")
    print("2. Flood wait handling")
    print("3. Session password needed")
    print("4. Phone number banned")
    print("5. Custom error handler")
    print("6. Common errors")

    choice = input("Enter choice (1-6): ")

    examples = {
        "1": example_dead_error_check,
        "2": example_flood_wait_handling,
        "3": example_session_password_needed,
        "4": example_phone_number_banned,
        "5": example_custom_error_handler,
        "6": example_common_errors,
    }

    if choice in examples:
        asyncio.run(examples[choice]())
    else:
        print("Invalid choice")
