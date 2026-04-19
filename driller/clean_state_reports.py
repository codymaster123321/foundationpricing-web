"""
=============================================================================
  FOUNDATION PRICING DATA — State Reports Cleaner
=============================================================================
  Skrypt czyszczący raporty stanowe z artefaktów Gemini Deep Research:
  
  1. Zamienia [cite: X, Y] na [X, Y] (usunięcie prefixu "cite: ")
  2. Usuwa sekcję **Sources:** i wszystko co po niej następuje
  
  Użycie:
    python clean_state_reports.py
=============================================================================
"""

import os
import re
import sys

# ═══════════════════════════════════════════════════════════════════════════════
#  KONFIGURACJA
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

REPORTS_DIR = os.path.join(
    PROJECT_ROOT, "injector", "src", "data", "state_reports"
)

# ═══════════════════════════════════════════════════════════════════════════════
#  LOGIKA CZYSZCZENIA
# ═══════════════════════════════════════════════════════════════════════════════

def clean_report(filepath: str) -> dict:
    """
    Czyści pojedynczy raport .md. Zwraca dict ze statystykami zmian.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    original_length = len(content)
    stats = {"cite_replacements": 0, "sources_removed": False}
    
    # ── 1. Zamiana [cite: X, Y] → [X, Y] ──
    # Obsługuje: [cite: 19, 21], [cite: 2], [cite: 1, 2, 3]
    def replace_cite(match):
        stats["cite_replacements"] += 1
        numbers = match.group(1)
        return f"[{numbers}]"
    
    content = re.sub(r'\[cite:\s*([^\]]+)\]', replace_cite, content)
    
    # ── 2. Usunięcie sekcji **Sources:** i wszystkiego po niej ──
    # Szukamy linii zawierającej **Sources:** (z ewentualnymi spacjami)
    sources_pattern = re.compile(
        r'\n\s*\*{0,2}Sources:?\*{0,2}\s*\n.*',
        re.DOTALL | re.IGNORECASE
    )
    
    match = sources_pattern.search(content)
    if match:
        content = content[:match.start()]
        stats["sources_removed"] = True
    
    # Wyczyść trailing whitespace i upewnij się że plik kończy się newline
    content = content.rstrip() + "\n"
    
    # Zapisz tylko jeśli coś się zmieniło
    if len(content) != original_length or stats["cite_replacements"] > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    
    return stats


# ═══════════════════════════════════════════════════════════════════════════════
#  GŁÓWNA PĘTLA
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  STATE REPORTS CLEANER")
    print("  Czyszczenie artefaktów Gemini Deep Research")
    print("=" * 60)
    
    if not os.path.exists(REPORTS_DIR):
        print(f"\n  ✖ Katalog nie istnieje: {REPORTS_DIR}")
        sys.exit(1)
    
    md_files = sorted([f for f in os.listdir(REPORTS_DIR) if f.endswith(".md")])
    
    if not md_files:
        print(f"\n  ✖ Brak plików .md w {REPORTS_DIR}")
        sys.exit(1)
    
    print(f"\n  📂 Katalog: {REPORTS_DIR}")
    print(f"  📊 Znalezionych raportów: {len(md_files)}")
    print("-" * 60)
    
    total_cites = 0
    total_sources = 0
    
    for filename in md_files:
        filepath = os.path.join(REPORTS_DIR, filename)
        stats = clean_report(filepath)
        
        total_cites += stats["cite_replacements"]
        if stats["sources_removed"]:
            total_sources += 1
        
        # Status dla każdego pliku
        cite_info = f"[cite:] → {stats['cite_replacements']}x"
        source_info = "Sources: ✂️ USUNIĘTE" if stats["sources_removed"] else "Sources: brak"
        
        if stats["cite_replacements"] > 0 or stats["sources_removed"]:
            print(f"  ✅ {filename:<35} | {cite_info:<20} | {source_info}")
        else:
            print(f"  ⏭️  {filename:<35} | Czysty — bez zmian")
    
    # Podsumowanie
    print("\n" + "=" * 60)
    print("  PODSUMOWANIE")
    print("=" * 60)
    print(f"  📝 Przetworzonych plików:     {len(md_files)}")
    print(f"  🔄 Zamienionych [cite:]:      {total_cites}")
    print(f"  ✂️  Usuniętych sekcji Sources: {total_sources}")
    print(f"\n  🏁 Zakończono!")


if __name__ == "__main__":
    main()
