import json
import os

def main():
    filepath = os.path.join("data", "master_input.json")
    
    if not os.path.exists(filepath):
        print(f"❌ Plik {filepath} nie istnieje!")
        return
        
    print(f"Odczytywanie pliku: {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    total_objects = len(data)
    print(f"\n==========================================")
    print(f"📊 RAPORT WALIDACJI: The Master JSON")
    print(f"==========================================")
    print(f"Całkowita liczba rekordów (kodów ZIP): {total_objects}")
    
    expected_keys = {
        "city", "state_abbr", "state_full", "county", 
        "lat", "lng", "population", 
        "usda_soil_index", "drought_status", "labour", "median_year_built"
    }
    
    errors = {
        "missing_keys": 0,
        "invalid_nulls": 0,
        "invalid_coordinates": 0,
        "invalid_population": 0,
        "missing_county_suffix": 0
    }
    
    for zip_code, info in data.items():
        # 1. Sprawdzanie czy zestaw kluczy jest kompletny
        actual_keys = set(info.keys())
        if actual_keys != expected_keys:
            errors["missing_keys"] += 1
            
        # 2. Sprawdzanie czy puste klucze do API mają na pewno status `null`
        if info.get("usda_soil_index") is not None or \
           info.get("drought_status") is not None or \
           info.get("labour") is not None or \
           info.get("median_year_built") is not None:
            errors["invalid_nulls"] += 1
            
        # 3. Sprawdzanie czy współrzędne to na pewno liczby
        if not isinstance(info.get("lat"), (int, float)) or not isinstance(info.get("lng"), (int, float)):
            errors["invalid_coordinates"] += 1
            
        # 4. Sprawdzanie populacji
        if not isinstance(info.get("population"), (int, type(None))):
            errors["invalid_population"] += 1
            
        # 5. Sprawdzanie mapowań County (czy na pewno mają poprawny przyrostek)
        county = str(info.get("county", ""))
        if county and not (county.endswith(" County") or county.endswith(" Parish") or county.endswith(" Borough")):
            errors["missing_county_suffix"] += 1
            
    print(f"\n[ Wyniki testów integralności ]")
    if sum(errors.values()) == 0:
        print("✅ STRUKTURA IDEALNA! Baza nie posiada żadnych braków.")
        print("✅ Wszystkie klucze są na swoim miejscu.")
        print("✅ Wszystkie rezerwacje (null) pod zapytania API są prawidłowe.")
        print("✅ Plik jest perfekcyjnie przygotowany do dalszych zapytań u Rządu USA (The Driller ETL).")
    else:
        print("⚠️ ZNALEZIONO BŁĘDY (Wymagane poprawki):")
        print(f" - Rekordy z brakującymi/nadmiarowymi kluczami: {errors['missing_keys']}")
        print(f" - Rekordy, gdzie usda/drought/labour NIE SĄ 'null': {errors['invalid_nulls']}")
        print(f" - Rekordy z uszkodzonymi współrzędnymi geograficznymi: {errors['invalid_coordinates']}")
        print(f" - Rekordy z nieprawidłowym formatem populacji: {errors['invalid_population']}")
        print(f" - Rekordy hrabstw bez przyrostka County/Parish/Borough: {errors['missing_county_suffix']}")
        
    print(f"==========================================")

if __name__ == "__main__":
    main()
