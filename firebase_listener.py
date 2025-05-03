import firebase_admin
from firebase_admin import credentials, db
import requests
import time
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate('firebase_key.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-project-id.firebaseio.com/'  # <-- Replace this!
})

# Your deployed ML API URL
API_URL = "https://your-api-endpoint.onrender.com/auto-shutoff"  # <-- Replace this!

# Function to turn off appliances
def turn_off():
    print("Turning off appliances...")
    # Send POST request to ML API (to make prediction)
    try:
        res = requests.post(API_URL)
        print("API response (OFF):", res.text)
    except Exception as e:
        print("Error calling API:", e)

    # Set Firebase B1, B2, B3 to 0 (OFF)
    db.reference("B1").set(0)
    db.reference("B2").set(0)
    db.reference("B3").set(0)

# Main loop
already_triggered = False  # To prevent duplicate triggers

while True:
    try:
        b1 = db.reference("B1").get()
        b2 = db.reference("B2").get()
        b3 = db.reference("B3").get()

        if (b1 == 1 or b2 == 1 or b3 == 1) and not already_triggered:
            print(f"Bulb ON detected at {datetime.now()}. Hitting API...")

            # Call the ML API (bulb on logic)
            try:
                res = requests.post(API_URL)
                print("API response (ON):", res.text)
            except Exception as e:
                print("Error calling API:", e)

            already_triggered = True  # Don't re-trigger during 2 min wait
            time.sleep(120)  # Wait for 2 minutes

            turn_off()  # Turn bulb OFF

        elif b1 == 0 and b2 == 0 and b3 == 0:
            already_triggered = False  # Reset flag if all OFF

    except Exception as e:
        print("Error reading from Firebase:", e)

    time.sleep(1)  # Check every second
