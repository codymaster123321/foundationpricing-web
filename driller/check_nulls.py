import json
import os
from collections import defaultdict

FILE_PATH = os.path.join("data", "final_enriched_database.json")

def main():
    if not os.path.exists(FILE_PATH):
        print(f"❌ BŁĄD: Plik wyjściowy {FILE_PATH} nie istnieje.")
        return

    print("⏳ Wczytywanie bazy danych do testów integralności (Integrity Check)...")
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_records = len(data)
    
    # Przechowujemy statystyki osobno dla każdego unikalnego kręgosa w JSON
    keys_stats = defaultdict(lambda: {"null": 0, "zero": 0})

    for zip_code, info in data.items():
        for key, value in info.items():
            # Standardowy None (Null w formacie wyciągniętym do Pythona)
            if value is None:
                keys_stats[key]["null"] += 1
            # Rzepliwe API mogły na etapie ekstrakcji zapisać string "None" lub "null"
            elif isinstance(value, str) and value.strip().lower() in ["none", "null", "n/a", ""]:
                keys_stats[key]["null"] += 1
            # Liczenie matematycznego zera (chronimy się przed chwytaniem booleanowego False)
            elif (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool):
                if value == 0 or value == 0.0:
                    keys_stats[key]["zero"] += 1

    print(f"\n====== RAPORT BRAKÓW DANYCH (INTEGRITY SCAN) ======")
    print(f"Analizowany plik: {FILE_PATH}")
    print(f"Miasta/Zip Codes poddane ewaluacji: {total_records}\n")
    
    print(f"{'ZMIENNA / KLUCZ':<30} | {'WARTOŚCI NULL':<15} | {'WARTOŚCI ZERO':<15}")
    print("-" * 68)
    
    # Sortowanie alfabetyczne by zgrabnie posegregować
    for key in sorted(keys_stats.keys()):
        stats = keys_stats[key]
        null_count = stats["null"]
        zero_count = stats["zero"]
        
        # Ostrzegawcze wizualizacje terminalowe - Null jest zły (ale naturalny), Zero w wycenie domu to patologia
        null_str = f"{null_count}" if null_count == 0 else f"{null_count} ⚠️"
        zero_str = f"{zero_count}" if zero_count == 0 else f"{zero_count} ⛔"
        
        print(f"{key:<30} | {null_str:<15} | {zero_str:<15}")

    print("\n✅ Narzędzie detekcji strukturalnej zakończyło analizę The Master JSON.")

if __name__ == "__main__":
    main()
