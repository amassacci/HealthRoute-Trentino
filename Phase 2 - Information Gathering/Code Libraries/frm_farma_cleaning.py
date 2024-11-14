from pathlib import Path
import os
import json
import csv
from collections import defaultdict

project_root = Path().resolve().parent
path = project_root.joinpath("data/health_facilities/raw_data")

with open(os.path.join(path,'dati-salute-gov-it-farmacie.json'), 'r') as file:
    data = json.load(file)

for item in data:
    for key, value in item.items():
        print(f"{key}: {value}")
    print()

# Extract unique values for "regione"
regione_values = {entry.get("regione") for entry in data if "regione" in entry}
print(regione_values)

# Filter entries where regione is "PROV. AUTON. TRENTO"
trentino_data = [entry for entry in data if entry.get("regione") == "PROV. AUTON. TRENTO"]
print(trentino_data)
print(len(trentino_data))

# Keys to remove
keys_to_remove = ["cod_farmacia_asl", "p_iva", "cod_provincia", "sigla_provincia", "provincia", "cod_regione", "codice_tipologia", "localizzazione"]

# Remove specified keys from each entry
for entry in trentino_data:
    for key in keys_to_remove:
        entry.pop(key)
print(trentino_data)

valid_data = [entry for entry in trentino_data if entry.get("data_fine_validita") == "-"]
len(valid_data)


# All uppercase
for entry in valid_data:
    print(entry)
    for key, value in entry.items():
        if isinstance(value, str):
            entry[key] = value.upper()
    print(entry)

    if "indirizzo" in entry:
        # Split the `indirizzo` value at the comma
        parts = entry["indirizzo"].split(",", 1)  # split at the first comma
        print(parts)
        entry["indirizzo"] = parts[0].strip()
        print(entry)
        entry["numero_civico"] = parts[1].strip() if len(parts) > 1 else "-"

print(json.dumps(valid_data, indent=4))


for i, entry in enumerate(valid_data):
    # Identify the last key and its value
    last_key = list(entry.keys())[-1]
    last_value = entry.pop(last_key)  # Remove the last key from the entry

    # Rebuild the entry with the last key at the third position
    new_entry = {}
    for j, (key, value) in enumerate(entry.items()):
        # Insert each key-value pair in the original order
        new_entry[key] = value
        # Insert the last key-value pair at the third position (index 2)
        if j == 1:  # After adding two keys (index 0 and 1), add the last key
            new_entry[last_key] = last_value

    # Replace the original entry with the reordered entry
    valid_data[i] = new_entry

# Print the modified data
print(json.dumps(valid_data, indent=4))

# Drop some other keys from each entry
for entry in valid_data:
    for key in ["cod_farmacia"]:
        entry.pop(key)
print(valid_data)



# Save to CSV
with open(os.path.join(path,'dati-salute-gov-it-farmacie-trentino.csv'), 'w') as csv_file:
    # Get field names (CSV column headers) from the first entry
    if trentino_data:
        fieldnames = valid_data[0].keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write headers
        writer.writeheader()

        # Write each entry in trentino_data to the CSV
        for entry in valid_data:
            writer.writerow(entry)