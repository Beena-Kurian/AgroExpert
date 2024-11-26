import unittest
from unittest.mock import patch, MagicMock
import sys
import os
# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from admin_functions import AdminFunctions
from gift_card import add_coupon, add_multiple_coupons, view_coupons, deactivate_coupon

class TestGiftCardManagement(unittest.TestCase):

    def setUp(self):
        self.admin = AdminFunctions()

    # Positive Test for Adding a Single Gift Card
    @patch('gift_card.add_coupon')
    def test_add_single_gift_card_ok(self, mock_add_coupon):
        with patch('builtins.input', side_effect=["100", "30"]):  # Valid input
            self.admin.gift_card_management_menu()
            mock_add_coupon.assert_called_with(100, 30)

    # Negative Test for Adding a Single Gift Card
    @patch('builtins.print')
    def test_add_single_gift_card_invalid_input(self, mock_print):
        with patch('builtins.input', side_effect=["A", "S"]):  # Invalid inputs
            self.admin.gift_card_management_menu()
            mock_print.assert_any_call("Invalid input! Please enter numerical values.")

    # Positive Test for Adding Multiple Gift Cards
    @patch('gift_card.add_multiple_coupons')
    def test_add_multiple_gift_cards_ok(self, mock_add_multiple_coupons):
        with patch('builtins.input', side_effect=["100", "30", "5"]):  # Valid input
            self.admin.gift_card_management_menu()
            mock_add_multiple_coupons.assert_called_with(100, 30, 5)

    # Negative Test for Adding Multiple Gift Cards
    @patch('builtins.print')
    def test_add_multiple_gift_cards_invalid_input(self, mock_print):
        with patch('builtins.input', side_effect=["100", "invalid", "5"]):  # Invalid days
            self.admin.gift_card_management_menu()
            mock_print.assert_any_call("Invalid input! Please enter numerical values.")

    # Positive Test for Viewing All Gift Cards
    @patch('gift_card.view_coupons')
    @patch('builtins.print')
    def test_view_all_gift_cards_ok(self, mock_print, mock_view_coupons):
        mock_view_coupons.return_value = None  # Simulate no return value
        self.admin.gift_card_management_menu()
        mock_view_coupons.assert_called_once()
        mock_print.assert_any_call("=== Gift Card Management ===")

    # Positive Test for Deactivating a Gift Card
    @patch('gift_card.deactivate_coupon')
    def test_deactivate_gift_card_ok(self, mock_deactivate_coupon):
        with patch('builtins.input', side_effect=["4"]):  # Valid coupon ID
            self.admin.gift_card_management_menu()
            mock_deactivate_coupon.assert_called_with(4)

    # Negative Test for Deactivating a Gift Card
    @patch('builtins.print')
    def test_deactivate_gift_card_invalid_id(self, mock_print):
        with patch('builtins.input', side_effect=["invalid", ""]):  # Non-numeric and empty inputs
            self.admin.gift_card_management_menu()
            mock_print.assert_any_call("Invalid input! Please enter a valid gift card ID.")

    # Positive Test for Menu Navigation
    @patch('builtins.input', side_effect=["5"])  # Exit to admin menu
    def test_gift_card_menu_navigation_ok(self, mock_input):
        with patch('builtins.print') as mock_print:
            self.admin.gift_card_management_menu()
            mock_print.assert_any_call("=== Gift Card Management ===")

if __name__ == '__main__':
    unittest.main()
