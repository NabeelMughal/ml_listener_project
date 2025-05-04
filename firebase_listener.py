import time
import requests
import firebase_admin
from firebase_admin import credentials, db
import os
import json

print("Firebase listener script started.\nLibraries imported.")

# Load credentials from environment variable
firebase_key = os.environ.get("FIREBASE_CREDENTIALS_JSON")

if firebase_key is None:
    raise ValueError("FIREBASE_CREDENTIALS_JSON environment variable not set")

firebase_key_dict = json.loads(firebase_key)

cred = credentials.Certificate(firebase_key_dict)
firebase_admin.initialize_app(
    cred, {
        'databaseURL':
        'https://energy-monitoring-and-tarif-default-rtdb.firebaseio.com/'
    })

print("Firebase initialized successfully.")
print("Listener loop started. Monitoring appliance states...")

# Firebase reference to root (since B1, B2, B3 are at root)
ref = db.reference('/')

while True:
    try:
        data = ref.get()

        if data is None:
            print("❌ No data found at root. Waiting...")
        else:
            b1 = int(data.get("B1", 0))
            b2 = int(data.get("B2", 0))
            b3 = int(data.get("B3", 0))

            print(f"Status check - B1: {b1}, B2: {b2}, B3: {b3}")

            if b1 == 1 or b2 == 1 or b3 == 1:
                print("💡 One or more appliances are ON. Calling ML API...")
                try:
                    response = requests.get(
                        "https://web-production-0ef71.up.railway.app/auto-shutoff"
                    )
                    print("✅ API response:", response.text)
                except Exception as e:
                    print("❌ Error calling API:", e)

    except Exception as e:
        print("❌ Error fetching data from Firebase:", e)

    time.sleep(1)
