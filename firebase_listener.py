import time
import requests
import threading
import firebase_admin
from firebase_admin import credentials, db
import os
import json

# Load Firebase credentials from environment variable
firebase_creds = json.loads(os.environ['FIREBASE_KEY_JSON'])
cred = credentials.Certificate(firebase_creds)

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://energy-monitoring-and-tarif-default-rtdb.firebaseio.com/'
})

API_URL = "https://web-production-0ef71.up.railway.app/auto-shutoff"

active_timers = {}

def handle_api_call(bulb_id):
    print(f"[INFO] Bulb {bulb_id} turned ON. Hitting API...")
    requests.get(API_URL)
    print("[INFO] Waiting 2 minutes...")
    time.sleep(120)
    print(f"[INFO] Calling API again to shut off Bulb {bulb_id}")
    requests.get(API_URL)
    # Optional: reset timer
    active_timers.pop(bulb_id, None)

def listener(event):
    data = event.data
    path = event.path
    if not isinstance(data, dict):  # single value changed
        if data == 1:
            bulb_id = path.strip("/")  # example: B1
            if bulb_id not in active_timers:
                thread = threading.Thread(target=handle_api_call, args=(bulb_id,))
                thread.start()
                active_timers[bulb_id] = thread

ref = db.reference("/")  # or "/bulbs" if B1/B2/B3 are inside a 'bulbs' node
ref.listen(listener)
