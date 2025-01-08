import argparse
import datetime
import os
import pprint

from notion_client import Client
import garminconnect

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

GARMIN_USERNAME = os.getenv("GARMIN_USERNAME")
GARMIN_PASSWORD = os.getenv("GARMIN_PASSWORD")

def main():
    parser = argparse.ArgumentParser(description="Sync Garmin data to Notion.")
    parser.add_argument(
        "--date",
        help="Date in YYYY-MM-DD format. (default: yesterday's date)",
        default=None
    )
    args = parser.parse_args()

    # 日付を指定しない場合は「昨日」をデフォルトとする
    if args.date:
        date_str = args.date
    else:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        date_str = yesterday.strftime("%Y-%m-%d")

    print(f"Using date: {date_str}")

    notion = Client(auth=NOTION_TOKEN)
    garmin = garminconnect.Garmin(GARMIN_USERNAME, GARMIN_PASSWORD)
    garmin.login()

    records = garmin.get_stats_and_body(date_str)

    new_page = notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties={
            "Date": {"type": "date", "date": {"start": date_str}},
            "Steps": {"type": "number", "number": records.get("totalSteps", 0)},
            "Calories": {"type": "number", "number": records.get("totalKilocalories", 0)},
            "Weight": {"type": "number", "number": records.get("weight", 0)},
            "BodyFat": {"type": "number", "number": records.get("bodyFat", 0)},
            "BodyWater": {"type": "number", "number": records.get("bodyWater", 0)},
            "MuscleMass": {"type": "number", "number": records.get("muscleMass", 0)},
            "BoneMass": {"type": "number", "number": records.get("boneMass", 0)},
            "SleepingHours": {"type": "number", "number": round(records.get("sleepingSeconds", 0) / 3600, 1)},
            "BodyBatteryHighestValue": {"type": "number", "number": records.get("bodyBatteryHighestValue", 0)},
            "BodyBatteryLowestValue": {"type": "number", "number": records.get("bodyBatteryLowestValue", 0)},
            "AverageStressLevel": {"type": "number", "number": records.get("averageStressLevel", 0)},
            "TotalDistanceMeters": {"type": "number", "number": records.get("totalDistanceMeters", 0)},
        }
    )

    print("New page created in Notion:", new_page["id"])

if __name__ == "__main__":
    main()
