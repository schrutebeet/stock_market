from pathlib import Path
import json

def read_json(json_path: str) -> dict:
    json_path = str(Path(json_path))
    with open(json_path) as json_file:
        # read JSON file
        file_contents = json_file.read()
        # Return as dictionary
        parsed_json = json.loads(file_contents)
    return parsed_json