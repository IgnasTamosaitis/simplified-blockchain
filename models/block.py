from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, TYPE_CHECKING
import json
import time

from hash_utils import my_hash

if TYPE_CHECKING:
    # Tik tipų tikrinimui; kad išvengt import cycle runtime metu
    from models.transaction import Transaction


def _json_canonical(obj) -> str:
    """
    Paverčia dict'ą į deterministinį JSON (rūšiuoti raktai, nėra tarpų),
    kad hash rezultatas būtų stabilus.
    """
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def merkle_root_simple(tx_ids: List[str]) -> str:
    """
    Supaprastinta Merkle šaknis:
    tiesiog sujungiame visų transakcijų ID ir tą string'ą hashinam.
    Tai atitinka v0.1 reikalavimą ("galima daryti paprastą visų TX ID maišą").
    """
    if not tx_ids:
        return my_hash("")
    return my_hash("".join(tx_ids))


@dataclass
class BlockHeader:
    """
    Bloko antraštė: tai kas yra kasama (Proof-of-Work).
    """
    prev_block_hash: str
    timestamp: int
    version: int
    merkle_root_hash: str
    nonce: int = 0
    difficulty_target: str = "000"  # hash prefiksas, kurio ieškom

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Block:
    """
    Pilnas blokas grandinėje:
    - index: kelintas blokas grandinėje
    - header: BlockHeader (kasimo dalis)
    - transactions: transakcijų sąrašas
    """
    index: int
    header: BlockHeader
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
        tx_ids = [t.tx_id for t in transactions]  # tavo Transaction turi tx_id
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
        Skaičiuojam hash tik nuo bloko HEADER.
        Tai yra kasimo esmė: mes nekeičiam transakcijų, tik nonce.
        """
        header_json = _json_canonical(self.header.to_dict())
        return my_hash(header_json)

    def mine(self) -> str:
        """
        Proof-of-Work:
        keliame nonce, kol hash prasideda difficulty_target (pvz. '000').
        Grąžina rastą hash.
        """
        prefix = self.header.difficulty_target
        while True:
            h = self.compute_hash()
            if h.startswith(prefix):
                return h
            self.header.nonce += 1

    # --- helperiai, kad blockchain klasė galėtų su tavim kalbėt patogiai ---

    def get_hash(self) -> str:
        """
        Sugrąžina current hash (pagal dabartinį nonce).
        Naudinga kaip "bloko identitetas" grandinėje.
        """
        return self.compute_hash()

    def short_info(self) -> str:
        """
        Gražus trumpas atvaizdavimas logams / printams.
        """
        return (
            f"Block(index={self.index}, hash={self.get_hash()[:12]}..., "
            f"tx_count={len(self.transactions)}, nonce={self.header.nonce})"
        )