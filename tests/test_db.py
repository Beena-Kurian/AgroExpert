# Automatic testing of config and db using pytest
import pytest
import sqlite3
import sys
import os

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import initialize_system
from db import create_connection, init_model_classes

@pytest.fixture
def test_db():
    """
    Fixture for creating an in-memory SQLite database for testing.
    """
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()

# POSITIVE TEST CASES
def test_initialize_system():
    """
    Test the system initialization using config.py.
    """
    result = initialize_system()
    assert result is True, "System initialization should complete successfully"

    # Verify that tables are created as expected
    conn = sqlite3.connect("data/agroexpert.db")
    cursor = conn.cursor()

    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    table_names = [table[0] for table in tables]
    expected_tables = [
        "users", "expert_details", "diseases", "disease_predictions", "consultations",
        "consultation_responses", "rewards", "reward_transactions", "news",
        "model_versions", "unknown_diseases", "disease_samples", "model_classes","coupons","coupon_usage"
    ]
    for table in expected_tables:
        assert table in table_names, f"Table {table} should exist after system initialization"
    
    conn.close()


def test_create_connection():
    """
    Test the database connection creation from db.py.
    """
    conn = create_connection()
    assert conn is not None, "Database connection should not be None"


def test_init_model_classes():
    conn = create_connection()
    init_model_classes()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM model_classes")
    count = cursor.fetchone()[0]
    assert count > 0, "Model classes should be initialized with entries"



# NEGATIVE TEST CASES
def test_create_connection_invalid_path(monkeypatch):
    """
    Test connection creation with an invalid path, expecting failure.
    """
    monkeypatch.setattr("db.sqlite3.connect", lambda _: (_ for _ in ()).throw(Exception("Invalid Path")))
    conn = create_connection()
    assert conn is None, "Connection should fail with an invalid path"
