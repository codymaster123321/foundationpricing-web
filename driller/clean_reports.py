import os
import re

def clean_all_reports():
    reports_dir = "raw_reports"
    if not os.path.exists(reports_dir):
        print("BŁĄD: Folder 'raw_reports' nie istnieje.")
        return

    cleaned_count = 0
    for filename in os.listdir(reports_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(reports_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # The RegEx Scrubbing
            content = re.sub(r'^\[(?:Hard|Provided) Data\].*$', '', content, flags=re.MULTILINE | re.IGNORECASE)
            content = re.sub(r'\[(?:Hard|Provided) Data\]', '', content, flags=re.IGNORECASE)
            content = re.sub(r'\*?\(?Word\s*count[^0-9]*[0-9,]+\)?\*?', '', content, flags=re.IGNORECASE)
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            # Check if any changes were made
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Oczyszczono z halucynacji: {filename}")
                cleaned_count += 1
                
    print(f"\nSKAN ZAKOŃCZONY. Oczyszczono {cleaned_count} plików Markdown.")

if __name__ == "__main__":
    clean_all_reports()
