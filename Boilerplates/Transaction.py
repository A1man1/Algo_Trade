from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel



class Transaction(BaseModel):
    """
    This class represents a stock transaction (buy or sell).

    Attributes:
        symbol (str): Symbol of the security.
        quantity (int): Quantity of shares bought or sold.
        buy_price (float): Price at which the stock was bought (or None for sell transactions).
        sell_price (float): Price at which the stock was sold (or None for buy transactions).
        transaction_cost (float): Per-share transaction cost (e.g., commission).
        tax_rate (float): Tax rate applied to the transaction (optional).

    Methods:
        get_profit(self):
            Calculate the profit from the transaction.
    """

    symbol: str
    quantity: int
    buy_price: Optional[float] = None
    sell_price: Optional[float] = None
    transaction_cost: float = 0.0
    tax_rate: float = 0.0

    def get_profit(self) -> float:
        """
        Calculate the profit from the transaction.

        Returns:
            float: The profit or loss from the transaction.
        """
        if self.buy_price is None or self.sell_price is None:
            return 0.0  # Cannot calculate profit without buy and sell prices

        total_cost = self.buy_price * self.quantity + self.transaction_cost * self.quantity
        total_proceeds = self.sell_price * self.quantity

        profit = total_proceeds - total_cost

        # Apply tax on the profit (if applicable)
        profit_after_tax = profit * (1 - self.tax_rate)

        return profit_after_tax