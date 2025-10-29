import random
import time
import uuid
from typing import List, Dict

from hash_utils import my_hash
from models.user import User
from models.transaction import Transaction
from models.block import Block


class Blockchain:
    def __init__(self, difficulty_target: str = "000"):
        self.users: Dict[str, User] = {}
        self.pending_transactions: List[Transaction] = []
        self.chain: List[Block] = []

        self.version = 1
        self.difficulty_target = difficulty_target

        self._create_genesis_block()

    def _create_genesis_block(self) -> None:
        print("[INIT] Kuriamas GENESIS blokas...")

        genesis_block = Block.build(
            index=0,
            prev_block_hash="0" * 64,
            version=self.version,
            transactions=[],
            difficulty_target=self.difficulty_target,
            timestamp=int(time.time()),
        )
        
        _ = genesis_block.mine()

        self.chain.append(genesis_block)

        print("[OK] Genesis blokas paruoštas.")
        print(f"     Hash: {genesis_block.get_hash()}")
        print(f"     Nonce: {genesis_block.header.nonce}\n")


    def generate_users(self, n: int = 1000):
        print(f"[INFO] Generuojami {n} vartotojai...")

        for _ in range(n):
            name = f"User_{uuid.uuid4().hex[:6]}"
            public_key = uuid.uuid4().hex
            balance = random.randint(100, 1_000_000)

            self.users[public_key] = User(
                name=name,
                public_key=public_key,
                balance=balance,
            )

        print(f"[OK] Sugeneruota {len(self.users)} vartotojų.\n")

    def generate_transactions(self, m: int = 10000):
        print(f"[INFO] Generuojamos {m} transakcijos...")

        keys = list(self.users.keys())
        for _ in range(m):
            sender_key, receiver_key = random.sample(keys, 2)
            amount = random.randint(1, 5000)

            tx = Transaction(
                sender_key=sender_key,
                receiver_key=receiver_key,
                amount=amount,
            )

            self.pending_transactions.append(tx)

        print(f"[OK] Sugeneruota {len(self.pending_transactions)} transakcijų.\n")




    def pick_transactions_for_block(self, k: int = 100) -> List[Transaction]:
        return self.pending_transactions[:k]




    def mine_block_from_transactions(self, txs: List[Transaction]) -> Block:
        prev_block_hash = self.chain[-1].get_hash()

        block = Block.build(
            index=len(self.chain),
            prev_block_hash=prev_block_hash,
            version=self.version,
            transactions=txs,
            difficulty_target=self.difficulty_target,
        )

        print("[MINING] Pradedamas kasimas naujam blokui...")
        print(f"         Bloko indeksas:        {block.index}")
        print(f"         Ankstesnio bloko hash: {prev_block_hash[:16]}...")
        print(f"         Transakcijų kiekis:    {len(txs)}")
        print(f"         Tikslas: hash prasideda '{block.header.difficulty_target}'\n")

        start = time.time()
        mined_hash = block.mine()
        end = time.time()

        print("[FOUND] Blokas iškastas!")
        print(f"        Hash         = {mined_hash}")
        print(f"        Nonce        = {block.header.nonce}")
        print(f"        Difficulty   = {block.header.difficulty_target}")
        print(f"        Kasybos laikas = {end - start:.4f} s\n")

        return block




    def apply_block_state_changes(self, block: Block) -> None:
        for tx in block.transactions:
            sender = self.users[tx.sender_key]
            receiver = self.users[tx.receiver_key]
            sender.debit(tx.amount)
            receiver.credit(tx.amount)

        used_ids = {t.tx_id for t in block.transactions}
        self.pending_transactions = [
            t for t in self.pending_transactions if t.tx_id not in used_ids
        ]

    def add_block_to_chain(self, block: Block) -> None:
        self.chain.append(block)





    def mine_until_done(self, block_tx_count: int = 100):

        while len(self.pending_transactions) > 0:
            print("=" * 60)
            print(f"[INFO] Grandinės ilgis dabar: {len(self.chain)} blokai (-as)")
            print(f"[INFO] Liko neapdorotų transakcijų: {len(self.pending_transactions)}\n")

            tx_batch = self.pick_transactions_for_block(block_tx_count)
            if not tx_batch:
                print("[INFO] Nebėra transakcijų blokui -> stabdom.")
                break

            new_block = self.mine_block_from_transactions(tx_batch)

            self.apply_block_state_changes(new_block)

            self.add_block_to_chain(new_block)

            print(f"[CHAIN] Naujas blokas #{new_block.index} įtrauktas į grandinę.")
            print(f"[CHAIN] Bloko hash: {new_block.get_hash()}")
            print(f"[CHAIN] Likusios neįtrauktos transakcijos: {len(self.pending_transactions)}\n")

        print("=== Viskas baigta ===")
        print(f"Galutinis blokų kiekis: {len(self.chain)}")
        print(f"Vartotojų kiekis:       {len(self.users)}")
        print(f"Paskutinio bloko hash:  {self.chain[-1].get_hash()[:32]}...")
        print("======================\n")

    def summary(self) -> str:
        return (
            f"Grandinės ilgis: {len(self.chain)} blokai\n"
            f"Vartotojų kiekis: {len(self.users)}\n"
            f"Laukiančių transakcijų: {len(self.pending_transactions)}\n"
            f"Paskutinio bloko hash: {self.chain[-1].get_hash()}\n"
        )