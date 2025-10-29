# Supaprastinta blokų grandinės simuliacija

## Aprašymas
Šis projektas įgyvendina supaprastintą **blokų grandinės (Blockchain)** modelį, skirtą edukaciniams ir analizės tikslams. Sistema imituoja vartotojų kūrimą, transakcijų generavimą, blokų formavimą bei jų kasimą naudojant **Proof-of-Work (PoW)** algoritmą.

Kiekvienas blokas yra susietas su ankstesniu per kriptografinį hash, užtikrinant grandinės vientisumą. Po iškasimo atnaujinami vartotojų balansai, o transakcijos pašalinamos iš laukiančių sąrašo.

## Funkcionalumas
- Atsitiktinių vartotojų generavimas su pradiniais balansais  
- Transakcijų kūrimas tarp vartotojų  
- Transakcijų grupavimas į blokus (pvz., po 100)  
- Proof-of-Work kasimo algoritmas, kol bloko hash atitinka nustatytą `difficulty_target`  
- Iškastų blokų saugojimas grandinėje  
- Balansų ir laukiančių transakcijų atnaujinimas po kiekvieno bloko iškasimo  
- Sistemos darbo eigos matavimas (laikas, transakcijų kiekis ir kt.)

## Naudojimas
1. Įsitikinkite, kad sistemoje įdiegtas **Python 3.8+**  
2. Atsisiųskite projektą ir atidarykite jį terminale  
3. Paleiskite pagrindinį failą:
   ```bash
   python main.py