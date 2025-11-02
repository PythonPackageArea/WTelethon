from glob import glob
import os

from .models import GlobResponse, SessionItem


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
    session_files = glob(f"{path}/*.session") + glob(f"{path}/**/*.session", recursive=True)
    sessions = {os.path.basename(path).split(".")[0].lower(): path for path in session_files}

    json_files = glob(f"{path}/*.json") + glob(f"{path}/**/*.json", recursive=True)
    jsons = {os.path.basename(path).split(".")[0].lower(): path for path in json_files}

    return GlobResponse(
        items={
            filename: SessionItem(session=sessions[filename], json=jsons[filename]) for filename in sessions if filename in jsons
        },
        json_loners={filename: jsons[filename] for filename in jsons if filename not in sessions},
        session_loners={filename: sessions[filename] for filename in sessions if filename not in jsons},
    )
