import os
import subprocess
import sys
import time
import pandas as pd
from flask import Flask, jsonify

app = Flask(__name__)

# --- HARDENED INGESTION LAYER ---
def sync_engine():
    print("--- Sentinel: Starting Mandatory Data Sync ---")
    
    # Absolute pathing for cloud reliability
    base_dir = os.path.dirname(os.path.abspath(__file__))
    scraper = os.path.join(base_dir, "src", "network", "scraper.py")
    storage = os.path.join(base_dir, "storage")
    
    if not os.path.exists(storage):
        os.makedirs(storage)

    if os.path.exists(scraper):
        try:
            # Execute scraper and wait for it to finish
            result = subprocess.run(
                [sys.executable, scraper],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Scraper Output: {result.stdout[:100]}...")
        except Exception as e:
            print(f"CRITICAL: Scraper failed: {e}")
    else:
        print(f"CRITICAL: Scraper missing at {scraper}")

# --- PREDICTION LAYER ---
def extract_matches():
    all_data = []
    storage_path = "storage"
    
    if not os.path.exists(storage_path):
        return []

    for file in os.listdir(storage_path):
        if file.endswith(".csv"):
            try:
                # Use engine='python' to avoid C-level parsing errors on small files
                df = pd.read_csv(os.path.join(storage_path, file), engine='python')
                
                if df.empty:
                    continue
                
                # Grab the first 20 rows of whatever is in the file
                for _, row in df.head(20).iterrows():
                    # We convert the whole row to a dict so no data is missed
                    all_data.append(row.to_dict())
            except Exception as e:
                print(f"Error reading {file}: {e}")
    return all_data

# --- ROUTES ---
@app.route('/')
def home():
    return "<h1>Project Sentinel: ONLINE</h1>"

@app.route('/predict')
def predict():
    matches = extract_matches()
    return jsonify({
        "engine": "Project Sentinel V1",
        "user": "Malebane",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "matches_found": len(matches),
        "data": matches,
        "status": "LIVE_DATA_FEED" if matches else "NO_DATA_IN_STORAGE"
    })

if __name__ == "__main__":
    # Force sync before starting the server
    sync_engine()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
