import json
import os
import requests
from typing import Dict, Any

INPUT_FILE = os.path.join("data", "master_input_3221.json")
OUTPUT_FILE = os.path.join("data", "census_output_3221.json")
CENSUS_API_URL = "https://api.census.gov/data/2022/acs/acs5"

# Konfiguracja słownika zmiennych ACS 2022 5-Year
# Te kody alfanumeryczne odpowiadają surowym zmiennym w API Censusu
ACS_VARIABLES = {
    "B25035_001E": "median_year_built",     # Mediana roku budowy struktury
    "B25077_001E": "median_home_value",     # Mediana wartości domu
    "B19013_001E": "median_income",         # Mediana dochodu gospodarstwa domowego
    "B25003_001E": "total_housing_units",   # Całkowita liczba lokali mieszkalnych
    "B25003_002E": "owner_occupied_units"   # Lokale mieszkaniowe zajmowane przez właściciela
}

def clean_census_value(val_str: str) -> Any:
    """
    Konwertuje tekstowe liczby na typy numeryczne Pythona.
    Census API stosuje ujemne wielkie liczby (np. -666666666) jako zamiennik braku danych (null).
    Ta funkcja chroni przed zanieczyszczeniem wyników poprzez rzutowanie ich na standardowe (None).
    """
    if val_str is None:
        return None
        
    try:
        f_val = float(val_str)
        # Census zwraca bardzo dziwne ujemne wartości dla "Brak Danych" / "N/A"
        if f_val < 0:
            return None
        
        # Jeśli liczba jest całkowita - zostawiamy ją jako prosty int
        if f_val.is_integer():
            return int(f_val)
            
        return f_val
    except ValueError:
        return None

def fetch_bulk_acs_data() -> list:
    """
    Pobiera dane demograficzne USA jednym zbiorczym strzałem 'Bulk'
    dla WSZYSTKICH stref ZCTA (Zip Code Tabulation Areas), omijając problem limitów 4544 zapytań.
    """
    # Konstrukcja stringu dla API: B25035_001E,B25077_001E,...
    variables_query = ",".join(ACS_VARIABLES.keys())
    
    # Parametry zgodne ze specyfikacją US Census API (ZCTA level)
    params = {
        "get": f"NAME,{variables_query}",
        "for": "zip code tabulation area:*"
    }
    
    print(f"🌍 [CENSUS API] Łączenie ze stacją bazową ({CENSUS_API_URL}) w trybie pracy masowej BULK (All ZCTAs)...")
    
    try:
        # Timeout wydłużony do 45 sekund, ponieważ paczka `ALL ZCTA` waży kilkanaście MB i wymaga przetrawienia przez serwer Rządu Północnoamerykańskiego.
        response = requests.get(CENSUS_API_URL, params=params, timeout=45)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ [CENSUS API] Sukces! Pobrane rekordy z rządu (Pełne terytorium ZCTA USA): {len(data) - 1}")
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ BŁĄD POBIERANIA: Błąd na poziomie połączenia z Census API: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ PARSER ERROR: Census uszkodzony lub zrezygnował z odpowiedzi JSON: {e}")
        return []

def transform_and_filter(raw_data: list, target_zips: set) -> Dict[str, Any]:
    """
    Odfiltrowuje 40+ tysięcy kodów pocztowych USA zostawiając jedynie 
    nasze ~4500 celów, formatując przy tym finalny output JSON.
    """
    if not raw_data:
        return {}
        
    # Pierwszy zrzut to lista kluczy (Headery kolumnowe)
    headers = raw_data[0]
    
    # Tworzymy dynamiczny mapownik indeksów kolumn, bo Census nie gwarantuje stałej kolejności
    col_idx_map = {}
    zip_idx = -1
    
    for i, col_name in enumerate(headers):
        if col_name in ACS_VARIABLES:
            col_idx_map[i] = ACS_VARIABLES[col_name]
        elif col_name == "zip code tabulation area" or col_name == "state":
            # Tabulation Area to nazwa zwrotna z Censusu kryjąca zip_code
            zip_idx = i

    if zip_idx == -1:
        print("❌ KRYTYCZNY BŁĄD: Nie odnaleziono kolumny strefy ZCTA w zwrocie Census API.")
        return {}

    final_output = {}
    matched_count = 0

    # Przesiewamy matrycę pomijając headery
    for row in raw_data[1:]:
        zip_code = str(row[zip_idx]).zfill(5) # Wymuszenie formatowania XXXXX (np. 01001)
        
        # Filtrowanie "The Matrix" -> interesują nas tylko nasze 4544 wektory.
        if zip_code not in target_zips:
            continue
            
        matched_count += 1
        city_metrics = {}
        
        total_units = None
        owner_units = None
        
        for i, var_name in col_idx_map.items():
            clean_val = clean_census_value(row[i])
            
            # Wektoryzacja przechowawcza do finalnej kalkulacji wskaźnika Ownership
            if var_name == "total_housing_units":
                total_units = clean_val
            elif var_name == "owner_occupied_units":
                owner_units = clean_val
            else:
                city_metrics[var_name] = clean_val
                
        # Obliczenie wymaganego Wskaźnika Własności (Owner-Occupied Rate) w procentach, formatowany do dziesiątych.
        if total_units and owner_units and total_units > 0:
            rate = (owner_units / total_units) * 100
            city_metrics["owner_occupied_rate"] = round(rate, 1)
        else:
            city_metrics["owner_occupied_rate"] = None
            
        final_output[zip_code] = city_metrics
        
    print(f"🔍 [MAPPER] Przefiltrowano USA. Złapanych na celowniku ZIP: {matched_count} / {len(target_zips)}")
    return final_output

def main():
    print(f"====== DEMOGRAFIA SPISU POWSzechnego (ACS 5-Year {CENSUS_API_URL.split('/')[-3]}) ======\n")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ KRYTYCZNY BŁĄD: Nie znaleziono bazy The Master JSON -> {INPUT_FILE}")
        return

    # 1. Wczytanie listy ~4500 docelowych Zip Code'ów, aby nie transformować zbędnych danych.
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        master_data = json.load(f)
        
    target_zips = set(master_data.keys())
    
    # 2. Strzał do bazy amerykańskiej
    raw_census_matrix = fetch_bulk_acs_data()
    
    # 3. Transformacja, translacja surowych intów i kalkulacja wskaźników
    final_census_dict = transform_and_filter(raw_census_matrix, target_zips)
    
    if not final_census_dict:
        print("❌ Wykryto PUSTY zrzut danych. Automatyczne przerwanie procedury (Fail-Safe) by nie nadpisać plików pustką.")
        return
        
    # 4. Zapis odseparowanego zrzutu danych badawczych
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_census_dict, f, indent=2, ensure_ascii=False)
        
    print(f"\n✅ ETL Ukończony! Złoty Zrzut (The Census Dummy) zeskładowany w: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
