import json
import os

DATA_DIR = "data"
MASTER_FILE = os.path.join(DATA_DIR, "master_input.json")
DROUGHT_FILE = os.path.join(DATA_DIR, "drought_output.json")
SOIL_FILE = os.path.join(DATA_DIR, "soil_output.json")
CENSUS_FILE = os.path.join(DATA_DIR, "census_output.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "final_enriched_database.json")

def load_json(filepath):
    """Pomocnicza funkcja do cichego ładowania JSON-ów z obsługą braków."""
    if not os.path.exists(filepath):
        print(f"⚠️ OSTRZEŻENIE: Brak pliku {filepath}. Pola zależne zostaną wypełnione jako 'null'.")
        return {}
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ BŁĄD PARSOWANIA: Plik {filepath} jest uszkodzony. Zwracam pusty słownik. ({e})")
        return {}

def calculate_labour_index(median_income):
    """
    Oblicza współczynnik robocizny 'labour_index' w ujęciu lokalnym
    na podstawie bazowej średniej USA na poziomie ~75,000 USD (index = 1.0).
    Zabezpieczone twardym clampingiem [0.85 - 2.50] dla rentowności projektu.
    """
    if median_income is None or median_income <= 0:
        return 1.00
        
    raw_index = median_income / 75000.0
    
    # Clamping (ograniczenia ekstremów zarobkowych)
    # 0.85 -> Zabezpiecza marżę i min. stawkę dla kontraktorów w najbiedniejszych strefach
    # 2.50 -> Ogranicza kosmicznie wysokie wyceny napraw w super-bogatych rejonach (Beverly Hills itp.)
    clamped_index = max(0.85, min(2.50, raw_index))
    
    # Ograniczenie i zwrot do 2 miejsc pod przecinku dla frontendu Astro
    return float(round(clamped_index, 2))

def main():
    print("====== AGLOMERACJA BAZY (MERGE PIPELINE) ======\n")
    
    # 1. Ładowanie kręgosłupa bazy danych w pamięć (In-Memory Processing)
    master_data = load_json(MASTER_FILE)
    if not master_data:
        print(f"❌ KRYTYCZNY BŁĄD: Kręgosłup The Master JSON ({MASTER_FILE}) jest pusty lub nie istnieje.")
        return

    # 2. Ładowanie odseparowanych paczek tematycznych
    print("⏳ Ładowanie satelitarnych plików JSON z danymi badawczymi do pamięci RAM...")
    drought_data = load_json(DROUGHT_FILE)
    soil_data = load_json(SOIL_FILE)
    census_data = load_json(CENSUS_FILE)

    merged_count = 0
    errors_count = 0

    print(f"🔄 Rozpoczęcie iteracyjnego wstrzykiwania parametrów dla {len(master_data)} stref...\n")

    # 3. Główna pętla wstrzykująca (Merge Logic)
    for zip_code, master_info in master_data.items():
        try:
            # Pobieranie bloków dla konkretnego ZIPa
            d_info = drought_data.get(zip_code, {})
            s_info = soil_data.get(zip_code, {})
            c_info = census_data.get(zip_code, {})
            
            # Wstrzykiwanie danych KLIMATYCZNYCH (Susza - zjawisko D0-D4)
            master_info["drought_status"] = d_info.get("drought_status", None)
            
            # Wstrzykiwanie danych GEO-TECHNICZNYCH (Glina / Kurczenie - Skala USDA 0-100)
            master_info["usda_soil_index"] = s_info.get("usda_soil_index", None)
            
            # Wstrzykiwanie danych DEMOGRAFICZNYCH Z CENSUSU (American Community Survey)
            master_info["median_year_built"] = c_info.get("median_year_built", None)
            master_info["median_home_value"] = c_info.get("median_home_value", None)
            master_info["owner_occupied_rate"] = c_info.get("owner_occupied_rate", None)
            
            m_income = c_info.get("median_income", None)
            master_info["median_income"] = m_income
            
            # DYNAMICZNA WARIACJA ZAROBKOWA (Labour Index)
            master_info["labour_index"] = calculate_labour_index(m_income)
            
            merged_count += 1
            
        except Exception as e:
            print(f"    [!] Wewnętrzny wyjątek na ZIP={zip_code}: {e}")
            errors_count += 1

    # 4. Zapisywanie pięknej finalnej bazy danych gotowej pod Payload Systemu
    print(f"💾 Zapisywanie złączonej bazy danych do {OUTPUT_FILE} (Indent=2)...")
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file_out:
        json.dump(master_data, file_out, indent=2, ensure_ascii=False)

    # 5. Podsumowanie raportu
    print(f"\n✅ ETL MERGE UKOŃCZONY BŁYSKAWICZNIE Z SUKCESEM!")
    print(f"🎯 Przemielono całkowicie: {merged_count} miast / kodów pocztowych USA.")
    if errors_count > 0:
        print(f"⚠️ Wystąpiły problemy i pominięto {errors_count} kodów pocztowych.")
    print(f"📍 Końcowa paczka złotych danych spoczywa w: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
