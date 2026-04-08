import os
import subprocess
import sys
import pandas as pd
from flask import Flask, jsonify

app = Flask(__name__)

def auto_fetch_data():
    print("--- Sentinel Engine: Initializing Auto-Fetch ---")
    # We use the direct path to the scraper you have in your network folder
    scraper_path = os.path.join("src", "network", "scraper.py") 
    if os.path.exists(scraper_path):
        try:
            subprocess.run([sys.executable, scraper_path], check=True)
        except Exception as e:
            print(f"Fetch Error: {e}")

def get_predictions():
    predictions = []
    storage_path = "storage/"
    
    if not os.path.exists(storage_path) or not os.listdir(storage_path):
        return [{"error": "Storage folder is empty or missing"}]

    for file in os.listdir(storage_path):
        if file.endswith(".csv"):
            try:
                df = pd.read_csv(os.path.join(storage_path, file))
                if df.empty:
                    continue
                
                # REASONING: Instead of specific names, we take the first 3 columns
                # This ensures we see data regardless of header naming
                for _, row in df.head(15).iterrows():
                    cols = row.index.tolist()
                    predictions.append({
                        "match": f"{row[cols[0]]} vs {row[cols[1]]}",
                        "raw_data": row.to_dict(), # This reveals the real column names to us
                        "source_file": file
                    })
            except Exception as e:
                predictions.append({"file_error": str(e), "file": file})
    return predictions

@app.route('/')
def home():
    return "<h1>Sentinel Engine: ONLINE</h1><p>Visit <b>/predict</b></p>"

@app.route('/predict')
def predict():
    preds = get_predictions()
    return jsonify({
        "engine": "Project Sentinel V1",
        "user": "Malebane",
        "matches_found": len(preds),
        "predictions": preds,
        "debug_info": "Check 'raw_data' to see actual CSV headers"
    })

if __name__ == "__main__":
    auto_fetch_data()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
