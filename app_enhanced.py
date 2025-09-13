#!/usr/bin/env python3
"""
Enhanced AI Land Use Classification for India
Interactive web application with advanced features
"""

from flask import Flask, render_template, jsonify, request
import os
import json
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Configuration
GEOJSON_FILE = 'output/india_assets.geojson'
STATIC_DIR = 'static'
TEMPLATES_DIR = 'templates'

class IndiaLandUseAPI:
    def __init__(self, geojson_file):
        self.geojson_file = geojson_file
        self.data = None
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Load and process the GeoJSON data."""
        try:
            with open(self.geojson_file, 'r') as f:
                self.data = json.load(f)
            
            # Convert to DataFrame for easier filtering
            features = []
            for feature in self.data['features']:
                props = feature['properties'].copy()
                props['geometry'] = feature['geometry']
                features.append(props)
            
            self.df = pd.DataFrame(features)
            print(f"Loaded {len(self.df)} features")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            self.data = {"type": "FeatureCollection", "features": []}
            self.df = pd.DataFrame()
    
    def get_filtered_data(self, filters=None):
        """Get filtered data based on provided filters."""
        if self.df is None or len(self.df) == 0:
            return {"type": "FeatureCollection", "features": []}
        
        filtered_df = self.df.copy()
        
        if filters:
            # Apply filters
            if 'state' in filters and filters['state']:
                filtered_df = filtered_df[filtered_df['state'] == filters['state']]
            
            if 'district' in filters and filters['district']:
                filtered_df = filtered_df[filtered_df['district'] == filters['district']]
            
            if 'village' in filters and filters['village']:
                filtered_df = filtered_df[filtered_df['village'] == filters['village']]
            
            if 'tribal_group' in filters and filters['tribal_group']:
                filtered_df = filtered_df[filtered_df['tribal_community'] == filters['tribal_group']]
            
            if 'class' in filters and filters['class']:
                filtered_df = filtered_df[filtered_df['class'] == filters['class']]
            
            if 'fra_type' in filters and filters['fra_type']:
                filtered_df = filtered_df[filtered_df['fra_type'] == filters['fra_type']]
            
            if 'claim_status' in filters and filters['claim_status']:
                filtered_df = filtered_df[filtered_df['claim_status'] == filters['claim_status']]
        
        # Convert back to GeoJSON format
        features = []
        for _, row in filtered_df.iterrows():
            feature = {
                "type": "Feature",
                "properties": {k: v for k, v in row.items() if k != 'geometry'},
                "geometry": row['geometry']
            }
            features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "properties": {
                "total_features": len(features),
                "filters_applied": filters or {}
            }
        }
    
    def get_statistics(self):
        """Get comprehensive statistics."""
        if self.df is None or len(self.df) == 0:
            return {}
        
        stats = {
            "total_features": len(self.df),
            "class_distribution": self.df['class'].value_counts().to_dict(),
            "state_distribution": self.df['state'].value_counts().to_dict(),
            "fra_statistics": {}
        }
        
        # FRA specific statistics
        fra_data = self.df[self.df['class'] == 'fra_area']
        if len(fra_data) > 0:
            stats["fra_statistics"] = {
                "total_claims": len(fra_data),
                "fra_type_distribution": fra_data['fra_type'].value_counts().to_dict(),
                "claim_status_distribution": fra_data['claim_status'].value_counts().to_dict(),
                "tribal_community_distribution": fra_data['tribal_community'].value_counts().to_dict(),
                "state_wise_fra": fra_data['state'].value_counts().to_dict()
            }
        
        return stats
    
    def get_filter_options(self):
        """Get available filter options."""
        if self.df is None or len(self.df) == 0:
            return {}
        
        options = {
            "states": sorted(self.df['state'].unique().tolist()),
            "districts": sorted(self.df['district'].dropna().unique().tolist()),
            "villages": sorted(self.df['village'].dropna().unique().tolist()),
            "classes": sorted(self.df['class'].unique().tolist()),
            "tribal_communities": sorted(self.df['tribal_community'].dropna().unique().tolist()),
            "fra_types": sorted(self.df['fra_type'].dropna().unique().tolist()),
            "claim_statuses": sorted(self.df['claim_status'].dropna().unique().tolist())
        }
        
        return options

# Initialize API
api = IndiaLandUseAPI(GEOJSON_FILE)

@app.route('/')
def index():
    """Serve the enhanced web map page."""
    return render_template('india_map.html')

@app.route('/api/data')
def get_data():
    """API endpoint to serve filtered land use data."""
    try:
        # Get filters from query parameters
        filters = {
            'state': request.args.get('state'),
            'district': request.args.get('district'),
            'village': request.args.get('village'),
            'tribal_group': request.args.get('tribal_group'),
            'class': request.args.get('class'),
            'fra_type': request.args.get('fra_type'),
            'claim_status': request.args.get('claim_status')
        }
        
        # Remove empty filters
        filters = {k: v for k, v in filters.items() if v}
        
        data = api.get_filtered_data(filters)
        return jsonify(data)
    
    except Exception as e:
        return jsonify({
            'error': f'Error loading data: {str(e)}',
            'features': []
        }), 500

@app.route('/api/statistics')
def get_statistics():
    """API endpoint to get comprehensive statistics."""
    try:
        stats = api.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/filter-options')
def get_filter_options():
    """API endpoint to get available filter options."""
    try:
        options = api.get_filter_options()
        return jsonify(options)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fra-progress')
def get_fra_progress():
    """API endpoint to get FRA progress tracking data."""
    try:
        if api.df is None or len(api.df) == 0:
            return jsonify({'error': 'No data available'}), 404
        
        fra_data = api.df[api.df['class'] == 'fra_area']
        
        if len(fra_data) == 0:
            return jsonify({'error': 'No FRA data available'}), 404
        
        # Calculate progress by different levels
        progress = {
            'village_level': fra_data.groupby('village')['claim_status'].value_counts().unstack(fill_value=0).to_dict(),
            'block_level': fra_data.groupby('block')['claim_status'].value_counts().unstack(fill_value=0).to_dict(),
            'district_level': fra_data.groupby('district')['claim_status'].value_counts().unstack(fill_value=0).to_dict(),
            'state_level': fra_data.groupby('state')['claim_status'].value_counts().unstack(fill_value=0).to_dict(),
            'overall': fra_data['claim_status'].value_counts().to_dict()
        }
        
        return jsonify(progress)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/layers')
def get_layers():
    """API endpoint to get available layers."""
    layers = {
        'land_use': {
            'name': 'Land Use Classification',
            'description': 'AI-detected land use classes',
            'visible': True
        },
        'fra_areas': {
            'name': 'FRA Areas',
            'description': 'Forest Rights Act claim areas',
            'visible': True
        },
        'village_boundaries': {
            'name': 'Village Boundaries',
            'description': 'Administrative village boundaries',
            'visible': False
        },
        'state_boundaries': {
            'name': 'State Boundaries',
            'description': 'State administrative boundaries',
            'visible': True
        },
        'tribal_areas': {
            'name': 'Tribal Areas',
            'description': 'Areas with significant tribal population',
            'visible': False
        }
    }
    
    return jsonify(layers)

@app.route('/api/export')
def export_data():
    """API endpoint to export filtered data."""
    try:
        # Get filters from query parameters
        filters = {
            'state': request.args.get('state'),
            'district': request.args.get('district'),
            'village': request.args.get('village'),
            'tribal_group': request.args.get('tribal_group'),
            'class': request.args.get('class'),
            'fra_type': request.args.get('fra_type'),
            'claim_status': request.args.get('claim_status')
        }
        
        # Remove empty filters
        filters = {k: v for k, v in filters.items() if v}
        
        data = api.get_filtered_data(filters)
        
        # Add export metadata
        data['export_info'] = {
            'exported_at': datetime.now().isoformat(),
            'filters_applied': filters,
            'total_features': len(data['features'])
        }
        
        return jsonify(data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory(STATIC_DIR, filename)

if __name__ == '__main__':
    print("=== Enhanced AI Land Use Classification for India ===")
    print("Starting enhanced Flask server...")
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
    
    # Generate sample data if it doesn't exist
    if not os.path.exists(GEOJSON_FILE):
        print("Generating sample data...")
        os.system('python scripts/india_land_classification.py')
    
    app.run(debug=True, host='127.0.0.1', port=5000)
