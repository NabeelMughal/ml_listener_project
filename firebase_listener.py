import os
import json
import firebase_admin
from firebase_admin import credentials, db
import numpy as np
import pickle
from datetime import datetime, timedelta
import time

# Load Firebase credentials from environment variable
firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

if not firebase_credentials_json:
    raise ValueError("Firebase credentials JSON not found in environment variable")

cred_dict = json.loads(firebase_credentials_json)

# Initialize Firebase Admin SDK
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://energy-monitoring-and-tarif-default-rtdb.firebaseio.com/'
})

# Load ML model
model = pickle.load(open("model.pkl", "rb"))

# Firebase references
appliance_ref = db.reference('/')
usage_ref = db.reference('Appliance Usage Time')

def monitor_appliances():
    print("👀 Listening to appliance states...")

    while True:
        try:
            appliances = appliance_ref.get()
            now = datetime.utcnow()

            for key, value in appliances.items():
                if key in ['B1', 'B2', 'B3']:
                    if value == "1":  # Appliance ON
                        start_time_str = usage_ref.child(key).get()

                        if not start_time_str:
                            usage_ref.child(key).set(now.isoformat())
                            print(f"⏱️ Start time noted for {key}")
                            continue

                        start_time = datetime.fromisoformat(start_time_str)
                        elapsed = (now - start_time).total_seconds() / 60

                        if elapsed >= 2:
                            duration = 2
                            load_during = 1
                            load_after = 0
                            time_of_day = 1 if now.hour >= 12 else 0
                            week_day = now.weekday()

                            features = [duration, load_during, load_after, time_of_day, week_day]
                            prediction = model.predict(np.array([features]))[0]

                            if prediction == 1:
                                appliance_ref.child(key).set("0")
                                usage_ref.child(key).delete()
                                print(f"🔴 {key} turned OFF by ML model")
                            else:
                                print(f"✅ {key} remains ON")
                        else:
                            print(f"⏳ {key} ON for {elapsed:.2f} minutes")
                    else:
                        usage_ref.child(key).delete()

            time.sleep(5)  # Check every 5 seconds

        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_appliances()
