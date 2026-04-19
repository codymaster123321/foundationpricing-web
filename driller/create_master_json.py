import json
import os

# Kompletny słownik 50 stanów USA + D.C.
STATE_MAPPING = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
    "DC": "District of Columbia",
    "PR": "Puerto Rico", "GU": "Guam", "VI": "Virgin Islands", "AS": "American Samoa", "MP": "Northern Mariana Islands"
}

def format_county(county_name: str, state_abbr: str) -> str:
    """
    Formatuje nazwę hrabstwa (County/Parish/Borough).
    Zabezpiecza przed podwójnym dopisaniem przyrostka.
    """
    if not county_name:
        return county_name
    
    county_name = county_name.strip()
    lower_county = county_name.lower()
    
    # Krok 1: Sprawdzamy czy przyrostek już przypadkiem nie istnieje w zmiennej
    if lower_county.endswith(" county") or lower_county.endswith(" parish") or lower_county.endswith(" borough") or lower_county.endswith(" municipio"):
        return county_name
        
    # Krok 2: Doklejamy odpowiedni przyrostek zależnie od stanu
    if state_abbr == "LA":
        return f"{county_name} Parish"
    elif state_abbr == "AK":
        return f"{county_name} Borough"
    elif state_abbr == "PR":
        return f"{county_name} Municipio"
    else:
        return f"{county_name} County"

def main():
    # Definiowanie ścieżek (relatywne względem uruchomienia wewnątrz folderu driller)
    input_filepath = os.path.join("data", "new_targets_only.json")
    output_filepath = os.path.join("data", "master_input_3221.json")
    
    # 1. Obsługa błędów / Weryfikacja pliku wejściowego
    if not os.path.exists(input_filepath):
        print(f"❌ BŁĄD: Nie znaleziono pliku wejściowego pod ścieżką: {input_filepath}")
        return
        
    try:
        with open(input_filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ BŁĄD PARSOWANIA: Niepoprawny format JSON w {input_filepath}. Szczegóły: {e}")
        return
        
    if not isinstance(raw_data, list):
        print(f"❌ BŁĄD TYPÓW: Oczekiwano tablicy JSON, otrzymano: {type(raw_data).__name__}.")
        return

    # Inicjalizacja docelowego słownika
    master_dict = {}
    processed_count = 0
    
    print("Rozpoczynam transformację bazy miast...")
    
    # 2. Transformacja i mapowanie
    for item in raw_data:
        zip_code = str(item.get("zip", ""))
        
        # Jeśli brakuje kodu ZIP, pomijamy dany rekord
        if not zip_code:
            continue
            
        city = item.get("city")
        state_abbr = item.get("state")
        county = item.get("county")
        lat = item.get("lat")
        lng = item.get("lng")
        population = item.get("population")
        
        # Logika uzupełniająca (Reguła 2, 3)
        state_full = STATE_MAPPING.get(state_abbr, state_abbr)
        county_formatted = format_county(county, state_abbr)
        
        # Budowa struktury docelowej
        master_dict[zip_code] = {
            "city": city,
            "state_abbr": state_abbr,
            "state_full": state_full,
            "county": county_formatted,
            "lat": lat,
            "lng": lng,
            "population": population,
            "usda_soil_index": None, # Zostanie przekonwertowane na null w pliku JSON
            "drought_status": None,
            "labour": None,
            "median_year_built": None
        }
        processed_count += 1

    # Zabezpieczenie katalogu docelowego (jeśli nie istnieje)
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    
    # 3. Zapis do głównego pliku ze wcięciem 2 (indent=2)
    try:
        with open(output_filepath, "w", encoding="utf-8") as f:
            json.dump(master_dict, f, indent=2, ensure_ascii=False)
        print(f"✅ SUKCES! Przetransformowano {processed_count} unikalnych rekordów ZIP.")
        print(f"✅ Baza The Master JSON została wyeksportowana do: {output_filepath}")
    except Exception as e:
        print(f"❌ BŁĄD ZAPISU: Wystąpił błąd podczas zapisywania pliku wynikowego: {e}")

if __name__ == "__main__":
    main()
