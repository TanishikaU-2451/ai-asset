#!/usr/bin/env python3
"""
AI Land Use Classification MVP
Phase 3: Web Server Backend

A minimal Flask server to serve the web map and provide data API.
"""

from flask import Flask, render_template, jsonify, send_from_directory
import os
import json

app = Flask(__name__)

# Configuration
GEOJSON_FILE = 'output/assets.geojson'
STATIC_DIR = 'static'
TEMPLATES_DIR = 'templates'

@app.route('/')
def index():
    """Serve the main web map page."""
    return render_template('index.html')

@app.route('/data')
def get_data():
    """API endpoint to serve the classified land use data as GeoJSON."""
    try:
        if not os.path.exists(GEOJSON_FILE):
            return jsonify({
                'error': 'No classified data available. Please run the classification script first.',
                'features': []
            }), 404
        
        with open(GEOJSON_FILE, 'r') as f:
            data = json.load(f)
        
        return jsonify(data)
    
    except Exception as e:
        return jsonify({
            'error': f'Error loading data: {str(e)}',
            'features': []
        }), 500

@app.route('/status')
def get_status():
    """API endpoint to check if classification data is available."""
    status = {
        'data_available': os.path.exists(GEOJSON_FILE),
        'geojson_file': GEOJSON_FILE,
        'file_exists': os.path.exists(GEOJSON_FILE)
    }
    
    if os.path.exists(GEOJSON_FILE):
        try:
            with open(GEOJSON_FILE, 'r') as f:
                data = json.load(f)
            status['feature_count'] = len(data.get('features', []))
            status['classes'] = list(set(feature['properties'].get('class', 'unknown') 
                                      for feature in data.get('features', [])))
        except Exception as e:
            status['error'] = str(e)
    
    return jsonify(status)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory(STATIC_DIR, filename)

if __name__ == '__main__':
    print("=== AI Land Use Classification MVP ===")
    print("Phase 3: Web Server Backend")
    print("Starting Flask server...")
    print("Open your browser to: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server\n")
    
    # Check if output directory exists
    if not os.path.exists('output'):
        os.makedirs('output')
        print("Created output directory")
    
    # Check if templates directory exists
    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR)
        print("Created templates directory")
    
    # Check if static directory exists
    if not os.path.exists(STATIC_DIR):
        os.makedirs(STATIC_DIR)
        print("Created static directory")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
