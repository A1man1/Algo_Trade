import Portfolio
import Order
import Alog_Trade.Boilerplates.Transaction as Transaction
from dataclasses import dataclass

@dataclass
class Strategy:
    """
    This class represents a trading strategy.

    Attributes:
        name (str): The name of the strategy.
        portfolio (Portfolio): Reference to the portfolio object.
        order (Order): Reference to the Order object for order execution.
        lookback (int): Number of data points used to calculate the mean price.
        transactions (list): List of Transaction objects for each trade.

    Methods:
        execute(self, market_data):
            This method implements a mean reversion trading strategy and tracks profits.

        get_historical_data(self, symbol, lookback):
            Replace this with your actual implementation to fetch historical data.
    """

    name: str
    portfolio: Portfolio
    order: Order
    lookback: int = 20
    transactions: list = None
    symbol: str
    
    def __init__(symbol, ):
        #symbol, stock to test
        pass


    def __post_init__(self):
        """
        Initialize transactions list if not provided.
        """
        if self.transactions is None:
            self.transactions = []

    def execute(self, market_data: dict):
        """
        This method implements a mean reversion trading strategy and tracks profits.

        Args:
            market_data (dict): Dictionary containing market data for the symbol.
                - symbol (str): Symbol of the security.
                - price (float): Current market price.
                - (optional) other relevant data points (e.g., historical prices).
        """

        symbol = self.symbol
        current_price = market_data["price"] # From Data Class
        # ... (rest of the mean reversion strategy logic from previous example)

        # Track transaction details if a trade is executed
        if self.order.order_history:
            last_order = self.order.order_history[-1]
            if last_order["order_type"] == "buy":
                self.transactions.append(Transaction(
                    symbol=symbol, quantity=last_order["quantity"], buy_price=current_price,
                    transaction_cost=self.get_transaction_cost(last_order["quantity"])
                ))
            elif last_order["order_type"] == "sell":
                # Assuming you have a way to retrieve the buy price for the sold shares (from portfolio or transaction history)
                buy_price = self.get_buy_price(symbol, last_order["quantity"])
                self.transactions.append(Transaction(
                    symbol=symbol, quantity=last_order["quantity"], buy_price=buy_price,
                    sell_price=current_price, transaction_cost=self.get_transaction_cost(last_order["quantity"])
                ))

    def get_transaction_cost(self, quantity: int, brokage = 0.03) -> float:
        """
        Calculate transaction cost based on quantity.

        Args:
            quantity (int): Quantity of shares.

        Returns:
            float: Transaction cost.
        """
        # Replace with your logic to calculate transaction cost based on quantity
        # (e.g., commission per share or fixed fee)
        return quantity * brokage  # Example: $0.01 per share

    def get_buy_price(self, symbol: str, quantity: int) -> float:
        """
        Retrieve the buy price for the sold shares.

        Args:
            symbol (str): Symbol of the security.
            quantity (int): Quantity of shares.

        Returns:
            float: Buy price of the sold shares.
        """
        # Replace with your logic to retrieve the buy price for the sold shares
        # (e.g., from portfolio or transaction history)
        # This example assumes FIFO (First-In-First-Out) accounting for simplicity
        # You might need more sophisticated logic for other accounting methods
        total_bought = 0
        average_buy_price = None
        for transaction in self.transactions:
            if transaction.symbol == symbol and transaction.buy_price:
                total_bought += transaction.quantity
                if total_bought >= quantity:
                    average_buy_price = sum(t.buy_price * t.quantity for t in self.transactions if
                                            t.symbol == symbol and t.buy_price) / total_bought
                    break
        return average_buy_price  # FIFO buy price or None if not enough shares bought