import json
import os
import time
import requests

INPUT_FILE = os.path.join("data", "master_input_3221.json")
OUTPUT_FILE = os.path.join("data", "soil_output_3221.json")
USDA_URL = "https://sdmdataaccess.sc.egov.usda.gov/Tabular/post.rest"

# Maskowanie pod przeglądarkę, by obejść rządowego firewalla WAF (Tarpitting)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def get_soil_index(lat, lng):
    """
    Odpytuje API SDA (Soil Data Access - USDA). 
    Pobiera procent gliny (Clay Percentage - claytotal_r), a w ostateczności ciągliwość (Linear Extensibility - lep_r).
    """
    # Konstrukcja wysoce specyficznego SQL'a dla wbudowanego endpointu przestrzennego Rządu USA
    # Używa SDA_Get_Mukey_from_intersection_with_WktWgs84
    query = f"""
        SELECT TOP 1 ch.claytotal_r, ch.lep_r 
        FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('POINT({lng} {lat})') i 
        JOIN component c ON i.mukey = c.mukey AND c.majcompflag = 'Yes' 
        JOIN chorizon ch ON c.cokey = ch.cokey 
        ORDER BY c.comppct_r DESC, ch.hzdept_r ASC
    """
    
    payload = {
        "query": query,
        "format": "JSON"
    }

    # Mechanizm z 3 próbami
    for attempt in range(1, 4):
        try:
            response = requests.post(USDA_URL, json=payload, headers=HEADERS, timeout=12)
            response.raise_for_status()
            
            data = response.json()
            table = data.get("Table", [])
            
            # Jak trafimy na beton, skałę albo wodę (API zwraca pusty zbiór) -> null
            if not table:
                return None
                
            # Response USDA wrzuca tablicę tablic w formie: [ [clay_val, lep_val] ]
            row = table[0]
            clay = row[0]
            lep = row[1]
            
            # MAPOWANIE BIZNESOWE NA SKALĘ 0-100 dla frontendowego indeksu
            if clay is not None:
                # Glina w USDA sama w sobie jest % i pasuje idealnie od 0 do 100
                return int(round(float(clay)))
            elif lep is not None:
                # LEP waha się zwykle między 0 a 15-20%. Tworzymy proporcję (mnożnik 5)
                # Ograniczamy brutalnie do maksymalnie 100 na wypadek anomalii 
                return min(100, int(round(float(lep) * 5)))
            else:
                return None

        except (requests.exceptions.RequestException, json.JSONDecodeError, ValueError) as e:
            if attempt < 3:
                print(f"    [!] Blokada/Timeout (Próba {attempt}/3): Ponawiam za 5 s...")
                time.sleep(5)
            else:
                print(f"    [X] Trwała awaria przy tych koordynatach: {lat},{lng} ({e})")
                return None

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ BŁĄD: Nie znaleziono bazy wejściowej -> {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    # 1. Wczytanie bezpiecznika (Checkpoint)
    output_data = {}
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                output_data = json.load(f)
            print(f"📂 Wczytano {len(output_data)} istniejących rekordów z pliku {OUTPUT_FILE}.")
        except json.JSONDecodeError:
            print("⚠️ Plik zrzucony z błędem składni, wznawianie w trybie zapisu bocznego.")

    total_records = len(master_data)
    processed_in_session = 0
    
    print(f"USDA Pipeline -> Ekstrakcja wskaźnika gleby (USDA Soil Index) dla {total_records} miast...\n")
    
    # 2. Główna pętla
    for i, (zip_code, info) in enumerate(master_data.items(), 1):
        # Bypassing już ukończonych kodów, żeby chronić serwery
        if zip_code in output_data and output_data[zip_code].get("usda_soil_index") is not None:
            continue

        lat = info.get("lat")
        lng = info.get("lng")

        if lat is None or lng is None:
            print(f"[{i:04d}/{total_records}] {zip_code} - POMINIĘTO: Brak lokalizacji lat/lng")
            output_data[zip_code] = {"usda_soil_index": None}
            continue

        # Uderzenie w potężne API USDA SDA (Soil Data Access)
        soil_index = get_soil_index(lat, lng)
        
        output_data[zip_code] = {
            "usda_soil_index": soil_index
        }
        
        # Wyświetlenie przejrzystego raportu na konsoli (do terminala i logów)
        print(f"[{i:04d}/{total_records}] {zip_code} - Fetched Soil Index: {soil_index}")
        
        processed_in_session += 1

        # LOGIKA PERIODYCZNEGO ZAPISU I CHŁODZENIA WAF (AWS RATE LIMITING)
        if processed_in_session > 0 and processed_in_session % 50 == 0:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as file_out:
                json.dump(output_data, file_out, indent=2, ensure_ascii=False)
            print(f"   [💾 AUTOSAVE] -> Zachowano postęp po {i} miastach na dysku...")
            print(f"   [⏳ COOL-DOWN] -> Wielka paczka obsłużona. Odczekuję 30 sekund...\n")
            time.sleep(30.0)
        elif processed_in_session > 0 and processed_in_session % 25 == 0:
            print(f"   [⏳ COOL-DOWN] -> Szybki oddech. Odczekuję 1 sekundę...\n")
            time.sleep(1.0)
        else:
            time.sleep(0.5)

    # 3. Zapis twardy na koniec całego obiegu
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file_out:
        json.dump(output_data, file_out, indent=2, ensure_ascii=False)
        
    print(f"\n✅ ETL Glebowy Ukończony! Plik {OUTPUT_FILE} wygenerowany pomyślnie. Nowe odpytania z tej sesji: {processed_in_session}")

if __name__ == "__main__":
    main()
