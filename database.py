import json, os, uuid
from datetime import datetime

DB_FILE = "records.json"
SHARE_FILE = "shared_records.json"

def save_record(record: dict) -> bool:
    try:
        records = load_records()
        record["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        records.append(record)
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def load_records() -> list:
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def create_share_link(record: dict) -> str:
    try:
        share_id = str(uuid.uuid4())[:8]
        shared = {}
        if os.path.exists(SHARE_FILE):
            with open(SHARE_FILE, "r") as f:
                shared = json.load(f)
        shared[share_id] = record
        with open(SHARE_FILE, "w") as f:
            json.dump(shared, f, indent=2, ensure_ascii=False)
        return share_id
    except Exception:
        return ""

def get_shared_record(share_id: str):
    if not os.path.exists(SHARE_FILE):
        return None
    try:
        with open(SHARE_FILE, "r") as f:
            shared = json.load(f)
        return shared.get(share_id)
    except Exception:
        return None