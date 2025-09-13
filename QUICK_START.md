# Quick Start Guide

Get the AI Land Use Classification MVP running in minutes!

## Prerequisites

- Python 3.8 or higher
- Internet connection for downloading dependencies

## Option 1: Test with Sample Data (5 minutes)

1. **Clone/Download** the project files
2. **Run Setup**:
   ```bash
   python setup.py
   ```
3. **Start Web Server**:
   ```bash
   python app.py
   ```
4. **Open Browser**: Go to http://127.0.0.1:5000

You'll see a map with sample land use data (Water, Forest, Agriculture) that you can toggle on/off.

## Option 2: Use Real Satellite Data (2-3 hours)

### Step 1: Prepare Data
1. Download Sentinel-2 imagery from [Copernicus Open Access Hub](https://scihub.copernicus.eu/)
2. Create training data in QGIS (see `PHASE1_DATA_PREPARATION.md`)
3. Place files in the correct directories:
   - `data/sentinel2_image.tif` - Satellite image
   - `data/training/` - Training shapefiles

### Step 2: Train AI Model
```bash
python scripts/train_and_classify.py
```

### Step 3: View Results
```bash
python app.py
```
Open http://127.0.0.1:5000

## Project Structure

```
ai-asset/
├── app.py                          # Flask web server
├── requirements.txt                # Python dependencies
├── setup.py                       # Setup script
├── scripts/
│   ├── train_and_classify.py      # AI model training
│   └── generate_sample_data.py    # Sample data generator
├── templates/
│   └── index.html                 # Web map interface
├── static/
│   ├── style.css                  # Styling
│   └── script.js                  # Interactive map logic
├── data/                          # Input data (you provide)
├── output/                        # Generated results
└── models/                        # Trained AI models
```

## Features

- **Interactive Map**: Zoom, pan, click for details
- **Layer Controls**: Toggle land use classes on/off
- **Real-time Data**: Live updates from AI classification
- **Responsive Design**: Works on desktop and mobile

## Troubleshooting

### Common Issues

1. **"No classified data available"**
   - Run `python scripts/generate_sample_data.py` for sample data
   - Or complete the real data workflow

2. **Python dependencies not found**
   - Run `pip install -r requirements.txt`

3. **Port already in use**
   - Change port in `app.py` (line with `app.run()`)

4. **QGIS not found**
   - Download from [qgis.org](https://qgis.org/)
   - Or use sample data instead

### Getting Help

- Check the detailed guides in the project
- Review error messages in the terminal
- Ensure all files are in the correct locations

## What's Next?

This MVP proves the concept works! You can then:

- Add more land use classes
- Improve the AI model (CNNs, more training data)
- Add a database (PostGIS)
- Deploy to the cloud
- Add user authentication
- Create mobile apps

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: Leaflet.js (JavaScript)
- **AI/ML**: scikit-learn (Random Forest)
- **GIS**: QGIS, GeoPandas, Rasterio
- **Data**: GeoJSON, Sentinel-2 imagery

---

**Ready to start?** Run `python setup.py` and follow the prompts!
