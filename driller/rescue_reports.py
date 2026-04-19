import json
import os
import re

def main():
    with open("output_step4_final.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    os.makedirs("raw_reports", exist_ok=True)
    
    for zip_id, info in data.items():
        if "ai_research" in info and "raw" in info["ai_research"]:
            raw_content = info["ai_research"]["raw"]
            city_name = info.get("city", "Unknown")
            state_name = info.get("state", "Unknown")
            
            safe_city_name = re.sub(r'[^a-zA-Z0-9_]', '', city_name.replace(' ', '_'))
            raw_filename = f"raw_reports/report_{safe_city_name}_{state_name}.md"
            
            with open(raw_filename, "w", encoding="utf-8") as out:
                out.write(raw_content)
            print(f"Odzyskano i zapisano: {raw_filename}")
            
if __name__ == "__main__":
    main()
