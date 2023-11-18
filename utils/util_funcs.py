from pathlib import Path
import json
import time

def read_json(json_path: str) -> dict:
    json_path = str(Path(json_path))
    with open(json_path) as json_file:
        # read JSON file
        file_contents = json_file.read()
        # Return as dictionary
        parsed_json = json.loads(file_contents)
    return parsed_json

def timeit(func):
    @staticmethod
    def wrapper(*args, **kwargs):
        start = time.time()
        # runs the function
        function = func(*args, **kwargs)
        end = time.time()
        print("\n", "-" * 30, sep="")
        print(f"Elapsed time: {(end - start):.2f} seconds")
        print("-" * 30, "\n")
        return function

    return wrapper
