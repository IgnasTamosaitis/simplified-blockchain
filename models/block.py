from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, TYPE_CHECKING
import json
import time

from hash_utils import my_hash

if TYPE_CHECKING:
    # Tik tipu tikrinimui; importo ciklams isvengti
    from models.transaction import Transaction


def _json_canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def merkle_root_simple(tx_ids: List[str]) -> str:
    # Paprasta Merkle šaknis: hash'ina visų transakcijų ID sujungimą.
    if not tx_ids:
        return my_hash("")
    return my_hash("".join(tx_ids))


@dataclass
class BlockHeader:
    #Blocko antrastė (kad identifikuoti bloką ir patikrinti)
    prev_block_hash: str
    timestamp: int
    version: int
    merkle_root_hash: str
    nonce: int = 0
    difficulty_target: str = "000"  # PoW prefiksas

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Block:
    # Blokas grandinėje
    index: int  # Bloko numeris grandinėje
    header: BlockHeader  # Bloko antraštė
    transactions: List["Transaction"] = field(default_factory=list)

    @staticmethod
    def build(
        index: int,
        prev_block_hash: str,
        version: int,
        transactions: List["Transaction"],
        difficulty_target: str = "000",
        timestamp: int | None = None,
    ) -> "Block":
        tx_ids = [t.transaction_id for t in transactions]
        mr = merkle_root_simple(tx_ids)
        hdr = BlockHeader(
            prev_block_hash=prev_block_hash,
            timestamp=int(timestamp if timestamp is not None else time.time()),
            version=version,
            merkle_root_hash=mr,
            nonce=0,
            difficulty_target=difficulty_target,
        )
        return Block(index=index, header=hdr, transactions=transactions)

    def compute_hash(self) -> str:
        """
        Hash skaičiuojamas tik nuo bloko antraštės.
        Tai leidžia kasti (keisti nonce) nekeičant pačių transakcijų.
        """
        return my_hash(_json_canonical(self.header.to_dict()))

    def mine(self) -> str:
        """
        Didiname nonce tol, kol bloko hash prasideda nurodytu prefiksu.
        Kai randame tinkamą hash, jį grąžiname.
        """
        prefix = self.header.difficulty_target
        while True:
            h = self.compute_hash()
            if h.startswith(prefix):
                return h
            self.header.nonce += 1
