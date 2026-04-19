import json
import os

INPUT_FILE = "data/final_enriched_database.json"
OUTPUT_DIR = "../injector/public/api"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "zip-map.json")

def generate_zip_map():
    print("[SYSTEM] Booting O(1) Route Compilation sequence...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] Critical failure: Database missing at {INPUT_FILE}")
        return

    # 1. Zassysamy potezna baze
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        database = json.load(f)

    # 2. Tworzymy folder publicznego API dla Frontendu jezeli go jeszcze nie ma
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 3. Przepisujemy baze sprowadzajac ja prosto do pary ZIP -> URL SLUG
    zip_map = {}
    for zip_code, info in database.items():
        city = info.get("city")
        state_abbr = info.get("state_abbr")
        
        if city and state_abbr:
            # Mechanizm identyczny do funkcji .replace(/ /g, '-') uzytej w Vite Astro getStaticPaths.
            city_slug = city.lower().replace(" ", "-")
            state_slug = state_abbr.lower()
            zip_map[zip_code] = f"/{state_slug}/{city_slug}"

    # 4. Eksportujemy ultra czysty plik O(1) dla reactowego the Fetch Engine. Minimalizujemy go.
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(zip_map, f, separators=(",", ":"))

    print(f"[SUCCESS] Compiled Route Dictionary spanning {len(zip_map)} vectors to {OUTPUT_FILE}.")

if __name__ == "__main__":
    generate_zip_map()
