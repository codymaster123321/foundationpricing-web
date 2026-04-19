import json
from collections import defaultdict

def main():
    input_file = "data/final_enriched_database.json"
    output_file = "../injector/src/data/state-metrics.json"

    print("Ładowanie danych...")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"BŁĄD: Nie znaleziono pliku {input_file}")
        return

    # Inicjalizacja słownika do agregacji
    # Struktura: state_abbr -> { "count": 0, "total_usda": 0, "valid_usda_count": 0 }
    states_data = defaultdict(lambda: {"count": 0, "total_usda": 0, "valid_usda_count": 0})

    for zip_code, info in data.items():
        state = info.get("state_abbr")
        if not state:
            continue

        # Zwiększamy licznik wygenerowanych raportów dla tego stanu
        states_data[state]["count"] += 1

        # Agregacja USDA Index (tylko poprawne wartości)
        usda = info.get("usda_soil_index")
        if usda not in [None, 0, 0.0, "0", "0.0", "null", "None"]:
            try:
                states_data[state]["total_usda"] += float(usda)
                states_data[state]["valid_usda_count"] += 1
            except ValueError:
                pass # Ignoruj jeśli to jakiś dziwny string

    # Formatowanie do pliku wynikowego
    final_metrics = {}
    for state, metrics in states_data.items():
        avg_usda = 0.0
        if metrics["valid_usda_count"] > 0:
            avg_usda = round(metrics["total_usda"] / metrics["valid_usda_count"], 1)

        final_metrics[state] = {
            "reportCount": metrics["count"],
            "avg_usda_index": avg_usda
        }

    # Zapis do JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_metrics, f, indent=2)
    
    print(f"SUKCES: Wygenerowano metryki dla {len(final_metrics)} stanów i zapisano do {output_file}.")

if __name__ == "__main__":
    main()