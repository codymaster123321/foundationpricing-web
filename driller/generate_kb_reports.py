"""
=============================================================================
  FOUNDATION PRICING DATA — Knowledge Base Report Generator (Gemini Deep Research)
=============================================================================
  Automatyczny generator artykułów do Bazy Wiedzy wykorzystujący Gemini Deep 
  Research Agent (Interactions API).
  
  Funkcje:
  - Parsuje tematy z knowledge-base_topics.md (19 tematów)
  - Wczytuje szablon promptu z deep_research_knowledge-base_prompt.md
  - Dynamicznie podmienia 5 znaczników: [Title], [Category], 
    [Primary Long-Tail Keyword], [Search Intent], [Content Angle & USP]
  - Uruchamia Deep Research w trybie background (async polling)
  - Zapisuje raporty .md do injector/src/data/knowledge-base/
  - Automatyczny checkpointing — pomija już wygenerowane raporty
  
  Wymagania:
    pip install google-genai python-dotenv
  
  Użycie:
    python generate_kb_reports.py
=============================================================================
"""

import os
import sys
import time
import re
from dotenv import load_dotenv

# ═══════════════════════════════════════════════════════════════════════════════
#  KONFIGURACJA — Klucz API ładowany z driller/.env
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

# Maksymalny czas oczekiwania na raport (w sekundach) — 15 minut
MAX_WAIT_SECONDS = 900

# Pauza między kolejnymi artykułami (sekundy) — Rate Limit Protection
COOLDOWN_BETWEEN_ARTICLES = 10

# Limit generacji w jednym uruchomieniu (faza testowa = 1, produkcja = 999)
NO_OF_GENERATIONS = 10

# Ścieżki plików
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

TEMPLATE_PATH = os.path.join(
    PROJECT_ROOT, "deep_research_knowledge_base_reports", 
    "deep_research_knowledge-base_prompt.md"
)

TOPICS_PATH = os.path.join(
    PROJECT_ROOT, "deep_research_knowledge_base_reports", 
    "knowledge-base_topics.md"
)

OUTPUT_DIR = os.path.join(
    PROJECT_ROOT, "injector", "src", "data", "knowledge-base"
)


# ═══════════════════════════════════════════════════════════════════════════════
#  PARSER TEMATÓW
# ═══════════════════════════════════════════════════════════════════════════════

