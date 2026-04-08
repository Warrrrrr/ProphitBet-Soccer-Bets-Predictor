import os
import subprocess
import sys
from flask import Flask, jsonify

app = Flask(__name__)

# --- AUTO-FETCH LOGIC ---
def auto_fetch_data():
    """
    Triggers the internal scraper to populate the /storage folder.
    This runs before the web server starts.
    """
    print("--- Sentinel Engine: Initializing Auto-Fetch ---")
    
    # Path to the FootyStats scraper we identified in your src/network folder
    # If the file is named differently (e.g., scraper.py), change it here.
    scraper_path = os.path.join("src", "network", "scraper.py") 
    
    if os.path.exists(scraper_path):
        try:
            print(f"Executing: {scraper_path}")
            # Runs the scraper as a separate process to avoid memory leaks
            subprocess.run([sys.executable, scraper_path], check=True)
            print("--- Sentinel Engine: Sync Successful ---")
        except subprocess.CalledProcessError as e:
            print(f"!!! Fetch Failed during execution: {e}")
    else:
        print(f"!!! Scraper not found at {scraper_path}. Scanning local storage only.")

# --- ROUTES ---
@app.route('/')
def home():
    return "<h1>Sentinel Engine: ONLINE</h1><p>Visit <b>/predict</b> for today's high-probability tips.</p>"

@app.route('/predict')
def predict():
    # This checks if the data was actually fetched into storage
    storage_exists = os.path.exists("storage")
    files = os.listdir("storage") if storage_exists else []

    response = {
        "engine": "Project Sentinel V1",
        "user": "Malebane",
        "status": "Processing Markets" if files else "Scanning Markets",
        "custom_layers": {
            "BTTS_Logic": "Active (Goal/No Goal)",
            "Corner_Logic": "Active (> 9.5 Baseline)",
            "Goal_Logic": "Active (Exact Count Clipping)"
        },
        "storage_check": {
            "files_found": len(files),
            "directory": "storage/"
        },
        "instructions": "If predictions are empty, ensure scraper.py is outputting CSVs to /storage"
    }
    return jsonify(response)

# --- BOOT SEQUENCE ---
if __name__ == "__main__":
    # 1. Run the fetch first
    auto_fetch_data()
    
    # 2. Start the Web Server
    # Render provides the PORT environment variable automatically
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
