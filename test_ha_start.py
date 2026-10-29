import importlib.util
import sqlite3
from pathlib import Path

import pytest

spec=importlib.util.spec_from_file_location("ha_start",Path(__file__).parent/"spoolman_reorder/ha_start.py")
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_import_is_consistent_read_only_and_once(tmp_path):
    source=tmp_path/"apps"/"2c829f0e_spoolman"
    source.mkdir(parents=True)
    db=source/"spoolman.db"
    with sqlite3.connect(db) as c:
        c.execute("CREATE TABLE item(id INTEGER PRIMARY KEY, value TEXT)")
        c.execute("INSERT INTO item VALUES (1, 'original')")
    before=db.read_bytes()
    target=tmp_path/"new"/"spoolman.db"
    assert module.import_database(tmp_path/"apps",target,"2c829f0e_spoolman")
    assert db.read_bytes()==before
    with sqlite3.connect(target) as c:
        assert c.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        c.execute("UPDATE item SET value='test change'")
    assert not module.import_database(tmp_path/"apps",target,"2c829f0e_spoolman")
    assert db.read_bytes()==before
    with sqlite3.connect(target) as c:
        assert c.execute("SELECT value FROM item").fetchone()[0]=="test change"


def test_invalid_import_never_creates_a_database(tmp_path):
    target=tmp_path/"spoolman.db"
    with pytest.raises(ValueError): module.import_database(tmp_path,target,"../escape")
    with pytest.raises(FileNotFoundError): module.import_database(tmp_path,target,"missing_app")
    assert not target.exists()
