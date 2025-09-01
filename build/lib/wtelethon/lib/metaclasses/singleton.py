from typing import Optional, TypeVar, Generic, cast


T = TypeVar("T", bound="_SingletonMeta")


class _SingletonMeta(type, Generic[T]):
    _instance: Optional[T] = None

    def __call__(cls: T, *args, **kwargs) -> T:
        if cls._instance is None:
            cls._instance = cast(T, super().__call__(*args, **kwargs))

        return cls._instance
