import asyncio
from wtelethon import TelegramClient, JsonAttachment, utils, helpers, MemoryAttachment


async def complete_account_check():
    json_attach = JsonAttachment("./data/account.json")
    await json_attach.load()

    client = TelegramClient(f"./data/sessions/{json_attach.phone}.session", json_attachment=json_attach)

    try:
        await helpers.storages.proxies.load_proxies_from_file("./data/proxies.txt", "socks5")
        client.set_proxy_from_storage()
    except Exception:
        print("No proxies available")

    await client.connect()

    try:
        await client.check_authorization(provoke_error=True)
        print(f"✓ Account {json_attach.phone} is authorized")

        await client.load_me_info()
        print(f"✓ User: {client.memory.first_name} {client.memory.last_name}")
        print(f"✓ Username: @{client.memory.username}")

        await client.load_spamblock_info(delete_dialog=True)
        from wtelethon.attachments.memory.types import Types

        if client.memory.spamblock_type == Types.spamblock_type.FREE:
            print("✓ Account is not blocked")
        else:
            print(f"✗ Spamblock: {client.memory.spamblock_type}")

        if client.memory.twofa:
            await client.check_twofa(client.memory.twofa)
            if not client.memory.twofa_unknown:
                print("✓ 2FA is valid")

        client.memory.fill_json(json_attach)
        await json_attach.save()
        print("✓ Account info saved to JSON")

    except Exception as exc:
        if utils.is_dead_error(exc):
            print(f"✗ Session is dead: {exc}")
            client.memory.dead_status = True
        else:
            print(f"✗ Error: {exc}")

    finally:
        await client.disconnect()


async def batch_session_conversion():
    import os

    session_dir = "./data/sessions/alive"
    output_dir = "./data/sessions/converted"

    os.makedirs(output_dir, exist_ok=True)

    session_files = [f for f in os.listdir(session_dir) if f.endswith(".session")]

    for session_file in session_files:
        session_path = os.path.join(session_dir, session_file)

        memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
        client = TelegramClient(session_path, memory_attachment=memory)
        await client.connect()

        if await client.is_user_authorized():
            session_string = client.get_session_string()
            auth_key_hex = client.get_auth_key_hex()

            output_file = os.path.join(output_dir, f"{session_file}.txt")
            with open(output_file, "w") as f:
                f.write(f"Session String:\n{session_string}\n\n")
                f.write(f"Auth Key Hex:\n{auth_key_hex}\n")

            print(f"✓ Converted {session_file}")
        else:
            print(f"✗ {session_file} not authorized")

        await client.disconnect()


async def multi_account_tdata_creator():
    import os
    from wtelethon.tools.session.convert_tools import ConvertTools

    session_dir = "./data/sessions/alive"
    output_tdata = "./data/tdata_export"

    session_files = [f for f in os.listdir(session_dir) if f.endswith(".session")]

    clients = []
    for session_file in session_files:
        session_path = os.path.join(session_dir, session_file)
        memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
        client = TelegramClient(session_path, memory_attachment=memory)
        await client.connect()

        if await client.is_user_authorized():
            clients.append(client)
            print(f"✓ Added {session_file}")
        else:
            await client.disconnect()
            print(f"✗ Skipped {session_file}")

    if clients:
        ConvertTools.create_tdata_from_clients(clients=clients, tdata_output_path=output_tdata, passcode="", active_index=0)
        print(f"✓ Created TData with {len(clients)} accounts")

        info = helpers.tdata.extract_tdata_info(output_tdata)
        print(f"✓ Validated: {info.accounts_count} accounts")

        for client in clients:
            await client.disconnect()


async def account_health_monitor():
    import os
    import datetime

    session_dir = "./data/sessions"

    alive_dir = os.path.join(session_dir, "alive")
    dead_dir = os.path.join(session_dir, "dead")

    os.makedirs(alive_dir, exist_ok=True)
    os.makedirs(dead_dir, exist_ok=True)

    session_files = [f for f in os.listdir(session_dir) if f.endswith(".session")]

    report = {"alive": 0, "dead": 0, "blocked": 0, "twofa_issues": 0}

    for session_file in session_files:
        session_path = os.path.join(session_dir, session_file)
        json_path = session_path.replace(".session", ".json")

        json_attach = None
        if os.path.exists(json_path):
            json_attach = JsonAttachment(json_path)
            await json_attach.load()

        client = TelegramClient(session_path, json_attachment=json_attach)

        await client.connect()

        try:
            await client.check_authorization(provoke_error=True)
            await client.load_me_info()

            await client.load_spamblock_info(delete_dialog=True)
            from wtelethon.attachments.memory.types import Types

            if client.memory.spamblock_type != Types.spamblock_type.FREE:
                report["blocked"] += 1
                print(f"⚠ {session_file} is blocked")
            else:
                report["alive"] += 1
                print(f"✓ {session_file} is alive")

            if json_attach:
                client.memory.fill_json(json_attach)
                await json_attach.save()

        except Exception as exc:
            if utils.is_dead_error(exc):
                report["dead"] += 1
                print(f"✗ {session_file} is dead")

                os.rename(session_path, os.path.join(dead_dir, session_file))
                if os.path.exists(json_path):
                    os.rename(json_path, os.path.join(dead_dir, session_file.replace(".session", ".json")))

        finally:
            await client.disconnect()

    print("\n=== Health Report ===")
    print(f"Alive: {report['alive']}")
    print(f"Dead: {report['dead']}")
    print(f"Blocked: {report['blocked']}")
    print(f"Total checked: {len(session_files)}")


if __name__ == "__main__":
    print("Choose workflow:")
    print("1. Complete account check")
    print("2. Batch session conversion")
    print("3. Multi-account TData creator")
    print("4. Account health monitor")

    choice = input("Enter choice (1-4): ")

    examples = {
        "1": complete_account_check,
        "2": batch_session_conversion,
        "3": multi_account_tdata_creator,
        "4": account_health_monitor,
    }

    if choice in examples:
        asyncio.run(examples[choice]())
    else:
        print("Invalid choice")
