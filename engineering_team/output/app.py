import gradio as gr
from accounts import Account, get_share_price

# Create a single account for the demo
account = None

def initialize_account(account_id, initial_deposit):
    global account
    try:
        initial_deposit = float(initial_deposit)
        if initial_deposit <= 0:
            return f"❌ Error: Initial deposit must be positive"
        account = Account(account_id, initial_deposit)
        return f"✅ Account {account_id} created with initial deposit of ${initial_deposit:.2f}"
    except ValueError:
        return f"❌ Error: Please enter a valid number for initial deposit"

def deposit_funds(amount):
    global account
    if account is None:
        return "❌ Error: Please create an account first"
    
    try:
        amount = float(amount)
        account.deposit(amount)
        return f"✅ Deposited ${amount:.2f}. New balance: ${account.balance:.2f}"
    except ValueError as e:
        return f"❌ Error: {str(e)}"

def withdraw_funds(amount):
    global account
    if account is None:
        return "❌ Error: Please create an account first"
    
    try:
        amount = float(amount)
        if account.withdraw(amount):
            return f"✅ Withdrew ${amount:.2f}. New balance: ${account.balance:.2f}"
        else:
            return f"❌ Error: Insufficient funds. Current balance: ${account.balance:.2f}"
    except ValueError as e:
        return f"❌ Error: {str(e)}"

def buy_stock(symbol, quantity):
    global account
    if account is None:
        return "❌ Error: Please create an account first"
    
    try:
        quantity = int(quantity)
        if account.buy_shares(symbol.upper(), quantity):
            return f"✅ Bought {quantity} shares of {symbol.upper()} at ${get_share_price(symbol.upper()):.2f} per share.\nNew balance: ${account.balance:.2f}"
        else:
            price = get_share_price(symbol.upper())
            if price == 0.0:
                return f"❌ Error: Symbol {symbol.upper()} not found"
            else:
                return f"❌ Error: Insufficient funds. Cost would be ${price * quantity:.2f}, but your balance is ${account.balance:.2f}"
    except ValueError as e:
        return f"❌ Error: {str(e)}"

def sell_stock(symbol, quantity):
    global account
    if account is None:
        return "❌ Error: Please create an account first"
    
    try:
        quantity = int(quantity)
        if account.sell_shares(symbol.upper(), quantity):
            return f"✅ Sold {quantity} shares of {symbol.upper()} at ${get_share_price(symbol.upper()):.2f} per share.\nNew balance: ${account.balance:.2f}"
        else:
            if symbol.upper() not in account.portfolio:
                return f"❌ Error: You don't own any shares of {symbol.upper()}"
            else:
                return f"❌ Error: You only have {account.portfolio[symbol.upper()]} shares of {symbol.upper()}, but attempted to sell {quantity}"
    except ValueError as e:
        return f"❌ Error: {str(e)}"

def get_account_summary():
    global account
    if account is None:
        return "❌ Error: Please create an account first"
    
    portfolio_value = account.get_portfolio_value()
    profit_loss = account.get_profit_or_loss()
    
    summary = f"Account ID: {account.account_id}\n"
    summary += f"Cash Balance: ${account.balance:.2f}\n"
    summary += f"Initial Deposit: ${account.initial_deposit:.2f}\n"
    summary += f"Portfolio Value: ${portfolio_value:.2f}\n"
    summary += f"Total Value: ${(account.balance + portfolio_value):.2f}\n"
    summary += f"Profit/Loss: ${profit_loss:.2f} "
    
    if profit_loss > 0:
        summary += "📈"
    elif profit_loss < 0:
        summary += "📉"
    
    return summary

def get_portfolio():
    global account
    if account is None:
        return "❌ Error: Please create an account first"
    
    if not account.portfolio:
        return "No stocks in portfolio."
    
    portfolio = "Current Holdings:\n"
    for symbol, quantity in account.portfolio.items():
        price = get_share_price(symbol)
        value = price * quantity
        portfolio += f"{symbol}: {quantity} shares @ ${price:.2f} = ${value:.2f}\n"
    
    return portfolio

