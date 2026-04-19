"""
=============================================================================
  FOUNDATION PRICING DATA — State Report Generator (Gemini Deep Research)
=============================================================================
  Automatyczny generator raportów stanowych wykorzystujący Gemini Deep Research
  Agent (Interactions API). 
  
  Funkcje:
  - Wczytuje szablon promptu z deep_research_state_reports/
  - Podmienia znacznik [STATE_NAME] na nazwę stanu
  - Uruchamia Deep Research w trybie background (async polling)
  - Zapisuje raporty .md z YAML Frontmatter do injector/src/data/state_reports/
  - Automatyczny checkpointing — pomija już wygenerowane raporty
  
  Wymagania:
    pip install google-genai python-dotenv
  
  Użycie:
    python generate_state_reports.py
=============================================================================
"""

import os
import sys
import time
import re
from dotenv import load_dotenv

# ═══════════════════════════════════════════════════════════════════════════════
#  KONFIGURACJA — Klucz API ładowany z driller/.env
#  Dodaj w pliku .env linię: GEMINI_API_KEY=twoj_klucz_tutaj
# ═══════════════════════════════════════════════════════════════════════════════

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ═══════════════════════════════════════════════════════════════════════════════
#  STAŁE KONFIGURACYJNE
# ═══════════════════════════════════════════════════════════════════════════════

# Agent Deep Research
AGENT_NAME = "deep-research-pro-preview-12-2025"

# Interwał pollingu w sekundach (co ile sprawdzamy status zadania)
POLL_INTERVAL_SECONDS = 15

# Maksymalny czas oczekiwania na raport (w sekundach) — 15 minut bezpieczeństwa
MAX_WAIT_SECONDS = 900

# Pauza między kolejnymi stanami (sekundy) — Rate Limit Protection
COOLDOWN_BETWEEN_STATES = 10

# Limit generacji w jednym uruchomieniu (faza testowa = 1, produkcja = 999)
# Ustaw na dużą liczbę (np. 999) aby wygenerować wszystkie brakujące raporty
NO_OF_GENERATIONS = 20

# Ścieżki plików (relatywne do katalogu skryptu /driller/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

TEMPLATE_PATH = os.path.join(
    PROJECT_ROOT, "deep_research_state_reports", "deep_research_state-reports.md"
)
OUTPUT_DIR = os.path.join(
    PROJECT_ROOT, "injector", "src", "data", "state_reports"
)

# ═══════════════════════════════════════════════════════════════════════════════
#  PEŁNA LISTA 50 STANÓW + DC
# ═══════════════════════════════════════════════════════════════════════════════

STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming", "District of Columbia"
]


# ═══════════════════════════════════════════════════════════════════════════════
#  FUNKCJE POMOCNICZE
# ═══════════════════════════════════════════════════════════════════════════════

def state_to_filename(state_name: str) -> str:
    """Konwertuje nazwę stanu na nazwę pliku: 'New York' -> 'new_york.md'"""
    return state_name.lower().replace(" ", "_") + ".md"


def state_to_slug(state_name: str) -> str:
    """Konwertuje nazwę stanu na slug: 'New York' -> 'new_york'"""
    return state_name.lower().replace(" ", "_")


