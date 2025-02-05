import json
from datetime import datetime, timedelta
import pytz

# Define the timezone difference (from UK to US Eastern Time)
UK_TZ = pytz.timezone('Europe/London')
US_TZ = pytz.timezone('US/Eastern')

def convert_time(uk_time_str):
    # Parse the time string into a datetime object
    uk_time = datetime.strptime(uk_time_str, "%H:%M")
    
    # Localize the time to UK timezone (assuming UK time is in GMT or BST)
    uk_time = UK_TZ.localize(uk_time, is_dst=None)  # Automatically adjusts for DST if needed
    
    # Convert to US Eastern Time
    us_time = uk_time.astimezone(US_TZ)
    
    # Return the time in 24-hour format (HH:MM)
    return us_time.strftime("%H:%M")

# Load the JSON data
with open('daddyliveSchedule.json', 'r') as file:
    data = json.load(file)

# Loop through the JSON and convert the "time" field
for day, schedule in data.items():
    for show in schedule['TV Shows']:
        show['time'] = convert_time(show['time'])

# Save the modified JSON data back to a file
with open('updated_schedule.json', 'w') as file:
    json.dump(data, file, indent=4)

print("Time conversion complete. Updated JSON saved as 'updated_schedule.json'.")
