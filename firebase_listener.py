import os
import json
import firebase_admin
from firebase_admin import credentials, db
import joblib
import time

# Load Firebase credentials from environment variable
firebase_key_json = os.environ.get("FIREBASE_KEY_JSON")

if not firebase_key_json:
    raise ValueError("FIREBASE_KEY_JSON environment variable not set!")

# Convert the JSON string to a dict
firebase_creds_dict = json.loads(firebase_key_json)

# Initialize Firebase app
cred = credentials.Certificate(firebase_creds_dict)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://energy-monitoring-and-tarif-default-rtdb.firebaseio.com/'
})

# Load the trained ML model
model = joblib.load('model.pkl')

# Reference to root
root_ref = db.reference('/')

def listen_and_predict():
    print("Listening to Firebase for changes...")
    while True:
        data = root_ref.get()
        B1 = data.get("B1", 0)
        B2 = data.get("B2", 0)
        B3 = data.get("B3", 0)

        # Determine load_during and load_after based on B1, B2, B3 status
        load_during = 1 if B1 == 1 or B2 == 1 or B3 == 1 else 0

        # Assume 'load_after' means load is STILL on after some duration
        # (In real case, you might use actual timing logic)
        load_after = load_during  # same initially

        if load_during == 1:
            print("Appliance ON detected. Running prediction...")

            # Use duration = 2, as per your dataset
            input_data = [[2, load_during, load_after]]
            prediction = model.predict(input_data)

            print(f"Model Prediction: {prediction[0]}")

            if prediction[0] == 1:
                print("Auto shut-off triggered. Waiting 2 minutes...")
                time.sleep(120)

                # Turn off all appliances
                updates = {
                    "B1": 0,
                    "B2": 0,
                    "B3": 0,
                    "timeusage": None
                }
                root_ref.update(updates)
                print("Appliances turned OFF via ML.")
        else:
            print("No appliance is ON.")

        time.sleep(2)

if __name__ == "__main__":
    listen_and_predict()
