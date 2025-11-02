import asyncio
from wtelethon import TelegramClient, MemoryAttachment, proxy_storage, helpers


async def example_set_proxy_directly():
    proxy = ("socks5", "127.0.0.1", 1080)

    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory, proxy=proxy)
    await client.connect()
    print("Connected with proxy")
    await client.disconnect()


async def example_load_proxies_from_file():
    await helpers.storages.proxies.load_proxies_from_file("./data/proxies.txt", network_type="socks5")

    print(f"Loaded {len(proxy_storage._proxies)} proxies")

    for proxy in proxy_storage._proxies.values():
        print(f"  {proxy.host}:{proxy.port}")


async def example_use_proxy_from_storage():
    await helpers.storages.proxies.load_proxies_from_file("./data/proxies.txt", network_type="socks5")

    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)

    proxy = client.set_proxy_from_storage(usage_index_choice=True)
    print(f"Using proxy: {proxy.host}:{proxy.port}")

    await client.connect()
    await client.disconnect()


async def example_random_proxy():
    await helpers.storages.proxies.load_proxies_from_file("./data/proxies.txt", network_type="socks5")

    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)

    proxy = client.set_proxy_from_storage(random_choice=True)
    print(f"Random proxy: {proxy.host}:{proxy.port}")

    await client.connect()
    await client.disconnect()


async def example_proxy_error_handling():
    await helpers.storages.proxies.load_proxies_from_file("./data/proxies.txt", network_type="socks5")

    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)

    try:
        proxy = client.set_proxy_from_storage()
        await client.connect()
        print("Connected successfully")
    except Exception:
        client.proxy_error()
        print("Proxy failed, trying another")

        proxy = client.set_proxy_from_storage()
        await client.connect()
        print("Connected with new proxy")
    finally:
        await client.disconnect()


async def example_check_current_proxy():
    await helpers.storages.proxies.load_proxies_from_file("./data/proxies.txt", network_type="socks5")

    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)

    client.set_proxy_from_storage()

    if client.current_proxy:
        print(f"Current proxy: {client.current_proxy.host}:{client.current_proxy.port}")
        print(f"Last used: {client.current_proxy.last_used}")
        print(f"Error times: {client.current_proxy.last_errors}")


if __name__ == "__main__":
    print("Choose proxy operation:")
    print("1. Set proxy directly")
    print("2. Load proxies from file")
    print("3. Use proxy from storage")
    print("4. Random proxy selection")
    print("5. Proxy error handling")
    print("6. Check current proxy")

    choice = input("Enter choice (1-6): ")

    examples = {
        "1": example_set_proxy_directly,
        "2": example_load_proxies_from_file,
        "3": example_use_proxy_from_storage,
        "4": example_random_proxy,
        "5": example_proxy_error_handling,
        "6": example_check_current_proxy,
    }

    if choice in examples:
        asyncio.run(examples[choice]())
    else:
        print("Invalid choice")
