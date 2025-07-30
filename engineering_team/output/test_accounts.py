import unittest
from unittest.mock import patch

class TestGetSharePrice(unittest.TestCase):
    """Tests for the get_share_price function."""
    
    def test_get_known_share_price(self):
        """Test getting prices for known stock symbols."""
        from accounts import get_share_price
        self.assertEqual(get_share_price('AAPL'), 150.0)
        self.assertEqual(get_share_price('TSLA'), 800.0)
        self.assertEqual(get_share_price('GOOGL'), 2500.0)
    
    def test_get_unknown_share_price(self):
        """Test getting prices for unknown stock symbols."""
        from accounts import get_share_price
        self.assertEqual(get_share_price('UNKNOWN'), 0.0)
        self.assertEqual(get_share_price(''), 0.0)


class TestAccount(unittest.TestCase):
    """Tests for the Account class."""
    
    def setUp(self):
        """Set up a test account before each test."""
        from accounts import Account
        self.account = Account('test123', 1000.0)
    
    def test_init(self):
        """Test account initialization."""
        self.assertEqual(self.account.account_id, 'test123')
        self.assertEqual(self.account.balance, 1000.0)
        self.assertEqual(self.account.initial_deposit, 1000.0)
        self.assertEqual(self.account.portfolio, {})
        self.assertEqual(len(self.account.transactions), 1)
        self.assertEqual(self.account.transactions[0], ("DEPOSIT", None, None, 1000.0))
    
    def test_deposit_valid(self):
        """Test depositing a valid amount."""
        self.account.deposit(500.0)
        self.assertEqual(self.account.balance, 1500.0)
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[1], ("DEPOSIT", None, None, 500.0))
    
    def test_deposit_invalid(self):
        """Test depositing invalid amounts (zero or negative)."""
        with self.assertRaises(ValueError):
            self.account.deposit(0)
        with self.assertRaises(ValueError):
            self.account.deposit(-100)
        # Balance should remain unchanged
        self.assertEqual(self.account.balance, 1000.0)
    
    def test_withdraw_valid(self):
        """Test withdrawing a valid amount."""
        result = self.account.withdraw(300.0)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 700.0)
        self.assertEqual(self.account.transactions[-1], ("WITHDRAW", None, None, 300.0))
    
    def test_withdraw_insufficient_funds(self):
        """Test withdrawing more than the available balance."""
        result = self.account.withdraw(1500.0)
        self.assertFalse(result)
        # Balance should remain unchanged
        self.assertEqual(self.account.balance, 1000.0)
        # No transaction should be recorded
        self.assertEqual(len(self.account.transactions), 1)
    
    def test_withdraw_invalid(self):
        """Test withdrawing invalid amounts (zero or negative)."""
        with self.assertRaises(ValueError):
            self.account.withdraw(0)
        with self.assertRaises(ValueError):
            self.account.withdraw(-100)
        # Balance should remain unchanged
        self.assertEqual(self.account.balance, 1000.0)
    
    def test_buy_shares_valid(self):
        """Test buying shares with sufficient funds."""
        result = self.account.buy_shares('AAPL', 5)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 250.0)  # 1000 - (5 * 150)
        self.assertEqual(self.account.portfolio, {'AAPL': 5})
        self.assertEqual(self.account.transactions[-1], ("BUY", 'AAPL', 5, 150.0))
    
    def test_buy_shares_insufficient_funds(self):
        """Test buying shares with insufficient funds."""
        result = self.account.buy_shares('GOOGL', 1)  # 2500 > 1000
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 1000.0)  # Unchanged
        self.assertEqual(self.account.portfolio, {})  # Unchanged
        self.assertEqual(len(self.account.transactions), 1)  # No new transaction
    
    def test_buy_shares_invalid_symbol(self):
        """Test buying shares with an invalid symbol."""
        result = self.account.buy_shares('INVALID', 5)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 1000.0)  # Unchanged
        self.assertEqual(self.account.portfolio, {})  # Unchanged
    
    def test_buy_shares_invalid_quantity(self):
        """Test buying an invalid quantity of shares (zero or negative)."""
        with self.assertRaises(ValueError):
            self.account.buy_shares('AAPL', 0)
        with self.assertRaises(ValueError):
            self.account.buy_shares('AAPL', -5)
        # Balance and portfolio should remain unchanged
        self.assertEqual(self.account.balance, 1000.0)
        self.assertEqual(self.account.portfolio, {})
    
    def test_buy_additional_shares(self):
        """Test buying additional shares of the same symbol."""
        self.account.buy_shares('AAPL', 3)
        self.account.buy_shares('AAPL', 2)
        self.assertEqual(self.account.portfolio, {'AAPL': 5})
        self.assertEqual(self.account.balance, 250.0)  # 1000 - 3*150 - 2*150
    
    def test_sell_shares_valid(self):
        """Test selling shares successfully."""
        # First buy some shares
        self.account.buy_shares('TSLA', 1)  # Balance becomes 200 (1000 - 800)
        
        # Now sell them
        result = self.account.sell_shares('TSLA', 1)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 1000.0)  # 200 + 800
        self.assertEqual(self.account.portfolio, {})  # All shares sold
        self.assertEqual(self.account.transactions[-1], ("SELL", 'TSLA', 1, 800.0))
    
    def test_sell_shares_insufficient_shares(self):
        """Test selling more shares than owned."""
        # First buy some shares
        self.account.buy_shares('AAPL', 2)  # Balance becomes 700 (1000 - 2*150)
        
        # Try to sell more than owned
        result = self.account.sell_shares('AAPL', 3)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 700.0)  # Unchanged
        self.assertEqual(self.account.portfolio, {'AAPL': 2})  # Unchanged
    
    def test_sell_shares_invalid_symbol(self):
        """Test selling shares with an invalid symbol."""
        result = self.account.sell_shares('INVALID', 1)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 1000.0)  # Unchanged
    
    def test_sell_shares_symbol_not_in_portfolio(self):
        """Test selling shares not in portfolio."""
        result = self.account.sell_shares('AAPL', 1)  # Not owned
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 1000.0)  # Unchanged
        self.assertEqual(self.account.portfolio, {})  # Unchanged
    
    def test_sell_shares_invalid_quantity(self):
        """Test selling an invalid quantity of shares (zero or negative)."""
        # First buy some shares
        self.account.buy_shares('AAPL', 2)
        
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', 0)
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', -1)
        # Balance and portfolio should remain unchanged
        self.assertEqual(self.account.balance, 700.0)  # 1000 - 2*150
        self.assertEqual(self.account.portfolio, {'AAPL': 2})
    
    def test_get_portfolio_value(self):
        """Test calculating the portfolio value."""
        # Empty portfolio
        self.assertEqual(self.account.get_portfolio_value(), 0.0)
        
        # Add some shares
        self.account.buy_shares('AAPL', 2)  # 2 * 150 = 300
        self.account.buy_shares('TSLA', 1)  # 1 * 800 = 800
        
        # Portfolio value should be 1100
        self.assertEqual(self.account.get_portfolio_value(), 1100.0)
    
    def test_get_profit_or_loss_no_change(self):
        """Test profit/loss calculation with no price changes."""
        # No activity, so no profit/loss
        self.assertEqual(self.account.get_profit_or_loss(), 0.0)
    
    def test_get_profit_or_loss_with_activity(self):
        """Test profit/loss calculation with price changes."""
        # Buy some shares
        self.account.buy_shares('AAPL', 2)  # Balance becomes 700, portfolio value 300
        
        # No profit/loss yet since total value is still 1000
        self.assertEqual(self.account.get_profit_or_loss(), 0.0)
        
        # Simulate price increase by mocking get_share_price
        with patch('accounts.get_share_price', return_value=200.0):
            # Portfolio value is now 2 * 200 = 400, balance is 700, total 1100
            self.assertEqual(self.account.get_profit_or_loss(), 100.0)
    
    def test_get_holdings(self):
        """Test getting holdings from the portfolio."""
        # Empty portfolio
        self.assertEqual(self.account.get_holdings(), {})
        
        # Add some shares
        self.account.buy_shares('AAPL', 3)
        self.account.buy_shares('TSLA', 1)
        
        # Check holdings
        self.assertEqual(self.account.get_holdings(), {'AAPL': 3, 'TSLA': 1})
        
        # Verify that get_holdings returns a copy
        holdings = self.account.get_holdings()
        holdings['AAPL'] = 10
        self.assertEqual(self.account.portfolio['AAPL'], 3)  # Original unchanged
    
    def test_list_transactions(self):
        """Test listing all transactions."""
        # Initial deposit transaction
        transactions = self.account.list_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0], ("DEPOSIT", None, None, 1000.0))
        
        # Add some transactions
        self.account.deposit(500.0)
        self.account.buy_shares('AAPL', 2)
        self.account.withdraw(100.0)
        
        # Check transactions
        transactions = self.account.list_transactions()
        self.assertEqual(len(transactions), 4)
        self.assertEqual(transactions[1], ("DEPOSIT", None, None, 500.0))
        self.assertEqual(transactions[2], ("BUY", "AAPL", 2, 150.0))
        self.assertEqual(transactions[3], ("WITHDRAW", None, None, 100.0))
        
        # Verify that list_transactions returns a copy
        transactions = self.account.list_transactions()
        transactions.append(("FAKE", None, None, 0.0))
        self.assertEqual(len(self.account.transactions), 4)  # Original unchanged


if __name__ == '__main__':
    unittest.main()