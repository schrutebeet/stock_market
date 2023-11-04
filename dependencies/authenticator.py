import sys
import src
from pathlib import Path
api_dir = str(Path(src.__file__).parent.parent.parent / "keys")
print(api_dir)
sys.path.append(api_dir)
from alpha_key import api_key

api_key = api_key