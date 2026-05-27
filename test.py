import datetime
import json
time=datetime.datetime.now().strftime("%H:%M")
print(time)

with open("names.json", "r") as f:
    names = json.load(f)

print("Loaded names:", names)

checktime = ["9:05","9:55","11:00","11:50","13:30","14:20","15:20"]
cap_checktime = ["9:10","10:00","11:05","11:55","13:35","14:25","15:25"]

# helper: parse "HH:MM" -> minutes since midnight
def to_minutes(s: str) -> int:
    h, m = map(int, s.split(":"))
    return h * 60 + m

# parse schedules once
check_minutes = set(to_minutes(t) for t in checktime)
cap_check_minutes = set(to_minutes(t) for t in cap_checktime)

print("Check minutes:", check_minutes)