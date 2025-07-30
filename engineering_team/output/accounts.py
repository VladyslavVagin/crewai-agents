def get_share_price(symbol: str) -> float:
    """Returns the current price for a given share symbol.
    This is a test implementation that returns fixed prices for AAPL, TSLA, and GOOGL.
    """
    prices = {
        'AAPL': 150.0,
        'TSLA': 800.0,
        'GOOGL': 2500.0
    }
    return prices.get(symbol, 0.0)

class Account:
    """A class representing a trading account in a simulation platform."""
    
    def __init__(self, account_id: str, initial_deposit: float) -> None:
        """Initialize a new account with a given ID and initial deposit amount.
        
        Args:
            account_id: Unique identifier for the account
            initial_deposit: Initial amount of money deposited
        """
        self.account_id = account_id
        self.balance = initial_deposit
        self.initial_deposit = initial_deposit
        self.portfolio = {}
        self.transactions = [("DEPOSIT", None, None, initial_deposit)]
    
    def deposit(self, amount: float) -> None:
        """Increase the account balance by the specified deposit amount.
        
        Args:
            amount: Amount to deposit
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        self.balance += amount
        self.transactions.append(("DEPOSIT", None, None, amount))
    
    def withdraw(self, amount: float) -> bool:
        """Attempt to withdraw the specified amount from the account balance.
        
        Args:
            amount: Amount to withdraw
            
        Returns:
            True if withdrawal was successful, False otherwise
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if amount > self.balance:
            return False
        
        self.balance -= amount
        self.transactions.append(("WITHDRAW", None, None, amount))
        return True
    
    def buy_shares(self, symbol: str, quantity: int) -> bool:
        """Buy a specified quantity of shares for the given symbol.
        
        Args:
            symbol: Stock symbol to buy
            quantity: Number of shares to buy
            
        Returns:
            True if purchase was successful, False otherwise
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        price = get_share_price(symbol)
        if price == 0.0:
            return False  # Symbol not found
        
        total_cost = price * quantity
        
        if total_cost > self.balance:
            return False  # Insufficient funds
        
        # Update balance and portfolio
        self.balance -= total_cost
        
        if symbol in self.portfolio:
            self.portfolio[symbol] += quantity
        else:
            self.portfolio[symbol] = quantity
            
        # Record transaction
        self.transactions.append(("BUY", symbol, quantity, price))
        return True
    
    def sell_shares(self, symbol: str, quantity: int) -> bool:
        """Sell a specified quantity of shares for the given symbol.
        
        Args:
            symbol: Stock symbol to sell
            quantity: Number of shares to sell
            
        Returns:
            True if sale was successful, False otherwise
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        # Check if user has enough shares
        if symbol not in self.portfolio or self.portfolio[symbol] < quantity:
            return False
        
        price = get_share_price(symbol)
        if price == 0.0:
            return False  # Symbol not found
        
        # Update balance and portfolio
        total_amount = price * quantity
        self.balance += total_amount
        
        self.portfolio[symbol] -= quantity
        
        # Remove symbol from portfolio if no shares left
        if self.portfolio[symbol] == 0:
            del self.portfolio[symbol]
            
        # Record transaction
        self.transactions.append(("SELL", symbol, quantity, price))
        return True
    
    def get_portfolio_value(self) -> float:
        """Calculate the current total value of all shares in the portfolio.
        
        Returns:
            Total portfolio value
        """
        total_value = 0.0
        
        for symbol, quantity in self.portfolio.items():
            price = get_share_price(symbol)
            total_value += price * quantity
            
        return total_value
    
    def get_profit_or_loss(self) -> float:
        """Compute the net profit or loss.
        
        Returns:
            Net profit or loss
        """
        total_value = self.get_portfolio_value() + self.balance
        return total_value - self.initial_deposit
    
    def get_holdings(self) -> dict:
        """Return a copy of the portfolio dictionary.
        
        Returns:
            Dictionary representing current holdings
        """
        return self.portfolio.copy()
    
    def list_transactions(self) -> list:
        """Return a list of all recorded transactions.
        
        Returns:
            List of transactions
        """
        return self.transactions.copy()