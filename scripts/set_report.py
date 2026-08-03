"""
Copiaza un fisier de raport nou peste data/raw/Report_JUL.xlsx,
locul si numele exact pe care le asteapta restul codului
(config/settings.py -> REPORT_FILE).

Utilizare:
    python scripts/set_report.py "C:\\cale\\catre\\Repot_AUG (3).xlsx"
"""

import shutil
import sys
from pathlib import Path

# Adaugam radacina proiectului in sys.path, ca sa mearga importul
# de mai jos indiferent din ce folder e rulat scriptul.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import REPORT_FILE


def main():
    if len(sys.argv) != 2:
        print("Utilizare: python scripts/set_report.py <cale_catre_fisierul_nou.xlsx>")
        sys.exit(1)

    source = Path(sys.argv[1])

    if not source.exists():
        print(f"Fisierul nu exista: {source}")
        sys.exit(1)

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(source, REPORT_FILE)

    print(f"Copiat:")
    print(f"  din: {source}")
    print(f"  in:  {REPORT_FILE}")
    print()
    print("Poti rula acum: streamlit run app.py")


if __name__ == "__main__":
    main()
