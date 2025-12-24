import json
import os
from typing import List, Dict


RAW_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "raw"
)


class UnifiedSchemeLoader:
    """
    Loads government schemes from curated JSON files
    (skips empty or invalid files safely)
    """

    def load_all_schemes(self, limit: int | None = None) -> List[Dict]:
        schemes: List[Dict] = []

        for filename in os.listdir(RAW_DATA_DIR):
            if not filename.endswith(".json"):
                continue

            file_path = os.path.join(RAW_DATA_DIR, filename)

            # Skip empty files
            if os.path.getsize(file_path) == 0:
                print(f"⚠️ Skipping empty file: {filename}")
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    if not isinstance(data, list):
                        print(f"⚠️ Skipping invalid format (not a list): {filename}")
                        continue

                    schemes.extend(data)

            except json.JSONDecodeError:
                print(f"⚠️ Skipping invalid JSON file: {filename}")
                continue

        # Remove duplicates by title
        unique = {s["title"].lower(): s for s in schemes if "title" in s}
        schemes = list(unique.values())

        return schemes[:limit] if limit else schemes
