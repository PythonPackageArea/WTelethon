from typing import Annotated, Literal, Iterator
from dataclasses import dataclass


@dataclass
class SessionItem:
    session: Annotated[Literal["path"], str]
    json: Annotated[Literal["path"], str]


class GlobResponse:
    _items: dict[Annotated[Literal["filename"], str], SessionItem]
    json_loners: dict[Annotated[Literal["filename"], str], Annotated[Literal["path"], str]]
    session_loners: dict[Annotated[Literal["filename"], str], Annotated[Literal["path"], str]]

    def __init__(
        self,
        items: dict[Annotated[Literal["filename"], str], SessionItem],
        json_loners: dict[Annotated[Literal["filename"], str], Annotated[Literal["path"], str]],
        session_loners: dict[Annotated[Literal["filename"], str], Annotated[Literal["path"], str]],
    ):
        self._items = items
        self.json_loners = json_loners
        self.session_loners = session_loners

    def __len__(self) -> int:
        return self._items.__len__()

    def __iter__(self) -> Iterator[SessionItem]:
        return self._items.values()

    def keys(self) -> Iterator[str]:
        return self._items.keys()

    def values(self) -> Iterator[SessionItem]:
        return self._items.values()

    def items(self) -> Iterator[tuple[str, SessionItem]]:
        return self._items.items()
