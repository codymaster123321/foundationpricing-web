import json
import os
import time
import requests

INPUT_FILE = os.path.join("data", "master_input_3221.json")
OUTPUT_FILE = os.path.join("data", "drought_output_3221.json")
BASE_URL = "https://services9.arcgis.com/RHVPKKiFTONKtxq3/ArcGIS/rest/services/US_Drought_Intensity_v1/FeatureServer/2/query"

DM_MAP = {
    0: "D0-Abnormally Dry",
    1: "D1-Moderate",
    2: "D2-Severe",
    3: "D3-Extreme",
    4: "D4-Exceptional"
}

def get_drought_status(lat, lng):
    """Odpytuje API USDM o status suszy (ArcGIS REST) uzywajac wspolrzednych."""
    # Oczekiwany format do spatialRelIntersects: x,y (czyli lng,lat)
    params = {
        "where": "1=1",
        "geometry": f"{lng},{lat}",
        "geometryType": "esriGeometryPoint",
        "spatialRel": "esriSpatialRelIntersects",
        "inSR": "4326",
        "outFields": "DM",
        "returnGeometry": "false",
        "f": "json"
    }

    # Mechanizm ponowień (3 próby)
    for attempt in range(1, 4):
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            response = requests.get(BASE_URL, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Brak przecięć = "None"
            features = data.get("features", [])
            if not features:
                return "None"
            
            # Wyciągnięcie wartości indeksu suszy (małe 'dm') z przeciętych poligonów
            # Bierzemy max z tablicy w przypadku nakładających się warstw przestrzennych
            dm_values = [feat.get("attributes", {}).get("dm") for feat in features]
            valid_dms = [v for v in dm_values if v is not None]
            
            if not valid_dms:
                return "None"
                
            dm_value = max(valid_dms)
                
            try:
                # Mapujemy surową cyfrę do czytelnego standardu
                return DM_MAP.get(int(dm_value), "None")
            except ValueError:
                return "None"
                
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            if attempt < 3:
                print(f"    [!] Błąd Sieci/API (Próba {attempt}/3): {e}. Ponawiam za 5 s...")
                time.sleep(5)
            else:
                print(f"    [X] Ostateczna awaria dla tych koordynatów po 3 próbach: {e}")
                return "Error/Unknown"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ BŁĄD: Nie znaleziono bazy wejściowej -> {INPUT_FILE}")
        return

    # 1. Wczytanie Bazy (master_input)
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    # 2. Odczyt stanu wznawiania (Checkpointing)
    output_data = {}
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                output_data = json.load(f)
            print(f"📂 Wczytano {len(output_data)} istniejących rekordów z pliku {OUTPUT_FILE}.")
        except json.JSONDecodeError:
            print("⚠️ Checkpoint jest uszkodzony, skrypt nadpisze lub połączy istniejące zapytania.")

    total_records = len(master_data)
    processed_in_session = 0
    
    print(f"ArcGIS Pipeline -> Ekstrakcja danych o suszy dla {total_records} lokalizacji...\n")
    
    # 3. Główna pętla i zapytania
    for i, (zip_code, info) in enumerate(master_data.items(), 1):
        # RESUME CAPABILITY: Pomijanie już przeanalizowanych miast, o ile nie mają statusu "Error/Unknown"
        if zip_code in output_data and output_data[zip_code].get("drought_status") != "Error/Unknown":
            continue

        lat = info.get("lat")
        lng = info.get("lng")

        # Przypadek braku koordynatów w źródłowym pliku
        if lat is None or lng is None:
            print(f"[{i:04d}/{total_records}] {zip_code} - POMINIĘTO: Brak lokalizacji lat/lng")
            output_data[zip_code] = {"drought_status": "Error/Unknown"}
            continue

        # Wypuszczenie strzału do API
        status = get_drought_status(lat, lng)
        
        # Oczekiwany format odpowiedzi: {"77494": {"drought_status": "D2-Severe"}}
        output_data[zip_code] = {
            "drought_status": status
        }
        
        print(f"[{i:04d}/{total_records}] {zip_code} - Pobrane ze stacji bazowej: {status}")
        
        processed_in_session += 1

        # PERIODYCZNY CHECKPOINT I KONTROLA PRZEPUSTOWOŚCI (RATE LIMITING)
        if processed_in_session > 0 and processed_in_session % 50 == 0:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as file_out:
                json.dump(output_data, file_out, indent=2, ensure_ascii=False)
            print(f"   [💾 AUTOSAVE] -> Zachowano postęp po {i} miastach na dysku...")
            print(f"   [⏳ COOL-DOWN] -> Większa paczka pobrana. Odczekuję 30 sekund dla serwerów ArcGIS...\n")
            time.sleep(30.0)
        elif processed_in_session > 0 and processed_in_session % 25 == 0:
            print(f"   [⏳ COOL-DOWN] -> Szybki oddech. Odczekuję 5 sekund...\n")
            time.sleep(5.0)
        else:
            # STANDARDOWE LIMITOWANIE TRANSFERU BEZ UPOWAŻNIEŃ API 
            time.sleep(0.5)

    # 4. Finalny zapis resztek sesji do pliku
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file_out:
        json.dump(output_data, file_out, indent=2, ensure_ascii=False)
        
    print(f"\n✅ ETL Ukończony! Plik {OUTPUT_FILE} zapisany pomyślnie. Nowe odpytania API z tej sesji: {processed_in_session}")

if __name__ == "__main__":
    main()
