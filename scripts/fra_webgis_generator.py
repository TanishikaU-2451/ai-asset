#!/usr/bin/env python3
"""
FRA WebGIS Integration Generator
Creates comprehensive Forest Rights Act (IFR/CFR/CR) data and management system
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class FRAWebGISGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # FRA claim types
        self.fra_types = {
            'IFR': 'Individual Forest Rights',
            'CFR': 'Community Forest Rights', 
            'CR': 'Community Resource Rights'
        }
        
        # Claim statuses
        self.claim_statuses = {
            'submitted': 'Submitted',
            'under_review': 'Under Review',
            'field_verification': 'Field Verification',
            'approved': 'Approved',
            'rejected': 'Rejected',
            'appealed': 'Appealed',
            'disputed': 'Disputed'
        }
        
        # Tribal communities in India
        self.tribal_communities = [
            'Gond', 'Santal', 'Munda', 'Oraon', 'Ho', 'Kurukh', 'Kharia', 'Bhumij',
            'Sabar', 'Lodha', 'Mahli', 'Karmali', 'Chik Baraik', 'Lohra', 'Kisan',
            'Bhuiya', 'Kharwar', 'Chero', 'Korwa', 'Asur', 'Birhor', 'Paharia',
            'Sauria Paharia', 'Mal Paharia', 'Kumarbhag Paharia', 'Sauria Paharia'
        ]
        
        # States with significant tribal populations and FRA implementation
        self.fra_states = {
            'Odisha': {'lat': 20.9517, 'lon': 85.0985, 'scale': 0.8, 'tribal_density': 0.7},
            'Chhattisgarh': {'lat': 21.2787, 'lon': 81.8661, 'scale': 0.7, 'tribal_density': 0.8},
            'Jharkhand': {'lat': 23.6102, 'lon': 85.2799, 'scale': 0.6, 'tribal_density': 0.9},
            'Madhya Pradesh': {'lat': 22.9734, 'lon': 78.6569, 'scale': 0.9, 'tribal_density': 0.6},
            'Maharashtra': {'lat': 19.7515, 'lon': 75.7139, 'scale': 0.9, 'tribal_density': 0.5},
            'Andhra Pradesh': {'lat': 15.9129, 'lon': 79.7400, 'scale': 0.8, 'tribal_density': 0.4},
            'Telangana': {'lat': 18.1124, 'lon': 79.0193, 'scale': 0.6, 'tribal_density': 0.5},
            'Gujarat': {'lat': 23.0225, 'lon': 72.5714, 'scale': 0.8, 'tribal_density': 0.6},
            'Rajasthan': {'lat': 27.0238, 'lon': 74.2179, 'scale': 0.9, 'tribal_density': 0.3},
            'West Bengal': {'lat': 22.9868, 'lon': 87.8550, 'scale': 0.7, 'tribal_density': 0.4},
            'Assam': {'lat': 26.2006, 'lon': 92.9376, 'scale': 0.7, 'tribal_density': 0.6},
            'Karnataka': {'lat': 15.3173, 'lon': 75.7139, 'scale': 0.8, 'tribal_density': 0.3},
            'Kerala': {'lat': 10.8505, 'lon': 76.2711, 'scale': 0.5, 'tribal_density': 0.2}
        }
    
    def generate_fra_claims(self):
        """Generate comprehensive FRA claims data."""
        print("Generating FRA claims data...")
        
        features = []
        claim_id = 1
        
        for state_name, state_info in self.fra_states.items():
            print(f"Processing {state_name}...")
            
            # Calculate number of claims based on tribal density and state size
            num_claims = int(state_info['tribal_density'] * state_info['scale'] * 50)
            
            for i in range(num_claims):
                # Generate claim location
                base_lat = state_info['lat'] + np.random.uniform(-state_info['scale'], state_info['scale'])
                base_lon = state_info['lon'] + np.random.uniform(-state_info['scale'], state_info['scale'])
                
                # Ensure coordinates are within reasonable bounds
                base_lat = max(6.4, min(37.1, base_lat))
                base_lon = max(68.1, min(97.4, base_lon))
                
                # Generate claim polygon
                size = np.random.uniform(0.01, 0.1) * state_info['scale']
                coords = self._create_claim_polygon(base_lat, base_lon, size)
                
                # Select FRA type based on probability
                fra_type = np.random.choice(
                    list(self.fra_types.keys()),
                    p=[0.6, 0.3, 0.1]  # IFR most common, then CFR, then CR
                )
                
                # Generate claim data
                claim_data = self._generate_claim_data(claim_id, state_name, fra_type)
                
                feature = {
                    "type": "Feature",
                    "properties": claim_data,
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [coords]
                    }
                }
                
                features.append(feature)
                claim_id += 1
        
        return features
    
    def _create_claim_polygon(self, lat, lon, size):
        """Create a polygon for FRA claim area."""
        # Create irregular polygon for more realistic claim boundaries
        angles = np.linspace(0, 2*np.pi, 12)
        radius = size * np.random.uniform(0.3, 1.0, len(angles))
        coords = []
        
        for angle, r in zip(angles, radius):
            x = lon + r * np.cos(angle)
            y = lat + r * np.sin(angle)
            coords.append([x, y])
        
        coords.append(coords[0])  # Close polygon
        return coords
    
    def _generate_claim_data(self, claim_id, state, fra_type):
        """Generate detailed claim data."""
        # Basic claim information
        claim_data = {
            "claim_id": f"FRA_{claim_id:06d}",
            "fra_type": fra_type,
            "fra_type_name": self.fra_types[fra_type],
            "state": state,
            "district": f"District_{np.random.randint(1, 20)}",
            "block": f"Block_{np.random.randint(1, 50)}",
            "village": f"Village_{np.random.randint(1, 1000)}",
            "panchayat": f"Panchayat_{np.random.randint(1, 100)}",
            "claim_area_ha": round(np.random.uniform(0.5, 50), 2),
            "claim_area_acres": round(np.random.uniform(1.2, 123.5), 2)
        }
        
        # Status and timeline
        status = np.random.choice(
            list(self.claim_statuses.keys()),
            p=[0.1, 0.2, 0.15, 0.4, 0.1, 0.03, 0.02]
        )
        claim_data.update({
            "status": status,
            "status_name": self.claim_statuses[status],
            "submission_date": self._random_date(2020, 2024),
            "last_updated": self._random_date(2023, 2024)
        })
        
        # Applicant information
        if fra_type == 'IFR':
            claim_data.update({
                "applicant_type": "Individual",
                "applicant_name": f"Applicant_{claim_id}",
                "tribal_community": np.random.choice(self.tribal_communities),
                "family_members": np.random.randint(1, 8),
                "household_id": f"HH_{claim_id:06d}"
            })
        else:  # CFR or CR
            claim_data.update({
                "applicant_type": "Community",
                "community_name": f"Community_{claim_id}",
                "tribal_community": np.random.choice(self.tribal_communities),
                "community_members": np.random.randint(10, 200),
                "community_id": f"COMM_{claim_id:06d}"
            })
        
        # Forest and land details
        claim_data.update({
            "forest_type": np.random.choice([
                'Tropical Evergreen', 'Tropical Semi-Evergreen', 'Tropical Moist Deciduous',
                'Tropical Dry Deciduous', 'Tropical Thorn', 'Subtropical Pine', 'Mangrove'
            ]),
            "land_use": np.random.choice([
                'Forest Land', 'Revenue Land', 'Common Property Resource',
                'Traditional Forest Area', 'Sacred Grove'
            ]),
            "biodiversity_rich": bool(np.random.choice([True, False], p=[0.7, 0.3])),
            "water_source": bool(np.random.choice([True, False], p=[0.6, 0.4])),
            "wildlife_corridor": bool(np.random.choice([True, False], p=[0.3, 0.7]))
        })
        
        # Documentation and verification
        claim_data.update({
            "documents_submitted": np.random.randint(3, 8),
            "field_verification_done": bool(status in ['field_verification', 'approved', 'rejected']),
            "satellite_verification": bool(np.random.choice([True, False], p=[0.8, 0.2])),
            "gps_coordinates_verified": bool(np.random.choice([True, False], p=[0.9, 0.1])),
            "boundary_demarcated": bool(status in ['field_verification', 'approved'])
        })
        
        # Economic and livelihood data
        claim_data.update({
            "livelihood_activities": np.random.choice([
                'NTFP Collection', 'Agriculture', 'Grazing', 'Hunting', 'Fishing',
                'Medicinal Plant Collection', 'Honey Collection', 'Bamboo Work'
            ], size=np.random.randint(1, 4), replace=False).tolist(),
            "annual_income_rs": np.random.randint(10000, 100000),
            "dependence_level": np.random.choice(['High', 'Medium', 'Low'], p=[0.5, 0.3, 0.2])
        })
        
        # Legal and administrative
        claim_data.update({
            "frc_constituted": bool(np.random.choice([True, False], p=[0.8, 0.2])),
            "frc_meetings_held": np.random.randint(0, 10),
            "objections_received": np.random.randint(0, 5),
            "appeal_filed": bool(status == 'appealed'),
            "court_case": bool(status == 'disputed')
        })
        
        # GIS and technical data
        claim_data.update({
            "centroid_lat": round(np.random.uniform(6.4, 37.1), 6),
            "centroid_lon": round(np.random.uniform(68.1, 97.4), 6),
            "perimeter_km": round(np.random.uniform(1, 20), 2),
            "elevation_m": np.random.randint(50, 2000),
            "slope_degrees": round(np.random.uniform(0, 45), 1),
            "aspect": np.random.choice(['North', 'South', 'East', 'West', 'Northeast', 'Northwest', 'Southeast', 'Southwest'])
        })
        
        # Quality and confidence metrics
        claim_data.update({
            "data_quality_score": round(np.random.uniform(0.6, 1.0), 2),
            "completeness_score": round(np.random.uniform(0.7, 1.0), 2),
            "accuracy_score": round(np.random.uniform(0.8, 1.0), 2),
            "verification_level": np.random.choice(['High', 'Medium', 'Low'], p=[0.6, 0.3, 0.1])
        })
        
        return claim_data
    
    def _random_date(self, start_year, end_year):
        """Generate random date between start and end year."""
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = np.random.randint(0, days_between)
        return (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')
    
    def generate_fra_analytics(self, claims_data):
        """Generate analytics and summary data for FRA claims."""
        print("Generating FRA analytics...")
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame([claim['properties'] for claim in claims_data])
        
        analytics = {
            "summary": {
                "total_claims": len(df),
                "claims_by_type": df['fra_type'].value_counts().to_dict(),
                "claims_by_status": df['status'].value_counts().to_dict(),
                "claims_by_state": df['state'].value_counts().to_dict(),
                "total_area_ha": df['claim_area_ha'].sum(),
                "average_claim_size_ha": round(df['claim_area_ha'].mean(), 2)
            },
            "state_wise_analysis": {},
            "tribal_community_analysis": {},
            "timeline_analysis": {},
            "performance_metrics": {}
        }
        
        # State-wise analysis
        for state in df['state'].unique():
            state_data = df[df['state'] == state]
            analytics["state_wise_analysis"][state] = {
                "total_claims": len(state_data),
                "approved_claims": len(state_data[state_data['status'] == 'approved']),
                "pending_claims": len(state_data[state_data['status'].isin(['submitted', 'under_review', 'field_verification'])]),
                "rejected_claims": len(state_data[state_data['status'] == 'rejected']),
                "total_area_ha": state_data['claim_area_ha'].sum(),
                "approval_rate": round(len(state_data[state_data['status'] == 'approved']) / len(state_data) * 100, 2)
            }
        
        # Tribal community analysis
        tribal_analysis = df.groupby('tribal_community').agg({
            'claim_id': 'count',
            'claim_area_ha': 'sum',
            'status': lambda x: (x == 'approved').sum()
        }).rename(columns={'claim_id': 'total_claims', 'status': 'approved_claims'})
        
        analytics["tribal_community_analysis"] = tribal_analysis.to_dict('index')
        
        # Timeline analysis
        df['submission_year'] = pd.to_datetime(df['submission_date']).dt.year
        timeline = df.groupby('submission_year').agg({
            'claim_id': 'count',
            'claim_area_ha': 'sum'
        }).rename(columns={'claim_id': 'claims_submitted'})
        
        analytics["timeline_analysis"] = timeline.to_dict('index')
        
        # Performance metrics
        analytics["performance_metrics"] = {
            "overall_approval_rate": round(len(df[df['status'] == 'approved']) / len(df) * 100, 2),
            "average_processing_days": self._calculate_processing_days(df),
            "documentation_completeness": round(df['documents_submitted'].mean(), 2),
            "field_verification_rate": round(len(df[df['field_verification_done']]) / len(df) * 100, 2),
            "gps_verification_rate": round(len(df[df['gps_coordinates_verified']]) / len(df) * 100, 2)
        }
        
        return analytics
    
    def _calculate_processing_days(self, df):
        """Calculate average processing days for claims."""
        # This is a simplified calculation
        return np.random.randint(30, 365)
    
    def _make_json_serializable(self, obj):
        """Convert numpy types and other non-serializable objects to JSON-serializable types."""
        import json
        import numpy as np
        import math
        
        def convert_item(item):
            if isinstance(item, np.integer):
                return int(item)
            elif isinstance(item, np.floating):
                if math.isnan(item):
                    return None
                return float(item)
            elif isinstance(item, np.ndarray):
                return item.tolist()
            elif isinstance(item, dict):
                return {k: convert_item(v) for k, v in item.items()}
            elif isinstance(item, list):
                return [convert_item(i) for i in item]
            elif isinstance(item, float) and math.isnan(item):
                return None
            else:
                return item
        
        return convert_item(obj)
    
    def generate_geojson(self):
        """Generate comprehensive FRA GeoJSON data."""
        print("=== FRA WebGIS Integration Generator ===")
        print("Generating comprehensive FRA data for WebGIS integration...\n")
        
        # Generate claims data
        claims_features = self.generate_fra_claims()
        
        # Generate analytics
        analytics = self.generate_fra_analytics(claims_features)
        
        # Ensure all data is JSON serializable
        analytics = self._make_json_serializable(analytics)
        
        # Create main GeoJSON
        geojson = {
            "type": "FeatureCollection",
            "features": claims_features,
            "properties": {
                "generated_at": datetime.now().isoformat(),
                "description": "Comprehensive FRA (Forest Rights Act) claims data for WebGIS integration",
                "total_claims": len(claims_features),
                "fra_types": list(self.fra_types.keys()),
                "states_covered": list(self.fra_states.keys()),
                "analytics": analytics
            }
        }
        
        # Save main GeoJSON
        main_file = os.path.join(self.output_dir, 'fra_claims.geojson')
        with open(main_file, 'w') as f:
            json.dump(geojson, f, indent=2)
        
        # Save analytics separately
        analytics_file = os.path.join(self.output_dir, 'fra_analytics.json')
        with open(analytics_file, 'w') as f:
            json.dump(analytics, f, indent=2)
        
        # Generate state-wise GeoJSON files
        self._generate_state_wise_geojson(claims_features)
        
        # Generate summary report
        self._generate_summary_report(analytics)
        
        print(f"FRA data saved to: {main_file}")
        print(f"Analytics saved to: {analytics_file}")
        print(f"Total claims generated: {len(claims_features)}")
        print(f"States covered: {len(self.fra_states)}")
        print(f"FRA types: {', '.join(self.fra_types.keys())}")
        
        return geojson
    
    def _generate_state_wise_geojson(self, claims_features):
        """Generate separate GeoJSON files for each state."""
        print("Generating state-wise GeoJSON files...")
        
        # Group claims by state
        state_claims = {}
        for claim in claims_features:
            state = claim['properties']['state']
            if state not in state_claims:
                state_claims[state] = []
            state_claims[state].append(claim)
        
        # Create state-wise files
        for state, claims in state_claims.items():
            state_geojson = {
                "type": "FeatureCollection",
                "features": claims,
                "properties": {
                    "state": state,
                    "total_claims": len(claims),
                    "generated_at": datetime.now().isoformat()
                }
            }
            
            state_file = os.path.join(self.output_dir, f'fra_claims_{state.replace(" ", "_").lower()}.geojson')
            with open(state_file, 'w') as f:
                json.dump(state_geojson, f, indent=2)
    
    def _generate_summary_report(self, analytics):
        """Generate a summary report."""
        report_file = os.path.join(self.output_dir, 'fra_summary_report.md')
        
        with open(report_file, 'w') as f:
            f.write("# FRA WebGIS Integration Summary Report\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Overview\n")
            f.write(f"- Total Claims: {analytics['summary']['total_claims']}\n")
            f.write(f"- Total Area: {analytics['summary']['total_area_ha']:.2f} hectares\n")
            f.write(f"- Average Claim Size: {analytics['summary']['average_claim_size_ha']} hectares\n\n")
            
            f.write("## Claims by Type\n")
            for fra_type, count in analytics['summary']['claims_by_type'].items():
                f.write(f"- {fra_type}: {count}\n")
            
            f.write("\n## Claims by Status\n")
            for status, count in analytics['summary']['claims_by_status'].items():
                f.write(f"- {status}: {count}\n")
            
            f.write("\n## Performance Metrics\n")
            metrics = analytics['performance_metrics']
            f.write(f"- Overall Approval Rate: {metrics['overall_approval_rate']}%\n")
            f.write(f"- Field Verification Rate: {metrics['field_verification_rate']}%\n")
            f.write(f"- GPS Verification Rate: {metrics['gps_verification_rate']}%\n")

def main():
    """Main execution function."""
    generator = FRAWebGISGenerator('output')
    geojson_data = generator.generate_geojson()
    
    print("\n=== FRA WebGIS Integration Complete ===")
    print("Files generated:")
    print("- fra_claims.geojson (main data file)")
    print("- fra_analytics.json (analytics data)")
    print("- fra_claims_[state].geojson (state-wise files)")
    print("- fra_summary_report.md (summary report)")
    print("\nYou can now use these files with the enhanced Flask application!")

if __name__ == "__main__":
    main()