def get_transaction_history():
    global account
    if account is None:
        return "❌ Error: Please create an account first"
    
    if not account.transactions:
        return "No transactions recorded."
    
    history = "Transaction History:\n"
    for idx, (transaction_type, symbol, quantity, price) in enumerate(account.transactions, 1):
        if transaction_type == "DEPOSIT":
            history += f"{idx}. DEPOSIT: ${price:.2f}\n"
        elif transaction_type == "WITHDRAW":
            history += f"{idx}. WITHDRAW: ${price:.2f}\n"
        elif transaction_type == "BUY":
            history += f"{idx}. BUY: {quantity} shares of {symbol} @ ${price:.2f} = ${quantity * price:.2f}\n"
        elif transaction_type == "SELL":
            history += f"{idx}. SELL: {quantity} shares of {symbol} @ ${price:.2f} = ${quantity * price:.2f}\n"
    
    return history

def get_available_stocks():
    stocks = "Available Stocks for Demo:\n"
    stocks += "AAPL: $150.00\n"
    stocks += "TSLA: $800.00\n"
    stocks += "GOOGL: $2,500.00"
    return stocks

with gr.Blocks(title="Trading Simulation Platform") as demo:
    gr.Markdown("# Trading Simulation Platform")
    gr.Markdown("A simple demo of a trading account management system")
    
    with gr.Tab("Create Account"):
        with gr.Row():
            account_id_input = gr.Textbox(label="Account ID")
            initial_deposit_input = gr.Textbox(label="Initial Deposit ($)")
        create_account_btn = gr.Button("Create Account")
        create_account_output = gr.Textbox(label="Result", lines=2)
        
        create_account_btn.click(
            initialize_account,
            inputs=[account_id_input, initial_deposit_input],
            outputs=create_account_output
        )
    
    with gr.Tab("Deposit/Withdraw"):
        with gr.Row():
            with gr.Column():
                deposit_amount = gr.Textbox(label="Deposit Amount ($)")
                deposit_btn = gr.Button("Deposit")
                deposit_output = gr.Textbox(label="Result", lines=2)
            
            with gr.Column():
                withdraw_amount = gr.Textbox(label="Withdraw Amount ($)")
                withdraw_btn = gr.Button("Withdraw")
                withdraw_output = gr.Textbox(label="Result", lines=2)
        
        deposit_btn.click(
            deposit_funds,
            inputs=[deposit_amount],
            outputs=deposit_output
        )
        
        withdraw_btn.click(
            withdraw_funds,
            inputs=[withdraw_amount],
            outputs=withdraw_output
        )
    
    with gr.Tab("Trade Stocks"):
        stocks_info = gr.Textbox(value=get_available_stocks, label="Available Stocks", lines=4)
        
        with gr.Row():
            with gr.Column():
                buy_symbol = gr.Textbox(label="Stock Symbol (e.g., AAPL)")
                buy_quantity = gr.Textbox(label="Quantity")
                buy_btn = gr.Button("Buy Shares")
                buy_output = gr.Textbox(label="Result", lines=3)
            
            with gr.Column():
                sell_symbol = gr.Textbox(label="Stock Symbol (e.g., AAPL)")
                sell_quantity = gr.Textbox(label="Quantity")
                sell_btn = gr.Button("Sell Shares")
                sell_output = gr.Textbox(label="Result", lines=3)
        
        buy_btn.click(
            buy_stock,
            inputs=[buy_symbol, buy_quantity],
            outputs=buy_output
        )
        
        sell_btn.click(
            sell_stock,
            inputs=[sell_symbol, sell_quantity],
            outputs=sell_output
        )
    
    with gr.Tab("Account Information"):
        refresh_btn = gr.Button("Refresh Account Information")
        
        with gr.Row():
            with gr.Column():
                account_summary = gr.Textbox(label="Account Summary", lines=7)
            
            with gr.Column():
                holdings = gr.Textbox(label="Current Holdings", lines=7)
        
        transactions = gr.Textbox(label="Transaction History", lines=10)
        
        refresh_btn.click(
            lambda: [get_account_summary(), get_portfolio(), get_transaction_history()],
            inputs=None,
            outputs=[account_summary, holdings, transactions]
        )

if __name__ == "__main__":
    demo.launch()