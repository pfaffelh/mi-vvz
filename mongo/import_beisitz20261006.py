# Import der Beisitze 2026 aus der Excel-Datei des Dekanats
# ("00_Beisitz 2026 fuer Peter_korr..xlsx", Blatt "Beisitz ab Jan26").
#
# Die drei Zahlenspalten werden zu je einem Eintrag in person.beisitz mit einem
# Stichtag als Datum (siehe SPALTEN). Eintraege mit Anzahl 0 werden weggelassen.
# Das Feld beisitz wird bei allen Personen aus der Datei ersetzt (nicht ergaenzt).
# Ausgeblendete Zeilen der Datei sind vom Dekanat bewusst herausgenommen und
# werden uebersprungen.
#
# Aufruf (Trockenlauf): python3 mongo/import_beisitz20261006.py <datei.xlsx>
# Aufruf (schreibend):  python3 mongo/import_beisitz20261006.py <datei.xlsx> --schreiben

import sys
import json
import unicodedata
from datetime import datetime

import openpyxl
from pymongo import MongoClient

# Spaltenindex (0-basiert) -> Stichtag des Eintrags
SPALTEN = {
    8: datetime(2026, 9, 15),    # "Anzahl Jun-Dez": Mitte des Zeitraums Jun-Dez 2026
    9: datetime(2026, 3, 31),    # "mueP LA/ANA (April/Maerz)"
    10: datetime(2026, 9, 30),   # "mueP LA/ANA (Sept./Okt)"
}

# Schreibweisen in der Datei -> (name, vorname) in der Datenbank
NAMENSKORREKTUR = {
    ("Bartnick", "Charlotte"): ("Amann-Bartnick", "Charlotte"),
    ("Schreiber (geb. )Stiefken", "Tatjana"): ("Schreiber", "Tatjana"),
    ("Wang", "Boyan (w)"): ("Wang", "Bohan"),
}


def norm(s):
    s = (s or "").strip().lower().replace("ß", "ss")
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def zeilen_lesen(pfad):
    ws = openpyxl.load_workbook(pfad, data_only=True).active
    for nr, r in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not r[1]:
            continue
        if ws.row_dimensions[nr].hidden:
            yield nr, str(r[1]).strip(), str(r[2] or "").strip(), None
            continue
        name = str(r[1]).strip()
        vorname = str(r[2] or "").strip()
        eintraege = []
        for spalte, datum in SPALTEN.items():
            wert = r[spalte]
            if wert not in (None, "") and int(wert) > 0:
                eintraege.append({"datum": datum, "anzahl": int(wert)})
        eintraege.sort(key=lambda e: e["datum"], reverse=True)
        yield nr, name, vorname, eintraege


def person_finden(personen, name, vorname):
    name, vorname = NAMENSKORREKTUR.get((name, vorname), (name, vorname))
    treffer = [p for p in personen if norm(p.get("name")) == norm(name)]
    if len(treffer) > 1 and vorname:
        vn = norm(vorname).split()[0]
        enger = [p for p in treffer if norm(p.get("vorname")).startswith(vn)]
        if len(enger) == 1:
            treffer = enger
    return treffer


def main():
    if len(sys.argv) < 2:
        sys.exit(f"Aufruf: python3 {sys.argv[0]} <datei.xlsx> [--schreiben]")
    pfad = sys.argv[1]
    schreiben = "--schreiben" in sys.argv

    mongo_db = MongoClient("mongodb://127.0.0.1:27017")["vvz"]
    personen = list(mongo_db["person"].find({}, {"name": 1, "vorname": 1, "beisitz": 1}))

    aenderungen, probleme, uebersprungen = [], [], []
    for nr, name, vorname, eintraege in zeilen_lesen(pfad):
        if eintraege is None:
            uebersprungen.append((nr, name, vorname))
            continue
        summe = sum(e["anzahl"] for e in eintraege)
        treffer = person_finden(personen, name, vorname)
        if len(treffer) != 1:
            probleme.append((nr, name, vorname, summe,
                             [f"{p['name']}, {p.get('vorname')}" for p in treffer]))
            continue
        p = treffer[0]
        if p.get("beisitz", []) != eintraege:
            aenderungen.append((p, eintraege))

    for p, eintraege in aenderungen:
        alt = sum(e["anzahl"] for e in p.get("beisitz", []))
        neu = sum(e["anzahl"] for e in eintraege)
        details = ", ".join("{:%d.%m.%Y}: {}".format(e["datum"], e["anzahl"]) for e in eintraege)
        print(f"{p['name']}, {p.get('vorname')}: {alt} -> {neu} ({details or 'leer'})")

    if uebersprungen:
        print("\nUebersprungen (in der Datei ausgeblendet):")
        for nr, name, vorname in uebersprungen:
            print(f"  Zeile {nr}: {name}, {vorname}")
    if probleme:
        print("\nNicht eindeutig zuzuordnen:")
        for nr, name, vorname, summe, kand in probleme:
            print(f"  Zeile {nr}: {name}, {vorname} ({summe} Beisitze) - Kandidaten: {kand or 'keine'}")

    print(f"\n{len(aenderungen)} Personen zu aendern, {len(probleme)} Probleme, "
          f"{len(uebersprungen)} uebersprungen")

    if not schreiben:
        print("Trockenlauf - nichts geschrieben. Mit --schreiben ausfuehren.")
        return

    sicherung = f"/tmp/beisitz_vorher_{datetime.now():%Y%m%d-%H%M%S}.json"
    with open(sicherung, "w") as f:
        json.dump([{"_id": str(p["_id"]), "name": p["name"], "vorname": p.get("vorname"),
                    "beisitz": [{"datum": e["datum"].isoformat(), "anzahl": e["anzahl"]}
                                for e in p.get("beisitz", [])]}
                   for p, _ in aenderungen], f, indent=1, ensure_ascii=False)
    print(f"Vorheriger Stand gesichert in {sicherung}")

    print("Ab hier wird veraendert")
    for p, eintraege in aenderungen:
        mongo_db["person"].update_one({"_id": p["_id"]}, {"$set": {"beisitz": eintraege}})
    print(f"person: beisitz bei {len(aenderungen)} Dokumenten gesetzt")


if __name__ == "__main__":
    main()
