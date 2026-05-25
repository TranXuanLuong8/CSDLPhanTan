import csv


class DataStore:
    def __init__(self, name, csv_path):
        self.name = name
        self.csv_path = csv_path
        self.items = {}
        self._load()

    def _load(self):
        with open(self.csv_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                item_id = row["resource_id"]
                self.items[item_id] = {
                    "location": row["location"],
                    "date": row["date"],
                    "available": int(row["available"]),
                }

    def can_reserve(self, item_id, qty):
        if item_id not in self.items:
            return False
        return self.items[item_id]["available"] >= qty

    def reserve(self, item_id, qty):
        if not self.can_reserve(item_id, qty):
            return False
        self.items[item_id]["available"] -= qty
        return True

    def snapshot(self):
        return {k: v["available"] for k, v in self.items.items()}
