import json
import os
import time
import re
from openai import OpenAI
from dotenv import load_dotenv

def main():
    # Krok 1: Wczytanie konfiguracji API
    load_dotenv()  # Wczytuje zmienne z pliku .env
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key or api_key == "wklej_tutaj_swoj_klucz_open_router":
        print("BŁĄD: Zmienna OPENROUTER_API_KEY nie została ustawiona w pliku .env.")
        return

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

    # Krok 2: Wczytanie pliku input_step3.json
    try:
        with open("data/final_enriched_database.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            print(f"Pomyślnie załadowano dane wejściowe dla {len(data)} miast.")
    except FileNotFoundError:
        print("BŁĄD: Nie znaleziono pliku input_step3.json.")
        return

    # Krok 3: Inicjalizacja wyników i odczyt Checkpointa
    output_filename = "output_step4_final.json"
    final_data = data.copy()
    
    if os.path.exists(output_filename):
        print(f"Znaleziono plik {output_filename}. Skrypt weryfikuje bazę danych i wznawia od ostatniego zapisu!")
        try:
            with open(output_filename, "r", encoding="utf-8") as outfile:
                saved_data = json.load(outfile)
                # Nadpisujemy danymi wejściowymi tylko te miasta, które zostały już pomyślnie przetworzone
                for k, v in saved_data.items():
                    if k in final_data and v.get("ai_research_status") == "SUCCESS":
                        final_data[k] = v
        except Exception as e:
            print(f"UWAGA: Problem z odczytem pliku checkpoint {output_filename}: {e}")

    # Tworzymy folder na surowe raporty, żeby utrzymać porządek
    os.makedirs("raw_reports", exist_ok=True)

    # Krok 4: Pętla po miastach i generowanie promptów
    for zip_id, info in final_data.items():
        city_name = info.get("city", "Unknown City")
        state_abbr = info.get("state_abbr", "Unknown")
        state_full = info.get("state_full", "Unknown State")
        county_name = info.get("county", "Unknown County")
        
        # New enriched variables
        usda_soil_index = info.get("usda_soil_index")
        drought_status = info.get("drought_status")
        median_year_built = info.get("median_year_built")
        median_home_value = info.get("median_home_value")
        owner_occupied_rate = info.get("owner_occupied_rate")
        median_income = info.get("median_income")
        labour_index = info.get("labour_index", 1.0)

        # --- TARCZA DANYCH (DATA SANITIZATION DO PROMPTU) ---
        prompt_soil = f"{usda_soil_index}%" if usda_soil_index not in [None, 0, 0.0, "0", "0.0"] else "DATA_MISSING"
        prompt_drought = str(drought_status) if drought_status not in [None, "null", ""] else "DATA_MISSING"
        prompt_year = str(median_year_built) if median_year_built not in [None, 0, "0"] else "DATA_MISSING"
        # ====================================

        # MECHANIZM WZNAWIANIA (CHECKPOINT)
        if info.get("ai_research_status") == "SUCCESS":
            safe_city_name = re.sub(r'[^a-zA-Z0-9_]', '', city_name.replace(' ', '_'))
            raw_filename = f"raw_reports/report_{zip_id}_{safe_city_name}.md"
            if os.path.exists(raw_filename):
                print(f"[{time.strftime('%H:%M:%S')}] POMIJANIE: {city_name}, {state_full} - raport już istnieje (wygenerowany wcześniej).")
                continue

        print(f"\n[{time.strftime('%H:%M:%S')}] Rozpoczynam Deep Research dla: {city_name}, {state_full}...")

        # Złożenie Metapromptu - Zmiana na format Markdown i dodanie klauzuli ratunkowej!
        metaprompt = f"""
You are an expert Geotechnical Researcher and Local Foundation Specialist writing a highly factual, yet accessible guide for homeowners in {city_name}, {state_full} ({county_name}). Your objective is to uncover obscure, hyper-local factual data about the city's soil, construction standards, and topography, and translate it into clear, engaging, B2C (Business-to-Consumer) language that a local homeowner can easily understand.

HARD DATA PROVIDED FOR THIS ZIP CODE:
- USDA Soil Clay Percentage: {prompt_soil}
- Current Drought Status: {prompt_drought}
- Median Year Homes Built: {prompt_year}
- Median Home Value: ${median_home_value}
- Owner-Occupied Rate: {owner_occupied_rate}%

CRITICAL FALLBACK CLAUSES (HOW TO HANDLE 'DATA_MISSING'):
- If Soil Clay Percentage is 'DATA_MISSING', it means the specific coordinate is heavily urbanized or unmapped. DO NOT invent a soil index number or assume it is zero. Instead, state that exact point data is obscured by urban development, and discuss the general geotechnical profile typical for {county_name}.
- If Median Year Built is 'DATA_MISSING', do not state a specific year. Discuss the general historical eras of housing development in this region.
- If Drought Status is 'DATA_MISSING', omit current drought conditions and discuss general historical weather and precipitation patterns for this part of {state_full}.

CRITICAL DIRECTIVES:
1. STRICT WORD COUNT: Your final output MUST be concise, ranging between 800 and 1500 words maximum.
2. NO AI FLUFF: Every sentence must contain a specific entity (date, neighborhood, creek, code number). However, explain these facts simply. 
3. HYPER-LOCAL EXCLUSIVITY: The facts MUST apply specifically to {city_name} or {county_name}. 
4. CITATIONS REQUIRED: Ground specific claims using inline numbers (e.g., [1], [2]) and provide the source URLs at the end.
5. OBJECTIVE TRUTH: If the city's geology provides naturally stable foundations (e.g., solid bedrock), explicitly state that homes here are generally safe. Do NOT fabricate foundation problems.

RESEARCH ANGLES REQUIRED:
Angle A: Local Building Code & Housing Age: Based on the Median Year Built ({median_year_built}), identify what foundation building codes or typical construction methods (e.g., slab vs. crawlspace) were popular during that specific era in {city_name}. Explain what this means for a homeowner today.
Angle B: Topography & Flood History: Identify exact names of creeks, aquifers, or floodplains in {city_name}. Explain how these specific water sources affect soil shifting in nearby neighborhoods.
Angle C: Soil Science & Geotechnical Data: Use the USDA Soil index ({usda_soil_index}) to explain the exact soil mechanics (shrink-swell potential, local clay names like Montmorillonite if applicable) under these homes.
Angle D: Real Estate Value & Repair ROI: Mention the Median Home Value (${median_home_value}) and Owner-Occupied Rate ({owner_occupied_rate}%). Explain why protecting a foundation is a critical financial investment for property values in this specific local market.

OUTPUT FORMAT:
Return your research as a well-formatted Markdown document. Do NOT use generic labels like "Angle A". Write engaging, unique, and SEO-optimized headers. STRICTLY FORBIDDEN: Do NOT include any "[Hard Data]" summaries, internal thought processes, or "(Word count: X)" markers anywhere in your final output. Return ONLY the final article content.

Structure your article exactly in this order:
# Write a catchy, unique H1 title about Foundation Health and Soil in {city_name}
## Write a unique H2 about {city_name}'s Housing Age & Building Codes
## Write a unique H2 about Local Topography, Flood History & Waterways
## Write a unique H2 about Local Soil Science & Geotechnical Data
## Write a unique H2 about Property Values & Foundation Repair ROI
## Citations
"""

        try:
            # Wywołanie modelu Perplexity przez OpenRouter
            response = client.chat.completions.create(
                model="perplexity/sonar-pro",
                messages=[
                    {"role": "user", "content": metaprompt}
                ]
            )
            
            # Pobranie odpowiedzi z modelu
            raw_content = response.choices[0].message.content
            
            # --- TARCZA ANTY-HALUCYNACYJNA (REGEX POST-PROCESSING) ---
            # 1. Usuwa całe zdania AI zaczynające się od twardych tagów (ignorując wielkość liter)
            raw_content = re.sub(r'^\[(?:Hard|Provided) Data\].*$', '', raw_content, flags=re.MULTILINE | re.IGNORECASE)
            # 2. Usuwa pozostawione doczepki typu "[Hard Data]" na końcach normalnych zdań
            raw_content = re.sub(r'\[(?:Hard|Provided) Data\]', '', raw_content, flags=re.IGNORECASE)
            # 3. Usuwa znaczniki liczby słów w każdej odmianie: (Word count: 1,128), *(Word Count - 900)* itp.
            raw_content = re.sub(r'\*?\(?Word\s*count[^0-9]*[0-9,]+\)?\*?', '', raw_content, flags=re.IGNORECASE)
            # 4. Kosmetyka pustych linii pozostawionych po wycinaniu
            raw_content = re.sub(r'\n{3,}', '\n\n', raw_content)
            raw_content = raw_content.strip()

            print(f" -> Otrzymano i przefiltrowano odpowiedź dla {city_name} (długość: {len(raw_content)} znaków).")

            # --- GENEROWANIE YAML FRONTMATTER ---
            def to_yaml_val(val):
                return "null" if val is None else str(val)
            
            frontmatter = f"""---
title: "Foundation Repair & Soil Guide for {city_name}, {state_full}"
city: "{city_name}"
state_full: "{state_full}"
state_abbr: "{state_abbr}"
county: "{county_name}"
zip_code: "{zip_id}"
usda_soil_index: {to_yaml_val(usda_soil_index)}
drought_status: "{to_yaml_val(drought_status)}"
median_year_built: {to_yaml_val(median_year_built)}
median_home_value: {to_yaml_val(median_home_value)}
owner_occupied_rate: {to_yaml_val(owner_occupied_rate)}
median_income: {to_yaml_val(median_income)}
labour_index: {to_yaml_val(labour_index)}
slug: "{state_abbr.lower()}/{city_name.lower().replace(' ', '-')}-foundation-soil-guide"
---

"""
            md_content_to_save = frontmatter + raw_content

            # BEZPIECZEŃSTWO: Od razu zapisujemy połączony tekst do pliku!
            safe_city_name = re.sub(r'[^a-zA-Z0-9_]', '', city_name.replace(' ', '_'))
            raw_filename = f"raw_reports/report_{zip_id}_{safe_city_name}.md"
            with open(raw_filename, "w", encoding="utf-8") as f:
                f.write(md_content_to_save)
            print(f" -> Zapisano plik MD (z YAML) do pliku: {raw_filename}")

            # Zapisujemy status w głównym słowniku (JSON pozostaje bez frontmatter)
            info["ai_research_raw_markdown"] = raw_content
            info["ai_research_status"] = "SUCCESS"

        except Exception as e:
            print(f" -> BŁĄD API OpenRouter dla {city_name}: {e}")
            info["ai_research_status"] = "ERROR"
            info["ai_research_error_msg"] = str(e)

        print(f"Oczekiwanie 3 sekund ze względu na limity API...")
        time.sleep(3)
        
        # AUTOSAVE (Zapis checkpointa po każdym mieście)
        try:
            with open(output_filename, "w", encoding="utf-8") as outfile:
                json.dump(final_data, outfile, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f" -> BŁĄD AUTOSAVE: {e}")

    # Krok 5: Zapis do pliku (Końcowy)
    try:
        with open(output_filename, "w", encoding="utf-8") as outfile:
            json.dump(final_data, outfile, indent=2, ensure_ascii=False)
        print(f"\nSUKCES: Wszystkie procesy zakończone. Zapisano wyniki do {output_filename}.")
        print("Surowe raporty znajdziesz w folderze 'raw_reports'.")
    except Exception as e:
        print(f"\nBŁĄD ZAPISU DO PLIKU: {e}")

if __name__ == "__main__":
    main()