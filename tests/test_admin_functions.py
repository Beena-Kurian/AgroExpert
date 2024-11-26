import unittest
from unittest.mock import patch, MagicMock
from admin_functions import AdminFunctions
from db import create_connection
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestAdminFunctions(unittest.TestCase):

    def setUp(self):
        self.admin = AdminFunctions()

    # Positive Test Case for Display Admin Menu-ok
    @pytest.mark.positive
    @patch('builtins.input', side_effect=['6'])  # Simulate 'Logout' choice
    def test_display_admin_menu_valid_choice(self, mock_input):
        with patch('builtins.print') as mock_print:
            self.admin.display_admin_menu()
            mock_print.assert_any_call("\n=== Admin Menu ===")

    # Negative Test Case for Display Admin Menu-ok
    @patch('builtins.input', side_effect=['invalid', '6'])  # Invalid input, then 'Logout'
    def test_display_admin_menu_invalid_choice(self, mock_input):
        with patch('builtins.print') as mock_print:
            self.admin.display_admin_menu()
            mock_print.assert_any_call("Invalid choice! Please try again.")

    # Positive Test Case for View All Users
    @patch('db.create_connection')
    def test_view_all_users_with_data(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [
            (1, 'user1', 'farmer', 'user1@example.com', 'active'),
            (2, 'user2', 'expert', 'user2@example.com', 'active'),
        ]
        mock_db.return_value = mock_conn

        with patch('builtins.print') as mock_print:
            self.admin.view_all_users()
            mock_print.assert_any_call("ID: 1")
            mock_print.assert_any_call("Username: user1")
            mock_print.assert_any_call("Role: admin")

    # Negative Test Case for View All Users-ok
    @patch('db.create_connection')
    def test_view_all_users_no_data(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = []  # Empty result
        mock_db.return_value = mock_conn

        with patch('builtins.print') as mock_print:
            self.admin.view_all_users()
            mock_print.assert_any_call("No users found.")

    # Positive Test Case for Model Management - View Model Versions
    @patch('db.create_connection')
    def test_view_model_versions_with_data(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [
            ('v1.0', 0.95, 10, '2024-01-01', 'Initial version', 1),
        ]
        mock_db.return_value = mock_conn

        with patch('builtins.print') as mock_print:
            self.admin.view_model_versions()
            mock_print.assert_any_call("Version: v1.0")
            mock_print.assert_any_call("Accuracy: 95.00%")

    # Negative Test Case for Model Management - View Model Versions
    @patch('db.create_connection')
    def test_view_model_versions_no_data(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = []  # Empty result
        mock_db.return_value = mock_conn

        with patch('builtins.print') as mock_print:
            self.admin.view_model_versions()
            mock_print.assert_any_call("\n=== Model Versions ===")

    # Positive Test for View System Statistics
    @patch('db.create_connection')
    def test_view_system_statistics_with_data(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        # Mock user statistics
        mock_cursor.execute.side_effect = [
            [(1, 'admin', 10), (2, 'user', 20)],  # User stats
            [(1, 'completed', 15), (2, 'pending', 5)],  # Consultation stats
            [('Flu', 8), ('COVID-19', 6), ('Allergy', 4)]  # Disease stats
        ]
        mock_db.return_value = mock_conn

        with patch('builtins.print') as mock_print:
            self.admin.view_system_statistics()
            mock_print.assert_any_call("\nUser Statistics:")
            mock_print.assert_any_call("Admin: 10")
            mock_print.assert_any_call("\nConsultation Statistics:")
            mock_print.assert_any_call("Completed: 15")

    # Negative Test for View System Statistics (No Data)
    @patch('db.create_connection')
    def test_view_system_statistics_no_data(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.execute.side_effect = [[], [], []]  # Empty results for all queries
        mock_db.return_value = mock_conn

        with patch('builtins.print') as mock_print:
            self.admin.view_system_statistics()
            mock_print.assert_any_call("No user statistics available.")
            mock_print.assert_any_call("No consultation statistics available.")
            mock_print.assert_any_call("No disease prediction statistics available.")

    # Positive Test for Add News
    @patch('db.create_connection')
    def test_add_news_success(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_db.return_value = mock_conn

        with patch('builtins.input', side_effect=["Test News", "Content Line 1", "Content Line 2", ""]):
            with patch('builtins.print') as mock_print:
                self.admin.add_news("Test News", "Content Line 1\nContent Line 2")
                mock_cursor.execute.assert_called_with(
                    '''
                    INSERT INTO news (title, content, created_at)
                    VALUES (?, ?, datetime('now'))
                    ''', 
                    ("Test News", "Content Line 1\nContent Line 2")
                )
                mock_print.assert_any_call("News added successfully!")

    # Negative Test for Add News (No Content)
    @patch('builtins.print')
    def test_add_news_missing_content(self, mock_print):
        with patch('db.create_connection', return_value=None):
            self.admin.add_news("Test News", "")
            mock_print.assert_any_call("Error adding news:")


    # Positive Test for View All News
    @patch('db.create_connection')
    def test_view_all_news(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [
            (1, "Title 1", "Content 1", "2024-01-01"),
            (2, "Title 2", "Content 2", "2024-01-02"),
        ]
        mock_db.return_value = mock_conn

        with patch('builtins.print') as mock_print:
            self.admin.view_all_news()
            mock_print.assert_any_call("Title 1")
            mock_print.assert_any_call("Content 1")
            mock_print.assert_any_call("2024-01-01")

    # Negative Test for View All News (No News)
    @patch('db.create_connection')
    def test_view_all_news_no_news(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = []  # No news
        mock_db.return_value = mock_conn

        with patch('builtins.print') as mock_print:
            self.admin.view_all_news()
            mock_print.assert_any_call("No news available.")

    # Positive Test for Delete News
    @patch('db.create_connection')
    def test_delete_news(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_db.return_value = mock_conn

        with patch('builtins.input', side_effect=["1"]):  # Simulate input for news ID
            with patch('builtins.print') as mock_print:
                self.admin.delete_news()
                mock_cursor.execute.assert_called_with(
                    "DELETE FROM news WHERE id = ?", (1,)
                )
                mock_print.assert_any_call("News deleted successfully!")

    # Negative Test for Delete News (Invalid ID)
    @patch('db.create_connection')
    def test_delete_news_invalid_id(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.execute.side_effect = Exception("Invalid ID")  # Simulate DB error
        mock_db.return_value = mock_conn

        with patch('builtins.input', side_effect=["999"]):  # Non-existent ID
            with patch('builtins.print') as mock_print:
                self.admin.delete_news()
                mock_print.assert_any_call("Error deleting news:")

    # Positive Test for View All News
    @patch('db.create_connection')
    def test_view_all_news_with_data(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [
            (1, "Title 1", "Content 1", "2024-01-01"),
            (2, "Title 2", "Content 2", "2024-01-02"),
        ]
        mock_db.return_value = mock_conn

        with patch('builtins.print') as mock_print:
            self.admin.view_all_news()
            mock_print.assert_any_call("Title: Title 1")
            mock_print.assert_any_call("Content: Content 1")

    # Negative Test for View All News (No Data)
    @patch('db.create_connection')
    def test_view_all_news_no_data(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = []  # Empty result
        mock_db.return_value = mock_conn

        with patch('builtins.print') as mock_print:
            self.admin.view_all_news()
            mock_print.assert_any_call("No news items found.")

    # Positive Test for Delete News
    @patch('db.create_connection')
    def test_delete_news_success(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [(1, "Title 1")]
        mock_cursor.rowcount = 1
        mock_db.return_value = mock_conn

        with patch('builtins.input', side_effect=["1"]):  # Simulate valid ID
            with patch('builtins.print') as mock_print:
                self.admin.delete_news()
                mock_print.assert_any_call("News deleted successfully!")

    # Negative Test for Delete News (Invalid ID)
    @patch('db.create_connection')
    def test_delete_news_invalid_id(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [(1, "Title 1")]
        mock_cursor.rowcount = 0  # Simulate no deletion
        mock_db.return_value = mock_conn

        with patch('builtins.input', side_effect=["999"]):  # Non-existent ID
            with patch('builtins.print') as mock_print:
                self.admin.delete_news()
                mock_print.assert_any_call("News item not found!")

    # Positive Test for Get Valid Path
    @patch('os.path.exists', return_value=True)
    @patch('os.path.isdir', return_value=True)
    def test_get_valid_path_success(self, mock_isdir, mock_exists):
        with patch('builtins.input', side_effect=["/valid/path"]):  # Valid path
            result = self.admin.get_valid_path("Enter a valid path: ")
            self.assertEqual(result, "/valid/path")

    # Negative Test for Get Valid Path
    @patch('os.path.exists', side_effect=[False, True])  # First invalid, then valid
    @patch('os.path.isdir', side_effect=[False, True])  # First invalid, then valid
    def test_get_valid_path_failure(self, mock_isdir, mock_exists):
        with patch('builtins.input', side_effect=["/invalid/path", "/valid/path"]):
            with patch('builtins.print') as mock_print:
                result = self.admin.get_valid_path("Enter a valid path: ")
                mock_print.assert_any_call("Invalid path: Path '/invalid/path' does not exist.")
                self.assertEqual(result, "/valid/path")

    # Positive Test for Train New Model
    @patch('admin_functions.ModelTrainer')
    @patch('admin_functions.create_connection')
    @patch('builtins.input', side_effect=["1", "15", "0.001", "/valid/dataset"])
    def test_train_new_model_success(self, mock_input, mock_db, mock_trainer):
        trainer_mock = mock_trainer.return_value
        trainer_mock.evaluate_model.return_value = 0.8  # Simulate high accuracy
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_db.return_value = mock_conn

        with patch('builtins.print') as mock_print:
            self.admin.train_new_model()
            mock_print.assert_any_call("Model saved and recorded in database successfully!")

    # Negative Test for Train New Model (Low Accuracy)
    @patch('admin_functions.ModelTrainer')
    @patch('builtins.input', side_effect=["1", "15", "0.001", "/valid/dataset"])
    def test_train_new_model_low_accuracy(self, mock_input, mock_trainer):
        trainer_mock = mock_trainer.return_value
        trainer_mock.evaluate_model.return_value = 0.5  # Simulate low accuracy

        with patch('builtins.print') as mock_print:
            self.admin.train_new_model()
            mock_print.assert_any_call("Model accuracy too low. Consider adjusting parameters and training again.")


    @patch('db.create_connection')
    def test_register_farmer(self, mock_db):
        mock_conn = MagicMock()
        mock_db.return_value = mock_conn
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = None  # Simulate valid DB state
        result = self.auth.register_user("farmer", "test_user", "password")
        self.assertEqual(result, "Registration successful!")

if __name__ == '__main__':
    unittest.main()
