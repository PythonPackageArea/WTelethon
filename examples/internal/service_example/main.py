import asyncio

from api_mock import ApiMock

# from config import alive_dir_path, proxies_file_path, proxy_type
# from loader import load_clients
# from proccess import run_software
# from handlers import connect_error_handler, dead_error_handler

from wtelethon import storages, helpers, utils
from proxy_loader import load_proxies
from proccess import run_service


helpers.logging.set_telethon_logging("off")
api_mock = ApiMock()


async def main():

    # ... service starting ...

    await helpers.tasks.run_fetch_task(load_proxies)
    await run_service()

    # ... service ending ...


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
