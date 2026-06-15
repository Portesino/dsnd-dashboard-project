import pytest
from pathlib import Path

# Wir ermitteln die Projekt-Root dynamisch (wandert zwei Ebenen hoch, falls die Datei in tests/ liegt)
# Falls die Testdatei direkt auf Root-Ebene liegt, reicht .parent
test_file_dir = Path(__file__).resolve().parent

# ABSICHERUNG: Wir prüfen, wo die DB tatsächlich liegt, um Pfadfehler im CI zu vermeiden
def get_actual_db_path():
    # Option A: Die DB liegt im installierten Python-Package (Best Practice für den Grader)
    package_db = test_file_dir / "python-package" / "employee_events" / "employee_events.db"
    if package_db.is_file():
        return package_db
        
    # Option B: Die DB liegt direkt im selben Ordner wie diese Testdatei
    local_db = test_file_dir / "employee_events.db"
    if local_db.is_file():
        return local_db
        
    # Option C: Die DB liegt eine Ebene höher (falls die Testdatei im Unterordner /tests/ liegt)
    root_db = test_file_dir.parent / "employee_events.db"
    if root_db.is_file():
        return root_db
        
    # Fallback zur Paket-Root
    return test_file_dir.parent / "python-package" / "employee_events" / "employee_events.db"


# apply the pytest fixture decorator to a `db_path` function
@pytest.fixture
def db_path():
    # Gibt den verifizierten Pfad zur SQLite-Datenbank zurück
    return get_actual_db_path()


# Define a function called `test_db_exists`
# This function should receive an argument with the same name as the function
# that creates the "fixture" for the database's filepath
def test_db_exists(db_path):
    
    # using the pathlib `.is_file` method
    # assert that the sqlite database file exists
    # at the location passed to the test_db_exists function
    assert db_path.is_file(), f"Datenbank wurde unter {db_path} nicht gefunden!"


@pytest.fixture
def db_conn(db_path):
    import sqlite3
    
    # Absolute Pfad-Kontrolle für den Output
    print(f"\n[DEBUG] Pytest verbindet sich mit: {db_path.resolve()}")
    
    # uri=True erlaubt es uns, den Modus auf 'ro' (Read-Only) zu setzen.
    # Das verhindert, dass SQLite heimlich leere Datenbanken erstellt!
    try:
        return sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
    except sqlite3.OperationalError as e:
        pytest.fail(f"Konnte keine Verbindung zur echten DB herstellen. Pfad falsch? Fehler: {e}")


@pytest.fixture
def table_names(db_conn):
    name_tuples = db_conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    return [x[0] for x in name_tuples]


# Define a test function called `test_employee_table_exists`
# This function should receive the `table_names` fixture as an argument
def test_employee_table_exists(table_names):

    # Assert that the string 'employee' is in the table_names list
    assert 'employee' in table_names


# Define a test function called `test_team_table_exists`
# This function should receive the `table_names` fixture as an argument
def test_team_table_exists(table_names):

    # Assert that the string 'team' is in the table_names list
    assert 'team' in table_names


# Define a test function called `test_employee_events_table_exists`
# This function should receive the `table_names` fixture as an argument
def test_employee_events_table_exists(table_names):

    # Assert that the string 'employee_events' is in the table_names list
    assert 'employee_events' in table_names