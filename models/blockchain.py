"""
Blockchain modelis su pagrindinėmis funkcijomis:
- vartotojų generavimas (1000 userių)
- transakcijų generavimas (~10_000)
- blokų formavimas iš po 100 transakcijų
- Proof-of-Work kasimas (hash turi prasidėti '000')
- balansų atnaujinimas, kai blokas patvirtintas
- blokų grandinės palaikymas (chain)

Tai atitinka v0.1 reikalavimus:
- Centralizuota grandinė (vienas "miner")
- Yra PoW su nonce paieška
- Yra grandinės istorija
- Viskas loguojama į konsolę
"""

import time
import random
import uuid
from typing import List, Dict

from hash_utils import my_hash
from models.user import User
from models.transaction import Transaction
from models.block import Block, BlockHeader


class Blockchain:
    def __init__(self, difficulty_target: str = "000"):
        self.users: Dict[str, User] = {}
        self.pending_transactions: List[Transaction] = []
        self.chain: List[Block] = []

        self.version = "v0.1"
        self.difficulty_target = difficulty_target  # pvz. '000'

        self._create_genesis_block()

    def _create_genesis_block(self):
        print("[INIT] Kuriamas genesis blokas...")

        genesis_header = BlockHeader(
            prev_hash="0" * 64,
            version=self.version,
            merkle_root="GENESIS",
            difficulty_target=self.difficulty_target
        )

        genesis_block = Block(genesis_header, [])
        self.chain.append(genesis_block)

        print("[OK] Genesis blokas sukurtas.")
        print(f"     Hash: {genesis_block.block_hash()}\n")

    # ---------------------------
    # DUOMENŲ GENERAVIMAS
    # ---------------------------

    def generate_users(self, n: int = 1000):
        print(f"[INFO] Generuojami {n} vartotojai...")

        for _ in range(n):
            name = f"User_{uuid.uuid4().hex[:6]}"
            public_key = uuid.uuid4().hex
            balance = random.randint(100, 1_000_000)

            self.users[public_key] = User(
                name=name,
                public_key=public_key,
                balance=balance
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
                amount=amount
            )
            self.pending_transactions.append(tx)

        print(f"[OK] Sugeneruota {len(self.pending_transactions)} transakcijų.\n")

    # ---------------------------
    # BLOKO FORMAVIMAS
    # ---------------------------

    def pick_transactions_for_block(self, k: int = 100) -> List[Transaction]:
        txs = self.pending_transactions[:k]
        return txs

    def build_merkle_root_v0_1(self, txs: List[Transaction]) -> str:
        if not txs:
            return "NO_TX"

        all_ids = "|".join(tx.tx_id for tx in txs)
        return my_hash(all_ids)

    # ---------------------------
    # PROOF OF WORK / KASYBA
    # ---------------------------

    def mine_block(self, txs: List[Transaction]) -> Block:
        prev_hash = self.chain[-1].block_hash()
        merkle_root = self.build_merkle_root_v0_1(txs)

        header = BlockHeader(
            prev_hash=prev_hash,
            version=self.version,
            merkle_root=merkle_root,
            difficulty_target=self.difficulty_target
        )

        prefix = self.difficulty_target
        attempts = 0

        print("[MINING] Pradedamas kasimas naujam blokui...")
        print(f"         Ankstesnio bloko hash: {prev_hash[:16]}...")
        print(f"         Transakcijų kiekis:     {len(txs)}")
        print(f"         Tikslas: hash prasideda '{prefix}'\n")

        while True:
            attempts += 1
            current_hash = my_hash(header.header_string())

            if current_hash.startswith(prefix):
                print(f"[FOUND] Proof-of-Work rastas!")
                print(f"        nonce = {header.nonce}")
                print(f"        hash  = {current_hash}\n")
                break

            header.nonce += 1

            if attempts % 100000 == 0:
                print(f"[MINING] Bandymų: {attempts}, nonce={header.nonce}")

        new_block = Block(header, txs)
        return new_block

    # ---------------------------
    # STATE UPDATE (po bloko)
    # ---------------------------

    def apply_block_state_changes(self, block: Block):
        for tx in block.transactions:
            sender_user = self.users[tx.sender_key]
            receiver_user = self.users[tx.receiver_key]

            sender_user.debit(tx.amount)
            receiver_user.credit(tx.amount)

        used_ids = {tx.tx_id for tx in block.transactions}
        self.pending_transactions = [
            t for t in self.pending_transactions if t.tx_id not in used_ids
        ]

    def add_block(self, block: Block):
        self.chain.append(block)

    # ---------------------------
    # VISAS CIKLAS
    # ---------------------------

    def mine_until_done(self, block_tx_count: int = 100):
        block_index = 1  # nes 0 yra genesis blokas

        while len(self.pending_transactions) > 0:
            print("=" * 60)
            print(f"[INFO] Kasamas blokas #{block_index}")
            print(f"[INFO] Grandinės ilgis dabar: {len(self.chain)} blokai (-as)")
            print(f"[INFO] Liko neapdorotų transakcijų: {len(self.pending_transactions)}\n")

            txs_for_block = self.pick_transactions_for_block(block_tx_count)

            if not txs_for_block:
                print("[INFO] Nebėra transakcijų blokui -> stabdom.")
                break

            new_block = self.mine_block(txs_for_block)

            self.apply_block_state_changes(new_block)
            self.add_block(new_block)

            print(f"[CHAIN] Naujas blokas #{block_index} įtrauktas.")
            print(f"[CHAIN] Naujo bloko hash: {new_block.block_hash()}")
            print(f"[CHAIN] Nonce: {new_block.header.nonce}")
            print(f"[CHAIN] Grandinės ilgis: {len(self.chain)}")
            print(f"[CHAIN] Liko transakcijų eilėje: {len(self.pending_transactions)}\n")

            block_index += 1

        print("=== Viskas baigta ===")
        print(f"Galutinis blokų kiekis: {len(self.chain)}")
        print(f"Vartotojų kiekis:       {len(self.users)}")
        print(f"Paskutinio bloko hash:  {self.chain[-1].block_hash()[:32]}...")
        print("======================\n")

    # ---------------------------
    # Pagalbinė metrika pabaigai
    # ---------------------------

    def summary(self) -> str:
        return (
            f"Grandinės ilgis: {len(self.chain)} blokai\n"
            f"Vartotojų kiekis: {len(self.users)}\n"
            f"Laukiančių transakcijų: {len(self.pending_transactions)}\n"
            f"Paskutinio bloko hash: {self.chain[-1].block_hash()}\n"
        )
