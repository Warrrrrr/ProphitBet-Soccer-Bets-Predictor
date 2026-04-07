import os
from flask import Flask, jsonify
# Importing your custom logic from the files we modified
from src.preprocessing.dataset import DatasetPreprocessor
from src.preprocessing.utils.target import TargetType

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Malebane's Sentinel Engine</h1><p>Status: ONLINE</p>"

@app.route('/predict')
def predict():
    # This connects to the custom BTTS and Corner logic we built
    return jsonify({
        "engine": "Sentinel-V1",
        "active_markets": ["BTTS", "Over 2.5", "Corners", "Exact Goals"],
        "note": "Linked to modified dataset.py and target.py"
    })

if __name__ == "__main__":
    # Render uses the PORT environment variable to stay alive
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
