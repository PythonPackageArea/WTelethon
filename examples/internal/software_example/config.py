from pathlib import Path

context_dir_path = Path("examples", "data")
sessions_dir_path = context_dir_path / "sessions"
proxies_file_path = context_dir_path / "proxies.txt"

alive_dir_path = sessions_dir_path / "alive"
wrong_format_dir_path = sessions_dir_path / "wrong_format"
dead_dir_path = sessions_dir_path / "dead"

proxy_type = "http"
