#!/usr/bin/env python3
"""
FRA WebGIS Integration Application
Comprehensive Forest Rights Act (IFR/CFR/CR) management system
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import json
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

app = Flask(__name__)

# Configuration
FRA_GEOJSON_FILE = 'output/fra_claims.geojson'
FRA_ANALYTICS_FILE = 'output/fra_analytics.json'
STATIC_DIR = 'static'
TEMPLATES_DIR = 'templates'

class FRAWebGISManager:
    def __init__(self, geojson_file, analytics_file):
        self.geojson_file = geojson_file
        self.analytics_file = analytics_file
        self.claims_data = None
        self.analytics_data = None
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Load FRA claims and analytics data."""
        try:
            # Load claims data
            with open(self.geojson_file, 'r') as f:
                self.claims_data = json.load(f)
            
            # Load analytics data
            with open(self.analytics_file, 'r') as f:
                self.analytics_data = json.load(f)
            
            # Convert to DataFrame for easier processing
            features = []
            for feature in self.claims_data['features']:
                props = feature['properties'].copy()
                props['geometry'] = feature['geometry']
                features.append(props)
            
            self.df = pd.DataFrame(features)
            print(f"Loaded {len(self.df)} FRA claims")
            
        except Exception as e:
            print(f"Error loading FRA data: {e}")
            self.claims_data = {"type": "FeatureCollection", "features": []}
            self.analytics_data = {}
            self.df = pd.DataFrame()
    
    def get_filtered_claims(self, filters=None):
        """Get filtered FRA claims based on provided filters."""
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
            
            if 'fra_type' in filters and filters['fra_type']:
                filtered_df = filtered_df[filtered_df['fra_type'] == filters['fra_type']]
            
            if 'status' in filters and filters['status']:
                filtered_df = filtered_df[filtered_df['status'] == filters['status']]
            
            if 'tribal_community' in filters and filters['tribal_community']:
                filtered_df = filtered_df[filtered_df['tribal_community'] == filters['tribal_community']]
            
            if 'claim_area_min' in filters and filters['claim_area_min']:
                min_area = float(filters['claim_area_min'])
                filtered_df = filtered_df[filtered_df['claim_area_ha'] >= min_area]
            
            if 'claim_area_max' in filters and filters['claim_area_max']:
                max_area = float(filters['claim_area_max'])
                filtered_df = filtered_df[filtered_df['claim_area_ha'] <= max_area]
        
        # Convert back to GeoJSON format
        features = []
        for _, row in filtered_df.iterrows():
            # Clean properties to handle NaN values
            properties = {}
            for k, v in row.items():
                if k != 'geometry':
                    try:
                        if pd.isna(v):
                            properties[k] = None
                        elif isinstance(v, (np.integer, np.floating)):
                            if np.isnan(v):
                                properties[k] = None
                            else:
                                properties[k] = float(v) if isinstance(v, np.floating) else int(v)
                        else:
                            properties[k] = v
                    except (TypeError, ValueError):
                        # Handle any other conversion issues
                        properties[k] = str(v) if v is not None else None
            
            feature = {
                "type": "Feature",
                "properties": properties,
                "geometry": row['geometry']
            }
            features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "properties": {
                "total_claims": len(features),
                "filters_applied": filters or {}
            }
        }
    
    def get_analytics(self):
        """Get comprehensive FRA analytics."""
        try:
            # Ensure all data is JSON serializable
            import json
            json.dumps(self.analytics_data)  # Test if it's serializable
            return self.analytics_data
        except (TypeError, ValueError) as e:
            print(f"Analytics data not JSON serializable: {e}")
            # Return a simplified version
            return {
                "summary": {
                    "total_claims": len(self.df) if self.df is not None else 0,
                    "claims_by_type": self.df['fra_type'].value_counts().to_dict() if self.df is not None and len(self.df) > 0 else {},
                    "claims_by_status": self.df['status'].value_counts().to_dict() if self.df is not None and len(self.df) > 0 else {},
                    "claims_by_state": self.df['state'].value_counts().to_dict() if self.df is not None and len(self.df) > 0 else {}
                },
                "error": "Analytics data simplified due to serialization issues"
            }
    
    def get_claim_details(self, claim_id):
        """Get detailed information for a specific claim."""
        if self.df is None or len(self.df) == 0:
            return None
        
        claim = self.df[self.df['claim_id'] == claim_id]
        if len(claim) == 0:
            return None
        
        return claim.iloc[0].to_dict()
    
    def get_state_wise_summary(self):
        """Get state-wise summary of FRA claims."""
        if self.df is None or len(self.df) == 0:
            return {}
        
        state_summary = self.df.groupby('state').agg({
            'claim_id': 'count',
            'claim_area_ha': 'sum',
            'status': lambda x: (x == 'approved').sum(),
            'fra_type': lambda x: x.value_counts().to_dict()
        }).rename(columns={
            'claim_id': 'total_claims',
            'status': 'approved_claims'
        })
        
        return state_summary.to_dict('index')
    
    def get_tribal_community_analysis(self):
        """Get analysis by tribal community."""
        if self.df is None or len(self.df) == 0:
            return {}
        
        tribal_analysis = self.df.groupby('tribal_community').agg({
            'claim_id': 'count',
            'claim_area_ha': 'sum',
            'status': lambda x: (x == 'approved').sum(),
            'fra_type': lambda x: x.value_counts().to_dict()
        }).rename(columns={
            'claim_id': 'total_claims',
            'status': 'approved_claims'
        })
        
        return tribal_analysis.to_dict('index')
    
    def get_timeline_analysis(self):
        """Get timeline analysis of FRA claims."""
        if self.df is None or len(self.df) == 0:
            return {}
        
        # Convert submission_date to datetime
        self.df['submission_date'] = pd.to_datetime(self.df['submission_date'])
        self.df['submission_year'] = self.df['submission_date'].dt.year
        self.df['submission_month'] = self.df['submission_date'].dt.month
        
        # Yearly analysis
        yearly = self.df.groupby('submission_year').agg({
            'claim_id': 'count',
            'claim_area_ha': 'sum',
            'status': lambda x: (x == 'approved').sum()
        }).rename(columns={
            'claim_id': 'claims_submitted',
            'status': 'claims_approved'
        })
        
        # Monthly analysis for current year
        current_year = datetime.now().year
        monthly = self.df[self.df['submission_year'] == current_year].groupby('submission_month').agg({
            'claim_id': 'count',
            'claim_area_ha': 'sum'
        }).rename(columns={'claim_id': 'claims_submitted'})
        
        return {
            'yearly': yearly.to_dict('index'),
            'monthly': monthly.to_dict('index')
        }
    
    def get_performance_metrics(self):
        """Get performance metrics for FRA implementation."""
        if self.df is None or len(self.df) == 0:
            return {}
        
        total_claims = len(self.df)
        approved_claims = len(self.df[self.df['status'] == 'approved'])
        pending_claims = len(self.df[self.df['status'].isin(['submitted', 'under_review', 'field_verification'])])
        
        return {
            'total_claims': total_claims,
            'approved_claims': approved_claims,
            'pending_claims': pending_claims,
            'rejected_claims': len(self.df[self.df['status'] == 'rejected']),
            'approval_rate': round(approved_claims / total_claims * 100, 2) if total_claims > 0 else 0,
            'pending_rate': round(pending_claims / total_claims * 100, 2) if total_claims > 0 else 0,
            'total_area_ha': round(self.df['claim_area_ha'].sum(), 2),
            'average_claim_size_ha': round(self.df['claim_area_ha'].mean(), 2),
            'field_verification_rate': round(len(self.df[self.df['field_verification_done']]) / total_claims * 100, 2) if total_claims > 0 else 0,
            'gps_verification_rate': round(len(self.df[self.df['gps_coordinates_verified']]) / total_claims * 100, 2) if total_claims > 0 else 0
        }

