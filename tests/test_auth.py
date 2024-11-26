import pytest
import sqlite3
from unittest.mock import patch, MagicMock
from auth import Auth  
import hashlib

# Rest of your test code remains the same

# Fixture to create a test database connection
@pytest.fixture
def mock_db_connection():
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Create test tables
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            status TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE rewards (
            user_id INTEGER PRIMARY KEY,
            points INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE expert_details (
            user_id INTEGER PRIMARY KEY,
            scope TEXT,
            specialization TEXT,
            commodity TEXT,
            region TEXT,
            city TEXT
        )
    ''')
    
    return conn

# Fixture for Auth instance
@pytest.fixture
def auth():
    return Auth()

def test_hash_password():
    """Test password hashing functionality"""
    auth = Auth()
    password = "testpassword123"
    expected_hash = hashlib.sha256(password.encode()).hexdigest()
    assert auth.hash_password(password) == expected_hash

@patch('auth.create_connection')
def test_register_farmer(mock_create_connection, mock_db_connection):
    """Test farmer registration"""
    mock_create_connection.return_value = mock_db_connection
    auth = Auth()
    
    result = auth.register_user(
        username="testfarmer",
        password="password123",
        role="farmer",
        email="farmer@test.com",
        phone="1234567890"
    )
    
    assert result is True
    
    cursor = mock_db_connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", ("testfarmer",))
    user = cursor.fetchone()
    
    assert user is not None
    assert user[1] == "testfarmer"
    assert user[3] == "farmer"
    assert user[4] == "farmer@test.com"
    assert user[6] == "active"  # Status should be active for farmers

@patch('auth.create_connection')
@patch('builtins.input')
def test_register_expert(mock_input, mock_create_connection, mock_db_connection):
    """Test expert registration"""
    mock_create_connection.return_value = mock_db_connection
    
    # Mock input values for expert details
    mock_input.side_effect = [
        "1",  # scope
        "1",  # specialization
        "1",  # commodity
        "1",  # region
        "TestCity"  # city
    ]
    
    auth = Auth()
    result = auth.register_user(
        username="testexpert",
        password="password123",
        role="expert",
        email="expert@test.com",
        phone="1234567890"
    )
    
    assert result is True
    
    cursor = mock_db_connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", ("testexpert",))
    user = cursor.fetchone()
    
    assert user is not None
    assert user[1] == "testexpert"
    assert user[3] == "expert"
    assert user[6] == "pending"  # Status should be pending for experts
    
    # Check expert details
    cursor.execute("SELECT * FROM expert_details WHERE user_id = ?", (user[0],))
    expert_details = cursor.fetchone()
    assert expert_details is not None

@patch('auth.create_connection')
def test_login_success(mock_create_connection, mock_db_connection):
    """Test successful login"""
    mock_create_connection.return_value = mock_db_connection
    auth = Auth()
    
    # First register a user
    auth.register_user(
        username="testuser",
        password="password123",
        role="farmer",
        email="test@test.com",
        phone="1234567890"
    )
    
    # Try logging in
    result = auth.login("testuser", "password123")
    
    assert result is not None
    assert isinstance(result, dict)
    assert result['role'] == "farmer"

@patch('auth.create_connection')
def test_login_failure_wrong_password(mock_create_connection, mock_db_connection):
    """Test login failure with wrong password"""
    mock_create_connection.return_value = mock_db_connection
    auth = Auth()
    
    # First register a user
    auth.register_user(
        username="testuser",
        password="password123",
        role="farmer",
        email="test@test.com",
        phone="1234567890"
    )
    
    # Try logging in with wrong password
    result = auth.login("testuser", "wrongpassword")
    assert result is None

@patch('auth.create_connection')
def test_login_pending_expert(mock_create_connection, mock_db_connection):
    """Test login attempt by pending expert"""
    mock_create_connection.return_value = mock_db_connection
    auth = Auth()
    
    # Register an expert
    auth.register_user(
        username="testexpert",
        password="password123",
        role="expert",
        email="expert@test.com",
        phone="1234567890"
    )
    
    # Try logging in
    result = auth.login("testexpert", "password123")
    assert result is None

@patch('auth.create_connection')
def test_register_duplicate_username(mock_create_connection, mock_db_connection):
    """Test registration with duplicate username"""
    mock_create_connection.return_value = mock_db_connection
    auth = Auth()
    
    # Register first user
    auth.register_user(
        username="testuser",
        password="password123",
        role="farmer",
        email="test1@test.com",
        phone="1234567890"
    )
    
    # Try registering with same username
    result = auth.register_user(
        username="testuser",
        password="password123",
        role="farmer",
        email="test2@test.com",
        phone="1234567890"
    )
    
    assert result is False

def test_collect_expert_details(auth):
    """Test collecting expert details with mocked inputs"""
    with patch('builtins.input', side_effect=[
        "1",  # scope
        "1",  # specialization
        "1",  # commodity
        "1",  # region
        "TestCity"  # city
    ]):
        details = auth.collect_expert_details()
        
        assert isinstance(details, dict)
        assert details['scope'] == "Agri-Business"
        assert details['specialization'] == "Feed nutrition"
        assert details['commodity'] == "Grains & oilseeds"
        assert details['region'] == "North"
        assert details['city'] == "TestCity"

def test_collect_expert_details(auth):
    """Test collecting expert details with mocked inputs"""
    with patch('builtins.input', side_effect=[
        "1",  # scope
        "1",  # specialization
        "1",  # commodity
        "1",  # region
        "TestCity"  # city
    ]):
        details = auth.collect_expert_details()
        
        assert isinstance(details, dict)
        assert details['scope'] == "Agri-Business"
        assert details['specialization'] == "Feed nutrition"
        assert details['commodity'] == "Grains & oilseeds"
        assert details['region'] == "North"
        assert details['city'] == "TestCity"

@patch('auth.getpass')
@patch('builtins.input')
def test_display_registration_menu_farmer(mock_input, mock_getpass, auth):
    """Test the registration menu display for farmer"""
    mock_input.side_effect = [
        "testfarmer",  # username
        "farmer",      # role
        "test@farmer.com",  # email
        "1234567890"   # phone
    ]
    mock_getpass.return_value = "password123"  # password
    
    with patch.object(auth, 'register_user', return_value=True) as mock_register:
        result = auth.display_registration_menu()
        
        assert result is True
        mock_register.assert_called_once_with(
            "testfarmer", "password123", "farmer", "test@farmer.com", "1234567890"
        )

@patch('auth.getpass')
@patch('builtins.input')
def test_display_registration_menu_invalid_role(mock_input, mock_getpass, auth):
    """Test the registration menu display with invalid role"""
    mock_input.side_effect = [
        "testuser",    # username
        "invalid",     # invalid role
        "test@test.com",  # email
        "1234567890"   # phone
    ]
    mock_getpass.return_value = "password123"  # password
    
    result = auth.display_registration_menu()
    assert result is False

@patch('auth.getpass')
@patch('builtins.input')
def test_display_login_menu(mock_input, mock_getpass, auth):
    """Test the login menu display"""
    mock_input.return_value = "testuser"
    mock_getpass.return_value = "password123"
    
    with patch.object(auth, 'login', return_value={'id': 1, 'role': 'farmer'}) as mock_login:
        result = auth.display_login_menu()
        
        assert result == {'id': 1, 'role': 'farmer'}
        mock_login.assert_called_once_with("testuser", "password123")

@patch('auth.create_connection')
def test_register_user_database_error(mock_create_connection, auth):
    """Test registration when database connection fails"""
    mock_create_connection.return_value = None
    
    result = auth.register_user(
        username="testuser",
        password="password123",
        role="farmer",
        email="test@test.com",
        phone="1234567890"
    )
    
    assert result is False

@patch('auth.create_connection')
def test_login_database_error(mock_create_connection, auth):
    """Test login when database connection fails"""
    mock_create_connection.return_value = None
    
    result = auth.login("testuser", "password123")
    assert result is None

@pytest.mark.parametrize("invalid_input", [
    ("1", "99", "1", "1", "TestCity"),  # Invalid specialization
    ("99", "1", "1", "1", "TestCity"),  # Invalid scope
    ("1", "1", "99", "1", "TestCity"),  # Invalid commodity
    ("1", "1", "1", "99", "TestCity"),  # Invalid region
])
def test_collect_expert_details_invalid_inputs(auth, invalid_input):
    """Test collecting expert details with invalid inputs"""
    with patch('builtins.input', side_effect=invalid_input), \
         pytest.raises(IndexError):  # Should raise IndexError for invalid indices
        auth.collect_expert_details()

if __name__ == '__main__':
    pytest.main(['-v'])