def parse_topics(topics_path: str) -> list[dict]:
    """
    Parsuje plik knowledge-base_topics.md i zwraca listę słowników.
    Każdy słownik zawiera: title, category, keyword, intent, angle
    """
    if not os.path.exists(topics_path):
        print(f"  ✖ BŁĄD KRYTYCZNY: Nie znaleziono pliku tematów: {topics_path}")
        sys.exit(1)
    
    with open(topics_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Dzielimy po "Topic N" (N = cyfra)
    topic_blocks = re.split(r'^Topic\s+\d+\s*$', content, flags=re.MULTILINE)
    
    # Pierwszy element to pusty string (przed Topic 1), pomijamy
    topic_blocks = [block.strip() for block in topic_blocks if block.strip()]
    
    topics = []
    for block in topic_blocks:
        topic = {}
        
        # Wyciągamy pola — każde pole to "NazwaPola: reszta linii"
        title_match = re.search(r'^Title:\s*(.+)$', block, re.MULTILINE)
        category_match = re.search(r'^Category:\s*(.+)$', block, re.MULTILINE)
        keyword_match = re.search(r'^Primary Long-Tail Keyword:\s*(.+)$', block, re.MULTILINE)
        intent_match = re.search(r'^Search Intent:\s*(.+)$', block, re.MULTILINE)
        angle_match = re.search(r'^Content Angle & USP:\s*(.+)$', block, re.MULTILINE)
        
        if not title_match:
            print(f"  ⚠️  Pominięto blok bez Title: {block[:80]}...")
            continue
        
        topic["title"] = title_match.group(1).strip()
        topic["category"] = category_match.group(1).strip() if category_match else "General"
        topic["keyword"] = keyword_match.group(1).strip() if keyword_match else ""
        topic["intent"] = intent_match.group(1).strip() if intent_match else ""
        topic["angle"] = angle_match.group(1).strip() if angle_match else ""
        
        topics.append(topic)
    
    return topics


# ═══════════════════════════════════════════════════════════════════════════════
#  FUNKCJE POMOCNICZE
# ═══════════════════════════════════════════════════════════════════════════════

def title_to_filename(title: str) -> str:
    """
    Konwertuje tytuł artykułu na nazwę pliku .md.
    'The Dangers of DIY: Why Patching Drywall Cracks' -> 'the_dangers_of_diy_why_patching_drywall_cracks.md'
    """
    # Usuń znaki specjalne, zostaw litery, cyfry i spacje
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', title)
    # Zamień spacje na podkreślenia, lowercase
    slug = clean.lower().strip()
    slug = re.sub(r'\s+', '_', slug)
    # Ogranicz długość
    if len(slug) > 80:
        slug = slug[:80].rstrip('_')
    return slug + ".md"


def title_to_slug(title: str) -> str:
    """Zwraca slug bez rozszerzenia .md"""
    filename = title_to_filename(title)
    return filename[:-3]  # usunięcie '.md'


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


def build_prompt(template: str, topic: dict) -> str:
    """Podmienia 5 znaczników w szablonie na dane z topiku."""
    prompt = template
    prompt = prompt.replace("[Title]", topic["title"])
    prompt = prompt.replace("[Category]", topic["category"])
    prompt = prompt.replace("[Primary Long-Tail Keyword]", topic["keyword"])
    prompt = prompt.replace("[Search Intent]", topic["intent"])
    prompt = prompt.replace("[Content Angle & USP]", topic["angle"])
    return prompt


def clean_report_output(report_text: str) -> str:
    """
    Czyści output od Deep Research:
    - Zamienia [cite: X, Y] na [X, Y]
    - Usuwa sekcję **Sources:** i wszystko po niej
    """
    # 1. Zamiana [cite: X, Y] → [X, Y]
    report_text = re.sub(r'\[cite:\s*([^\]]+)\]', r'[\1]', report_text)
    
    # 2. Usunięcie sekcji Sources
    sources_pattern = re.compile(
        r'\n\s*\*{0,2}Sources:?\*{0,2}\s*\n.*',
        re.DOTALL | re.IGNORECASE
    )
    match = sources_pattern.search(report_text)
    if match:
        report_text = report_text[:match.start()]
    
    return report_text.rstrip() + "\n"


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

def run_deep_research(client, prompt: str, topic_title: str) -> str | None:
    """
    Uruchamia Gemini Deep Research w trybie asynchronicznym (background).
    Polluje status co POLL_INTERVAL_SECONDS aż do ukończenia.
    Zwraca tekst raportu lub None w przypadku błędu.
    """
    print(f"  🚀 Wysyłam zapytanie Deep Research...")
    
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
        
        if elapsed > MAX_WAIT_SECONDS:
            print(f"  ⚠️  TIMEOUT po {MAX_WAIT_SECONDS}s! Pomijam artykuł.")
            return None
        
        time.sleep(POLL_INTERVAL_SECONDS)
        poll_count += 1
        
        try:
            interaction = client.interactions.get(interaction_id)
        except Exception as e:
            print(f"  ⚠️  Błąd pollingu (próba {poll_count}): {e}")
            continue
        
        status = interaction.status
        elapsed_min = elapsed / 60
        
        if status == "completed":
            print(f"  ✅ Ukończono w {elapsed_min:.1f} min (po {poll_count} pollach)")
            
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
            print(f"     ⏳ [{elapsed_min:.1f} min] Status: {status} (poll #{poll_count})")


# ═══════════════════════════════════════════════════════════════════════════════
#  GŁÓWNA PĘTLA WYKONAWCZA
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("  FOUNDATION PRICING DATA — Knowledge Base Report Generator")
    print("  Gemini Deep Research Agent (Interactions API)")
    print("=" * 70)
    
    # ── Walidacja klucza API ──
    if not GEMINI_API_KEY:
        print("\n  ✖ BŁĄD: Nie znaleziono GEMINI_API_KEY w pliku .env!")
        print("    Dodaj w driller/.env linię: GEMINI_API_KEY=twoj_klucz_tutaj")
        sys.exit(1)
    
    # ── Import SDK ──
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
    
    # ── Parsowanie tematów ──
    topics = parse_topics(TOPICS_PATH)
    print(f"  📋 Sparsowanych tematów: {len(topics)}")
    
    # ── Skanowanie istniejących raportów (Checkpoint) ──
    existing_reports = get_existing_reports(OUTPUT_DIR)
    print(f"  📂 Katalog wyjściowy: {OUTPUT_DIR}")
    print(f"  📊 Już wygenerowanych raportów: {len(existing_reports)}")
    
    # ── Określenie listy tematów do przetworzenia ──
    topics_todo = []
    topics_skipped = []
    
    for topic in topics:
        filename = title_to_filename(topic["title"])
        if filename in existing_reports:
            topics_skipped.append(topic)
        else:
            topics_todo.append(topic)
    
    print(f"  ⏭️  Pomijam (już gotowe): {len(topics_skipped)}")
    if topics_skipped:
        for t in topics_skipped:
            print(f"     → {t['title'][:60]}...")
    
    print(f"  🎯 Do wygenerowania: {len(topics_todo)}")
    if not topics_todo:
        print("\n  ✅ Wszystkie artykuły są już wygenerowane! Nic do roboty.")
        return
    
    # Przytnij kolejkę do limitu NO_OF_GENERATIONS
    if NO_OF_GENERATIONS < len(topics_todo):
        topics_todo = topics_todo[:NO_OF_GENERATIONS]
        print(f"  🔒 Limit generacji: {NO_OF_GENERATIONS} (faza testowa)")
    
    print(f"\n  📋 Kolejka ({len(topics_todo)} artykułów):")
    for i, t in enumerate(topics_todo, 1):
        print(f"     {i}. {t['title'][:65]}")
    
    print(f"  ⏱️  Szacowany czas: ~{len(topics_todo) * 5} min (przy ~5 min/artykuł)")
    print("-" * 70)
    
    # ── Pętla generacji ──
    success_count = 0
    fail_count = 0
    
    for i, topic in enumerate(topics_todo, 1):
        filename = title_to_filename(topic["title"])
        
        print(f"\n  ┌─────────────────────────────────────────────────────────")
        print(f"  │ [{i}/{len(topics_todo)}] {topic['title'][:55]}")
        print(f"  │ Plik: {filename}")
        print(f"  │ Kategoria: {topic['category']}")
        print(f"  └─────────────────────────────────────────────────────────")
        
        # Buduj prompt z podmianami
        prompt = build_prompt(template, topic)
        
        # Wyślij do Deep Research
        report_text = run_deep_research(client, prompt, topic["title"])
        
        if report_text:
            # Wyczyść output (usun cite: i Sources)
            cleaned_report = clean_report_output(report_text)
            save_report(OUTPUT_DIR, filename, cleaned_report)
            success_count += 1
        else:
            fail_count += 1
            print(f"  ✖ POMINIĘTO — brak raportu od API")
        
        # Cooldown między artykułami (nie dotyczy ostatniego)
        if i < len(topics_todo):
            print(f"  ❄️  Cooldown {COOLDOWN_BETWEEN_ARTICLES}s przed następnym artykułem...")
            time.sleep(COOLDOWN_BETWEEN_ARTICLES)
    
    # ── Podsumowanie ──
    print("\n" + "=" * 70)
    print("  PODSUMOWANIE GENERACJI")
    print("=" * 70)
    print(f"  ✅ Sukces:      {success_count}")
    print(f"  ✖  Błąd:        {fail_count}")
    print(f"  ⏭️  Pominięte:   {len(topics_skipped)} (już istniały)")
    print(f"  ─────────────────────────────────────")
    print(f"  📊 Razem w bazie: {success_count + len(topics_skipped)} / {len(topics)}")
    
    if fail_count > 0:
        print(f"\n  ⚠️  {fail_count} artykułów nie udało się wygenerować.")
        print(f"      Uruchom skrypt ponownie — checkpoint pominie gotowe raporty.")
    
    print(f"\n  🏁 Zakończono!")


if __name__ == "__main__":
    main()
