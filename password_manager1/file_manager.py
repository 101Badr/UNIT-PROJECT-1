import json
import os
from models import VaultItem
from dotenv import load_dotenv


load_dotenv()
FILENAME = os.getenv("DATA_FILENAME", "passwords_data.json")


def save_vault(items_list):
    
    try:
        data = [item.to_dict() for item in items_list]
        with open(FILENAME, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"❌ Error saving data: {e}")

def load_vault():
    
    if not os.path.exists(FILENAME):
        return []
    
    try:
        with open(FILENAME, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [VaultItem.from_dict(item) for item in data]
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return []