def get_existing_reports(output_dir: str) -> set:
    """Zwraca zbiór nazw plików (set) już istniejących raportów."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        return set()
    return set(f for f in os.listdir(output_dir) if f.endswith(".md"))


def load_template(template_path: str) -> str:
    """Wczytuje szablon promptu z pliku."""
    if not os.path.exists(template_path):
        print(f"  ✖ BŁĄD KRYTYCZNY: Nie znaleziono szablonu: {template_path}")
        sys.exit(1)
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(template: str, state_name: str) -> str:
    """Podmienia [STATE_NAME] w szablonie na nazwę stanu."""
    return template.replace("[STATE_NAME]", state_name)


def add_frontmatter(report_text: str, state_slug: str) -> str:
    """Dodaje YAML Frontmatter na początku raportu."""
    frontmatter = f'---\nstate_slug: "{state_slug}"\n---\n\n'
    
    # Usuń ewentualny frontmatter dodany przez AI (gdyby sam go wygenerował)
    cleaned = re.sub(r'^---\s*\n.*?\n---\s*\n', '', report_text, flags=re.DOTALL)
    
    return frontmatter + cleaned.strip() + "\n"


def save_report(output_dir: str, filename: str, content: str):
    """Zapisuje raport do pliku .md"""
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    size_kb = os.path.getsize(filepath) / 1024
    print(f"  💾 Raport zapisany: {filepath} ({size_kb:.1f} KB)")


# ═══════════════════════════════════════════════════════════════════════════════
#  RDZEŃ — GEMINI DEEP RESEARCH API
# ═══════════════════════════════════════════════════════════════════════════════

def run_deep_research(client, prompt: str, state_name: str) -> str | None:
    """
    Uruchamia Gemini Deep Research w trybie asynchronicznym (background).
    Polluje status co POLL_INTERVAL_SECONDS aż do ukończenia.
    Zwraca tekst raportu lub None w przypadku błędu.
    """
    print(f"  🚀 Wysyłam zapytanie Deep Research dla: {state_name}...")
    
    try:
        interaction = client.interactions.create(
            input=prompt,
            agent=AGENT_NAME,
            background=True
        )
    except Exception as e:
        print(f"  ✖ Błąd podczas tworzenia interakcji: {e}")
        return None
    
    interaction_id = interaction.id
    print(f"  📡 Interakcja uruchomiona: {interaction_id}")
    print(f"  ⏳ Oczekiwanie na wynik (polling co {POLL_INTERVAL_SECONDS}s, max {MAX_WAIT_SECONDS}s)...")
    
    start_time = time.time()
    poll_count = 0
    
    while True:
        elapsed = time.time() - start_time
        
        # Zabezpieczenie czasowe
        if elapsed > MAX_WAIT_SECONDS:
            print(f"  ⚠️  TIMEOUT po {MAX_WAIT_SECONDS}s! Pomijam {state_name}.")
            return None
        
        time.sleep(POLL_INTERVAL_SECONDS)
        poll_count += 1
        
        try:
            interaction = client.interactions.get(interaction_id)
        except Exception as e:
            print(f"  ⚠️  Błąd pollingu (próba {poll_count}): {e}")
            # Nie rezygnujemy — spróbujemy ponownie przy następnym cyklu
            continue
        
        status = interaction.status
        elapsed_min = elapsed / 60
        
        if status == "completed":
            print(f"  ✅ Ukończono w {elapsed_min:.1f} min (po {poll_count} pollach)")
            
            # Wyciągnij tekst z ostatniego outputu
            if interaction.outputs and len(interaction.outputs) > 0:
                report_text = interaction.outputs[-1].text
                if report_text:
                    return report_text
                else:
                    print(f"  ⚠️  Interakcja completed ale brak tekstu w output!")
                    return None
            else:
                print(f"  ⚠️  Interakcja completed ale brak outputs!")
                return None
        
        elif status == "failed":
            error_msg = getattr(interaction, 'error', 'Nieznany błąd')
            print(f"  ✖ Badanie zakończone BŁĘDEM po {elapsed_min:.1f} min: {error_msg}")
            return None
        
        else:
            # Status: in_progress
            print(f"     ⏳ [{elapsed_min:.1f} min] Status: {status} (poll #{poll_count})")


# ═══════════════════════════════════════════════════════════════════════════════
#  GŁÓWNA PĘTLA WYKONAWCZA
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("  FOUNDATION PRICING DATA — State Report Generator")
    print("  Gemini Deep Research Agent (Interactions API)")
    print("=" * 70)
    
    # ── Walidacja klucza API ──
    if not GEMINI_API_KEY:
        print("\n  ✖ BŁĄD: Nie znaleziono GEMINI_API_KEY w pliku .env!")
        print("    Dodaj w driller/.env linię: GEMINI_API_KEY=twoj_klucz_tutaj")
        sys.exit(1)
    
    # ── Import SDK (po walidacji klucza, żeby nie crashować bez potrzeby) ──
    try:
        from google import genai
    except ImportError:
        print("\n  ✖ BŁĄD: Brak pakietu google-genai!")
        print("    Uruchom: pip install google-genai")
        sys.exit(1)
    
    # ── Inicjalizacja klienta ──
    client = genai.Client(api_key=GEMINI_API_KEY)
    print(f"\n  🔑 Klient Gemini API zainicjalizowany")
    
    # ── Wczytanie szablonu ──
    template = load_template(TEMPLATE_PATH)
    print(f"  📄 Szablon wczytany: {TEMPLATE_PATH}")
    
    # ── Skanowanie istniejących raportów (Checkpoint) ──
    existing_reports = get_existing_reports(OUTPUT_DIR)
    print(f"  📂 Katalog wyjściowy: {OUTPUT_DIR}")
    print(f"  📊 Już wygenerowanych raportów: {len(existing_reports)}")
    
    # ── Określenie listy stanów do przetworzenia ──
    states_todo = []
    states_skipped = []
    
    for state in STATES:
        filename = state_to_filename(state)
        if filename in existing_reports:
            states_skipped.append(state)
        else:
            states_todo.append(state)
    
    print(f"  ⏭️  Pomijam (już gotowe): {len(states_skipped)}")
    if states_skipped:
        print(f"     → {', '.join(states_skipped)}")
    
    print(f"  🎯 Do wygenerowania: {len(states_todo)}")
    if not states_todo:
        print("\n  ✅ Wszystkie raporty są już wygenerowane! Nic do roboty.")
        return
    
    # Przytnij kolejkę do limitu NO_OF_GENERATIONS
    if NO_OF_GENERATIONS < len(states_todo):
        states_todo = states_todo[:NO_OF_GENERATIONS]
        print(f"  🔒 Limit generacji: {NO_OF_GENERATIONS} (faza testowa)")
    
    print(f"\n  📋 Kolejka: {', '.join(states_todo)}")
    print(f"  ⏱️  Szacowany czas: ~{len(states_todo) * 5} min (przy ~5 min/raport)")
    print("-" * 70)
    
    # ── Pętla generacji ──
    success_count = 0
    fail_count = 0
    
    for i, state in enumerate(states_todo, 1):
        filename = state_to_filename(state)
        slug = state_to_slug(state)
        
        print(f"\n  ┌─────────────────────────────────────────────────────────")
        print(f"  │ [{i}/{len(states_todo)}] Generuję raport: {state}")
        print(f"  │ Plik: {filename} | Slug: {slug}")
        print(f"  └─────────────────────────────────────────────────────────")
        
        # Buduj prompt z podmianami
        prompt = build_prompt(template, state)
        
        # Wyślij do Deep Research
        report_text = run_deep_research(client, prompt, state)
        
        if report_text:
            # Dodaj frontmatter i zapisz
            final_content = add_frontmatter(report_text, slug)
            save_report(OUTPUT_DIR, filename, final_content)
            success_count += 1
        else:
            fail_count += 1
            print(f"  ✖ POMINIĘTO {state} — brak raportu od API")
        
        # Cooldown między stanami (nie dotyczy ostatniego)
        if i < len(states_todo):
            print(f"  ❄️  Cooldown {COOLDOWN_BETWEEN_STATES}s przed następnym stanem...")
            time.sleep(COOLDOWN_BETWEEN_STATES)
    
    # ── Podsumowanie ──
    print("\n" + "=" * 70)
    print("  PODSUMOWANIE GENERACJI")
    print("=" * 70)
    print(f"  ✅ Sukces:      {success_count}")
    print(f"  ✖  Błąd:        {fail_count}")
    print(f"  ⏭️  Pominięte:   {len(states_skipped)} (już istniały)")
    print(f"  ─────────────────────────────────────")
    print(f"  📊 Razem w bazie: {success_count + len(states_skipped)} / {len(STATES)}")
    
    if fail_count > 0:
        print(f"\n  ⚠️  {fail_count} raportów nie udało się wygenerować.")
        print(f"      Uruchom skrypt ponownie — checkpoint pominie gotowe raporty.")
    
    print(f"\n  🏁 Zakończono!")


if __name__ == "__main__":
    main()
