import os

states = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming", "District of Columbia"
]

template_path = r"g:\0_RAFAL\Antigravity\subterra-project\deep_research_state_reports\deep_research_state-reports.md"
output_dir = r"g:\0_RAFAL\Antigravity\subterra-project\deep_research_state_reports"

with open(template_path, "r", encoding="utf-8") as f:
    template_content = f.read()

for state in states:
    new_content = template_content.replace("[STATE_NAME]", state)
    output_path = os.path.join(output_dir, f"{state}.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_content)

print(f"Pomyślnie nadpisano i wygenerowano {len(states)} plików stanowych!")
