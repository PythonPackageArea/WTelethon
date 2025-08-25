from .client_holds import ClientHoldsStorage
from .proxies import ProxyStorage, Proxy


client_holds_storage = ClientHoldsStorage()
proxy_storage = ProxyStorage()


__ALL__ = [client_holds_storage, proxy_storage, Proxy]
