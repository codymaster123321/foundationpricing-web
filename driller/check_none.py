import os

# Konfiguracja stałych (według zlecenia)
REPORTS_DIR = "raw_reports"
TARGET_STRINGS = ["None%", "none%", "%none", "%None"]
PREFIX = "XX_"

def main():
    print(f"Rozpoczynam przeszukiwanie folderu: {REPORTS_DIR}")
    print(f"Szukane warianty ciągu znaków wewnątrz plików: {TARGET_STRINGS}\n")
    
    if not os.path.exists(REPORTS_DIR):
        print(f"❌ BŁĄD: Folder z raportami nie istnieje pod ścieżką: {REPORTS_DIR}")
        return

    files_with_target = []
    all_files = os.listdir(REPORTS_DIR)
    
    # ----------------------------------------------------
    # Krok 1: Skanowanie treści każdego pliku w folderze
    # ----------------------------------------------------
    for filename in all_files:
        filepath = os.path.join(REPORTS_DIR, filename)
        
        # Omijanie katalogów (na wszelki wypadek)
        if not os.path.isfile(filepath):
            continue
            
        # Omijanie plików, które już dostały nasz przedrostek z poprzednich wywołań
        if filename.startswith(PREFIX):
            continue
            
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()
                if any(target in content for target in TARGET_STRINGS):
                    files_with_target.append(filename)
        except Exception as e:
            print(f"⚠️ Nie można odczytać pliku {filename}. Błąd: {e}")

    print(f"🔎 Analiza ukończona. Znaleziono {len(files_with_target)} plików zawierających halucynację AI (warianty none%).")

    # ----------------------------------------------------
    # Krok 2: Modyfikacja nazw plików
    # ----------------------------------------------------
    renamed_count = 0
    if files_with_target:
        for filename in files_with_target:
            old_path = os.path.join(REPORTS_DIR, filename)
            new_filename = f"{PREFIX}{filename}"
            new_path = os.path.join(REPORTS_DIR, new_filename)
            
            try:
                os.rename(old_path, new_path)
                renamed_count += 1
            except Exception as e:
                print(f"❌ BŁĄD podczas zmiany nazwy pliku {filename}: {e}")

    # ----------------------------------------------------
    # Krok 3: Double Check - Rygorystyczna Weryfikacja
    # ----------------------------------------------------
    verified_count = 0
    current_files_after_rename = os.listdir(REPORTS_DIR)
    
    # Sprawdzamy czy konkretne pliki, którym zmieniliśmy nazwę, faktycznie tam istnieją pod nową formą
    for old_filename in files_with_target:
        expected_new_filename = f"{PREFIX}{old_filename}"
        if expected_new_filename in current_files_after_rename:
            verified_count += 1

    # Podsumowanie
    print("-" * 50)
    print(f"\n--- ZESTAWIENIE THE NONE FIXER ---")
    print(f"🔄 Utworzono i pomyślnie zmieniono nazwę (dodano '{PREFIX}'): {renamed_count} plików.")
    print(f"✅ Double-check: Potwierdzono nową tożsamość dla {verified_count} plików w przestrzeni systemu plików.")

if __name__ == "__main__":
    main()
