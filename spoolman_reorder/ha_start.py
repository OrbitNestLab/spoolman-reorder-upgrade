"""Home Assistant entrypoint. Import a source DB once, using SQLite backup."""

import json
import os
import re
import sqlite3
from contextlib import closing
from pathlib import Path


def import_database(source_root: Path, target: Path, slug: str) -> bool:
    if not slug or target.exists():
        return False
    if not re.fullmatch(r"[a-zA-Z0-9]+_[a-zA-Z0-9_-]+", slug):
        raise ValueError("Invalid source app slug")
    source = source_root / slug / "spoolman.db"
    if not source.is_file():
        raise FileNotFoundError("The selected app has no accessible spoolman.db")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".importing")
    try:
        with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True, timeout=30)) as src:
            with closing(sqlite3.connect(temporary)) as dst:
                src.backup(dst)
                if dst.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise ValueError("Imported database failed integrity_check")
        temporary.replace(target)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return True


def main() -> None:
    options = json.loads(Path("/data/options.json").read_text())
    root = Path("/data/spoolman")
    root.mkdir(exist_ok=True)
    imported = import_database(Path("/app_configs"), root / "spoolman.db", options.get("import_from_app", ""))
    if imported:
        print("Imported a consistent inventory copy; the source was opened read-only.", flush=True)
    for name in ("backups", "logs", "cache"):
        (root / name).mkdir(exist_ok=True)
    for directory, _, files in os.walk(root):
        os.chown(directory, 1000, 1000)
        for name in files:
            os.chown(Path(directory) / name, 1000, 1000)
    os.environ["SPOOLMAN_DEBUG_MODE"] = "TRUE" if options.get("debug") else "FALSE"
    os.environ["SPOOLMAN_LEGACY_CLIENT"] = "TRUE" if options.get("legacy_client") else "FALSE"
    if options.get("cors_origin"):
        os.environ["SPOOLMAN_CORS_ORIGIN"] = options["cors_origin"]
    os.execv("/home/app/spoolman/entrypoint.sh", ["/home/app/spoolman/entrypoint.sh"])


if __name__ == "__main__":
    main()
