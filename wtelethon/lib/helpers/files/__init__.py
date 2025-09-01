from glob import glob
import os
from typing import Optional, Annotated, Literal, Iterator
from dataclasses import dataclass


@dataclass
class SessionItem:
    session: Annotated[Literal["path"], str]
    json: Annotated[Literal["path"], str]


class GlobResponse:
    _items: dict[
        Annotated[Literal["filename"], str],
        SessionItem,
    ]
    json_loners: dict[
        Annotated[Literal["filename"], str],
        Annotated[Literal["path"], str],
    ]
    session_loners: dict[
        Annotated[Literal["filename"], str],
        Annotated[Literal["path"], str],
    ]

    def __init__(
        self,
        items: dict[
            Annotated[Literal["filename"], str],
            SessionItem,
        ],
        json_loners: dict[
            Annotated[Literal["filename"], str],
            Annotated[Literal["path"], str],
        ],
        session_loners: dict[
            Annotated[Literal["filename"], str],
            Annotated[Literal["path"], str],
        ],
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


def glob_files(path: str) -> GlobResponse:
    """Находит .session и .json файлы в указанной директории.

    Args:
        path: Путь к директории для поиска.
        must_have_json: Если True, включает только сессии с соответствующим JSON.

    Returns:
        Словарь вида {имя_файла: SessionItem}.

    Example:
        >>> files = glob_files("./sessions")
        >>> for name, paths in files.items():
        >>>     print(f"Аккаунт: {name}")
        >>>     print(f"Сессия: {paths.session_file}")
        >>>     if paths.json_file:
        >>>         print(f"JSON: {paths.json_file}")
    """
    session_files = glob(f"{path}/*.session") + glob(
        f"{path}/**/*.session", recursive=True
    )
    sessions = {
        os.path.basename(path).split(".")[0].lower(): path for path in session_files
    }

    json_files = glob(f"{path}/*.json") + glob(f"{path}/**/*.json", recursive=True)
    jsons = {os.path.basename(path).split(".")[0].lower(): path for path in json_files}

    return GlobResponse(
        items={
            filename: SessionItem(session=sessions[filename], json=jsons[filename])
            for filename in sessions
            if filename in jsons
        },
        json_loners={
            filename: jsons[filename] for filename in jsons if filename not in sessions
        },
        session_loners={
            filename: sessions[filename]
            for filename in sessions
            if filename not in jsons
        },
    )
