from api_mock import ApiMock
from wtelethon import storages, helpers
from wtelethon.storages.proxies import Proxy


api_mock = ApiMock()


async def load_proxies():
    proxies = api_mock.get_proxies()

    for proxy in proxies:
        storages.proxy_storage.add_proxy(
            Proxy(
                proxy.slug,
                proxy.host,
                proxy.port,
                proxy.type,
                proxy.username,
                proxy.password,
            ),
            proxy.type,
        )

    for proxy_source in storages.proxy_storage._proxies.keys():
        if proxy_source not in [p.slug for p in proxies]:
            storages.proxy_storage.remove_proxy(proxy_source)
