import time
from models.blockchain import Blockchain

def main():
    start = time.time()

    print("===== Blockchain v0.1 demo start =====\n")

    bc = Blockchain(difficulty_target="000")
    bc.generate_users(n=50)          # gali sumažinti, kad greičiau skaičiuotų
    bc.generate_transactions(m=1000)  # irgi mažiau, kad spėtų persukti
    bc.mine_until_done(block_tx_count=100)

    print("===== SUMMARY =====")
    print(bc.summary())

    end = time.time()
    print(f"Bendras vykdymo laikas: {end - start:.2f} s")

    print("\n===== Blockchain =====")

if __name__ == "__main__":
    main()