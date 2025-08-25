from glob import glob
import os


def glob_files(path: str, must_have_json: bool = False) -> dict[str, dict[str, str]]:
    """Находит .session и .json файлы в указанной директории.

    Args:
        path: Путь к директории для поиска.
        must_have_json: Если True, включает только сессии с соответствующим JSON.

    Returns:
        Словарь вида {имя_файла: {"session_file": путь, "json_file": путь_или_None}}.

    Example:
        >>> files = glob_files("./sessions")
        >>> for name, paths in files.items():
        >>>     print(f"Аккаунт: {name}")
        >>>     print(f"Сессия: {paths['session_file']}")
        >>>     if paths['json_file']:
        >>>         print(f"JSON: {paths['json_file']}")
    """
    session_files = glob(f"{path}/*.session") + glob(f"{path}/**/*.session", recursive=True)
    sessions = {os.path.basename(path).split(".")[0].lower(): path for path in session_files}

    json_files = glob(f"{path}/*.json") + glob(f"{path}/**/*.json", recursive=True)
    jsons = {os.path.basename(path).split(".")[0].lower(): path for path in json_files}

    return {
        filename: dict(session_file=sessions[filename], json_file=jsons.get(filename))
        for filename in sessions
        if not must_have_json or filename in jsons
    }
