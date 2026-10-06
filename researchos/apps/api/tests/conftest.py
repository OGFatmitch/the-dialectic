import os, sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

@pytest.fixture(autouse=True)
def isolated_db(tmp_path):
    os.environ["RESEARCHOS_DB"] = str(tmp_path / "test.db")
    from app.database import initialize
    initialize()
    yield
    os.environ.pop("RESEARCHOS_DB", None)
