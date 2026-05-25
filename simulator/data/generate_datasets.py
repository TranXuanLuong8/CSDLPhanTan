import csv
import os
from datetime import date, timedelta


BASE_DIR = os.path.dirname(__file__)


def _write_csv(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["resource_id", "location", "date", "available"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def generate():
    start = date(2026, 5, 22)
    days = 5
    hotel_rows = []
    flight_rows = []
    car_rows = []

    for i in range(days):
        d = (start + timedelta(days=i)).isoformat()
        hotel_rows.append({
            "resource_id": f"H-{i+1}",
            "location": "HCM",
            "date": d,
            "available": 5,
        })
        flight_rows.append({
            "resource_id": f"F-{i+1}",
            "location": "HCM",
            "date": d,
            "available": 8,
        })
        car_rows.append({
            "resource_id": f"C-{i+1}",
            "location": "HCM",
            "date": d,
            "available": 3,
        })

    _write_csv(os.path.join(BASE_DIR, "Hotel_Rooms.csv"), hotel_rows)
    _write_csv(os.path.join(BASE_DIR, "Flight_Seats.csv"), flight_rows)
    _write_csv(os.path.join(BASE_DIR, "Car_Rentals.csv"), car_rows)


if __name__ == "__main__":
    generate()