# Initialize FRA manager
fra_manager = FRAWebGISManager(FRA_GEOJSON_FILE, FRA_ANALYTICS_FILE)

@app.route('/')
def index():
    """Serve the FRA WebGIS main page."""
    return render_template('fra_webgis.html')

@app.route('/india')
def india_webgis():
    """Serve the India Asset Management WebGIS."""
    return render_template('india_webgis.html')

@app.route('/api/assets')
def get_assets():
    """API endpoint to get asset data."""
    try:
        # Try to load enhanced assets first, fallback to original
        assets_files = ['output/assets_enhanced.geojson', 'output/assets.geojson']
        assets_data = None
        
        for assets_file in assets_files:
            try:
                with open(assets_file, 'r') as f:
                    assets_data = json.load(f)
                print(f"Loaded assets from {assets_file}")
                break
            except FileNotFoundError:
                continue
        
        if assets_data is None:
            raise FileNotFoundError("No assets file found")
            
        # Add filtering based on query parameters
        filters = {
            'asset_type': request.args.get('asset_type'),
            'state': request.args.get('state'),
            'min_area': request.args.get('min_area'),
            'max_area': request.args.get('max_area')
        }
        
        # Apply filters if provided
        if any(filters.values()):
            filtered_features = []
            for feature in assets_data['features']:
                props = feature['properties']
                
                # Asset type filter
                if filters['asset_type'] and props.get('class') != filters['asset_type']:
                    continue
                
                # State filter
                if filters['state'] and props.get('state') != filters['state']:
                    continue
                
                # Area filters
                area = props.get('area_km2', 0)
                if filters['min_area'] and area < float(filters['min_area']):
                    continue
                if filters['max_area'] and area > float(filters['max_area']):
                    continue
                
                filtered_features.append(feature)
            
            assets_data['features'] = filtered_features
        
        return jsonify(assets_data)
    except Exception as e:
        return jsonify({
            'error': f'Error loading assets: {str(e)}',
            'type': 'FeatureCollection',
            'features': []
        }), 500

