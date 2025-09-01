import asyncio

from config import alive_dir_path, proxies_file_path, proxy_type
from loader import load_clients
from proccess import run_software
from handlers import connect_error_handler, dead_error_handler

from wtelethon import storages, helpers, utils

helpers.logging.set_telethon_logging("simple")


async def main():
    # ... software starting ...
    try:
        await helpers.storages.proxies.load_proxies_from_file(
            proxies_file_path,
            proxy_type,
        )

    except Exception as e:
        print(f"Ошибка при загрузке прокси: {e}")

    print(f"Загружено {storages.proxy_storage._proxies.__len__()} прокси")

    clients = await load_clients(alive_dir_path)
    print(f"Загружено {clients.__len__()} клиентов")

    for client in clients:
        client.add_exception_handler(utils.is_connection_error, connect_error_handler)
        client.add_exception_handler(utils.is_dead_error, dead_error_handler)
        storages.client_holds_storage.add_client(client)

    await run_software()

    # ... software ending ...


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
