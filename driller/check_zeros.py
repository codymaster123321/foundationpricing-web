import json
import os

# Konfiguracja stałych (według zlecenia)
FILE_PATH = os.path.join("data", "final_enriched_database.json")
REPORTS_DIR = "raw_reports"
TARGET_KEY = "usda_soil_index"
TARGET_VALUE = 0
PREFIX = "X_"

def rename_reports(zip_codes):
    """Przeszukuje folder raw_reports i dodaje prefix do plików zawierających podane kody ZIP."""
    if not os.path.exists(REPORTS_DIR):
        print(f"❌ BŁĄD: Folder z raportami nie istnieje pod ścieżką: {REPORTS_DIR}")
        return

    renamed_count = 0
    all_files = os.listdir(REPORTS_DIR)
    
    for filename in all_files:
        # Pomijamy pliki, które już zaczynają się od prefixu (zabezpieczenie przed podwójną zmianą nazwy)
        if filename.startswith(PREFIX):
            continue
            
        # Sprawdzamy czy którykolwiek ze znalezionych kodów ZIP znajduje się w nazwie pliku
        for zip_code in zip_codes:
            if zip_code in filename:
                old_path = os.path.join(REPORTS_DIR, filename)
                new_filename = f"{PREFIX}{filename}"
                new_path = os.path.join(REPORTS_DIR, new_filename)
                
                os.rename(old_path, new_path)
                renamed_count += 1
                break # Jeśli plik został przypisany i zmieniony, nie musimy dalej przeszukiwać kodów
                
    # Double check - weryfikacja ile plików z naszymi kodami ZIP ma teraz prefix w folderze
    verified_count = 0
    current_files_after_rename = os.listdir(REPORTS_DIR)
    
    for filename in current_files_after_rename:
        if filename.startswith(PREFIX):
            for zip_code in zip_codes:
                if zip_code in filename:
                    verified_count += 1
                    break

    print(f"\n--- Podsumowanie Zmiany Nazw ---")
    print(f"🔄 Zmieniono nazwę: {renamed_count} plików (dodano prefiks '{PREFIX}').")
    print(f"✅ Double-check (Weryfikacja): Znaleziono {verified_count} plików z docelowymi kodami ZIP posiadających prefiks '{PREFIX}'.")


def main():
    print(f"Rozpoczynam przeszukiwanie pliku: {FILE_PATH}")
    print(f"Szukany klucz: '{TARGET_KEY}' o wartości: {TARGET_VALUE}\n")
    
    if not os.path.exists(FILE_PATH):
        print(f"❌ BŁĄD: Nie znaleziono pliku pod ścieżką: {FILE_PATH}")
        return

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"❌ BŁĄD: Plik JSON jest uszkodzony. Szczegóły: {e}")
        return

    found_zips = []
    
    # Przeszukiwanie bazy danych w celu zebrania celów
    for zip_code, metrics in data.items():
        if TARGET_KEY in metrics and metrics[TARGET_KEY] == TARGET_VALUE:
            found_zips.append(zip_code)

    print("-" * 40)
    print(f"Znaleziono łącznie kodów z usda równe 0: {len(found_zips)}")
    
    # Wywołanie nowej funkcji jeśli znaleziono jakieś kody ZIP
    if found_zips:
        rename_reports(found_zips)
    else:
        print("Brak kodów do zmiany nazw plików.")

if __name__ == "__main__":
    main()
