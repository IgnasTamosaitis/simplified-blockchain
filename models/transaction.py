"""
Transaction klasė reprezentuoja lėšų pervedimą tarp dviejų adresų.

Laukai:
- sender_key: siuntėjo public_key
- receiver_key: gavėjo public_key
- amount: kiek pinigų siunčiama
- timestamp: kada transakcija sukurta (epoch sekundėmis)
- tx_id: transakcijos identifikatorius (maišos reikšmė pagal kitus laukus)

transaction_id = hash(sender, receiver, amount, timestamp)
"""

import time
from hash_utils import my_hash


class Transaction:
    def __init__(self, sender_key: str, receiver_key: str, amount: int):
        self.sender_key = sender_key
        self.receiver_key = receiver_key
        self.amount = amount
        self.timestamp = time.time()

        self.tx_id = self.compute_id()

    def compute_id(self) -> str:
        base = f"{self.sender_key}|{self.receiver_key}|{self.amount}|{self.timestamp}"
        return my_hash(base)

    def __repr__(self):
        return (
            f"Transaction(id={self.tx_id[:10]}..., "
            f"{self.sender_key[:8]} -> {self.receiver_key[:8]}, "
            f"amount={self.amount})"
        )
