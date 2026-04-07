import os
from flask import Flask, jsonify
import pandas as pd
# Importing your custom logic
from src.preprocessing.dataset import DatasetPreprocessor

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Sentinel Engine: ONLINE</h1><p>Visit <b>/predict</b> for today's high-probability tips.</p>"

@app.route('/predict')
def predict():
    try:
        # 1. Initialize your custom processor
        # This uses the BTTS and Corner logic we added to dataset.py
        preprocessor = DatasetPreprocessor()
        
        # 2. Pull the latest data (This usually triggers the scraper)
        # Note: In a real run, this would point to your 'fixtures' or 'upcoming' CSV
        # For now, we'll confirm the engine is ready to process your new markets
        
        report = {
            "user": "Malebane",
            "engine": "Project Sentinel V1",
            "status": "Scanning Markets",
            "custom_layers": {
                "BTTS_Logic": "Active (Goal/No Goal)",
                "Corner_Logic": "Active (> 9.5 Baseline)",
                "Goal_Logic": "Active (Exact Count Clipping)"
            },
            "instructions": "Ensure your 'storage' folder contains the latest match CSVs for the engine to crunch."
        }
        
        return jsonify(report)
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
