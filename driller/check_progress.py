import os

def check_progress():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.join(script_dir, "raw_reports")
    total_cities = 4544
    
    if not os.path.exists(directory):
        print(f"Błąd: Katalog '{directory}' nie istnieje.")
        return

    count = sum(1 for f in os.listdir(directory) if f.endswith(".md"))
    
    progress = (count / total_cities) * 100
    
    print("\n" + "="*40)
    print("📡 TELEMETRIA SYSTEMU: THE DRILLER")
    print("="*40)
    print(f"Wygenerowano raportów MD: {count}")
    print(f"Ilość docelowa w master_input: {total_cities}")
    print(f"Ukończono fazę E-E-A-T: {progress:.2f}%")
    print("="*40 + "\n")

if __name__ == "__main__":
    check_progress()
