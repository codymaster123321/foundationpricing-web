import csv
import json
import os

def merge_zips():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')
    
    csv_path = os.path.join(data_dir, 'new_3221_codes.csv')
    new_json_path = os.path.join(data_dir, 'new_targets_only.json')
    master_json_path = os.path.join(data_dir, 'main_clean_targets.json')
    merged_json_path = os.path.join(data_dir, 'main_clean_targets_v2.json')
    
    # 1. READ CSV & CONVERT TO JSON OBJECTS
    new_objects = []
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            # Walidacja The Zip Code (zfill dla kodów Puerto Rico i wschodniego wybrzeża)
            zip_code = str(row['zip']).zfill(5)
            
            new_obj = {
                "zip": zip_code,
                "city": row['city'].strip(),
                "state": row['state'].strip(),
                "county": row['county'].strip(),
                "lat": float(row['lat']),
                "lng": float(row['lng']),
                "population": int(row['population'])
            }
            new_objects.append(new_obj)
            
    print(f"Successfully converted {len(new_objects)} new targets from CSV.")

    # 2. SAVE NEW TARGETS (THE DELTA FILE)
    with open(new_json_path, mode='w', encoding='utf-8') as f:
        json.dump(new_objects, f, indent=4)
    print(f"Saved delta file: {new_json_path}")

    # 3. MERGE WITH EXISTING MASTER JSON
    if os.path.exists(master_json_path):
        with open(master_json_path, mode='r', encoding='utf-8') as f:
            master_data = json.load(f)
            
        print(f"Loaded {len(master_data)} existing targets from master database.")
        
        # O(1) Merge
        combined_data = master_data + new_objects
        
        with open(merged_json_path, mode='w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=4)
            
        print(f"Successfully saved {len(combined_data)} total targets to: {merged_json_path}")
    else:
        print(f"ERROR: Could not find existing database at {master_json_path}")

if __name__ == "__main__":
    merge_zips()
