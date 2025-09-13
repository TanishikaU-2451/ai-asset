# AI Land Use Classification MVP

A Minimum Viable Product for AI-powered land use classification using satellite imagery.

## Overview

This MVP demonstrates the core workflow of:
1. Training a Random Forest model on satellite imagery
2. Classifying land use into Water, Forest, and Agriculture
3. Displaying results on an interactive web map

## Technology Stack

- **Data Source**: Sentinel-2 satellite imagery
- **AI/ML**: Random Forest (scikit-learn)
- **GIS**: QGIS for data preparation
- **Backend**: Flask (Python)
- **Frontend**: Leaflet.js
- **Data Format**: GeoJSON

## Project Structure

```
ai-asset/
├── data/                   # Raw satellite imagery and training data
├── models/                 # Trained ML models
├── output/                 # Generated classified maps and GeoJSON
├── templates/              # HTML templates
├── static/                 # CSS, JS, and other static files
├── scripts/                # Python processing scripts
├── app.py                  # Flask web server
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Setup Instructions

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Download Sentinel-2 imagery for your target area

3. Create training data using QGIS (see Phase 1)

4. Run the classification pipeline:
   ```bash
   python scripts/train_and_classify.py
   ```

5. Start the web server:
   ```bash
   python app.py
   ```

6. Open http://127.0.0.1:5000 in your browser

## Phases

- **Phase 1**: Data Preparation (QGIS + Sentinel-2)
- **Phase 2**: AI Model Training & Classification
- **Phase 3**: Web Server Backend (Flask)
- **Phase 4**: Web Map Frontend (Leaflet.js)
