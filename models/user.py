from dataclasses import dataclass
from typing import List
import random
from hash_utils import my_hash


@dataclass
class User:
    name: str
    public_key: str
    balance: int

    def debit(self, amount: int) -> None:
        self.balance -= amount

    def credit(self, amount: int) -> None:
        self.balance += amount

    def __repr__(self) -> str:
        return f"User(name={self.name}, key={self.public_key[:8]}..., balance={self.balance})"


def generate_users(n: int = 1000, min_balance: int = 100, max_balance: int = 1_000_000) -> List[User]:
    users: List[User] = []
    for i in range(n):
        name = f"user_{i:04d}"
        public_key = my_hash(f"pk::{name}")
        balance = random.randint(min_balance, max_balance)
        users.append(User(name=name, public_key=public_key, balance=balance))
    return users