@app.route('/api/fra-claims')  
def get_fra_claims():
    """API endpoint to get FRA claims data."""
    try:
        # Get filters from query parameters
        filters = {
            'state': request.args.get('state'),
            'district': request.args.get('district'),
            'village': request.args.get('village'),
            'fra_type': request.args.get('fra_type'),
            'status': request.args.get('status'),
            'tribal_community': request.args.get('tribal_community'),
            'claim_area_min': request.args.get('claim_area_min'),
            'claim_area_max': request.args.get('claim_area_max')
        }
        
        # Remove empty filters
        filters = {k: v for k, v in filters.items() if v}
        
        data = fra_manager.get_filtered_claims(filters)
        return jsonify(data)
    
    except Exception as e:
        return jsonify({
            'error': f'Error loading FRA claims: {str(e)}',
            'type': 'FeatureCollection',
            'features': []
        }), 500

@app.route('/test')
def test_page():
    """Serve the test page."""
    return send_from_directory('.', 'test_fra_webgis.html')

@app.route('/api/claims')
def get_claims():
    """API endpoint to get filtered FRA claims (legacy endpoint)."""
    return get_fra_claims()

@app.route('/api/analytics')
def get_analytics():
    """API endpoint to get FRA analytics."""
    try:
        analytics = fra_manager.get_analytics()
        return jsonify(analytics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/claim/<claim_id>')
def get_claim_details(claim_id):
    """API endpoint to get detailed claim information."""
    try:
        claim_details = fra_manager.get_claim_details(claim_id)
        if claim_details is None:
            return jsonify({'error': 'Claim not found'}), 404
        return jsonify(claim_details)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/state-summary')
def get_state_summary():
    """API endpoint to get state-wise summary."""
    try:
        summary = fra_manager.get_state_wise_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tribal-analysis')
def get_tribal_analysis():
    """API endpoint to get tribal community analysis."""
    try:
        analysis = fra_manager.get_tribal_community_analysis()
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/timeline')
def get_timeline_analysis():
    """API endpoint to get timeline analysis."""
    try:
        timeline = fra_manager.get_timeline_analysis()
        return jsonify(timeline)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance')
def get_performance_metrics():
    """API endpoint to get performance metrics."""
    try:
        metrics = fra_manager.get_performance_metrics()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/filter-options')
def get_filter_options():
    """API endpoint to get available filter options."""
    try:
        if fra_manager.df is None or len(fra_manager.df) == 0:
            return jsonify({})
        
        options = {
            'states': sorted(fra_manager.df['state'].unique().tolist()),
            'districts': sorted(fra_manager.df['district'].unique().tolist()),
            'villages': sorted(fra_manager.df['village'].unique().tolist()),
            'fra_types': sorted(fra_manager.df['fra_type'].unique().tolist()),
            'statuses': sorted(fra_manager.df['status'].unique().tolist()),
            'tribal_communities': sorted(fra_manager.df['tribal_community'].unique().tolist())
        }
        
        return jsonify(options)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export')
def export_claims():
    """API endpoint to export filtered claims data."""
    try:
        # Get filters from query parameters
        filters = {
            'state': request.args.get('state'),
            'district': request.args.get('district'),
            'village': request.args.get('village'),
            'fra_type': request.args.get('fra_type'),
            'status': request.args.get('status'),
            'tribal_community': request.args.get('tribal_community'),
            'claim_area_min': request.args.get('claim_area_min'),
            'claim_area_max': request.args.get('claim_area_max')
        }
        
        # Remove empty filters
        filters = {k: v for k, v in filters.items() if v}
        
        data = fra_manager.get_filtered_claims(filters)
        
        # Add export metadata
        data['export_info'] = {
            'exported_at': datetime.now().isoformat(),
            'filters_applied': filters,
            'total_claims': len(data['features'])
        }
        
        return jsonify(data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory(STATIC_DIR, filename)

if __name__ == '__main__':
    print("=== FRA WebGIS Integration Application ===")
    print("Starting FRA WebGIS server...")
    print("Open your browser to: http://127.0.0.1:5001")
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
    
    # Generate FRA data if it doesn't exist
    if not os.path.exists(FRA_GEOJSON_FILE):
        print("Generating FRA data...")
        os.system('python scripts/fra_webgis_generator.py')
    
    app.run(debug=True, host='127.0.0.1', port=5001)
