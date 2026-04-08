import os
import subprocess
import sys
import pandas as pd
from flask import Flask, jsonify

app = Flask(__name__)

# --- AUTO-FETCH LOGIC ---
def auto_fetch_data():
    print("--- Sentinel Engine: Initializing Auto-Fetch ---")
    # Path to your identified scraper
    scraper_path = os.path.join("src", "network", "scraper.py") 
    
    if os.path.exists(scraper_path):
        try:
            subprocess.run([sys.executable, scraper_path], check=True)
            print("--- Sentinel Engine: Sync Successful ---")
        except Exception as e:
            print(f"!!! Fetch Failed: {e}")
    else:
        print("!!! Scraper not found. Using existing storage data.")

# --- ENGINE LOGIC: THE PREDICTOR ---
def get_predictions():
    predictions = []
    storage_path = "storage/"
    
    if not os.path.exists(storage_path):
        return predictions

    # We look for the CSVs the scraper just created
    for file in os.listdir(storage_path):
        if file.endswith(".csv"):
            try:
                df = pd.read_csv(os.path.join(storage_path, file))
                # Basic logic to extract match rows (adjust column names to match your CSV)
                for _, row in df.head(10).iterrows():
                    match_data = {
                        "match": f"{row.get('home_team', 'TBD')} vs {row.get('away_team', 'TBD')}",
                        "probability": f"{row.get('win_prob', 0)}%",
                        "tip": "High Value" if row.get('win_prob', 0) > 70 else "Neutral"
                    }
                    predictions.append(match_data)
            except:
                continue
    return predictions

# --- ROUTES ---
@app.route('/')
def home():
    return "<h1>Sentinel Engine: ONLINE</h1><p>Visit <b>/predict</b> for matches.</p>"

@app.route('/predict')
def predict():
    preds = get_predictions()
    
    return jsonify({
        "engine": "Project Sentinel V1",
        "user": "Malebane",
        "status": "Success" if preds else "Processing Markets",
        "matches_found": len(preds),
        "predictions": preds,
        "custom_layers": {
            "BTTS_Logic": "Active",
            "Corner_Logic": "Active",
            "Goal_Logic": "Active"
        }
    })

if __name__ == "__main__":
    # Fetch data on startup
    auto_fetch_data()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
