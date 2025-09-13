#!/usr/bin/env python3
"""
Enhanced AI Land Use Classification for India
Extended MVP with comprehensive coverage and accurate classification
"""

import os
import sys
import numpy as np
import pandas as pd
import rasterio
import geopandas as gpd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import json
from rasterio.features import shapes
from rasterio.transform import from_bounds
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class IndiaLandUseClassifier:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.model = None
        
        # Enhanced class mapping for India
        self.class_mapping = {
            'water': 1,
            'forest_dense': 2,
            'forest_open': 3,
            'agriculture_irrigated': 4,
            'agriculture_rainfed': 5,
            'urban': 6,
            'grassland': 7,
            'wasteland': 8,
            'wetland': 9,
            'mangrove': 10
        }
        
        # State and district boundaries
        self.india_bounds = {
            'north': 37.1,
            'south': 6.4,
            'east': 97.4,
            'west': 68.1
        }
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_india_sample_data(self):
        """Generate comprehensive sample data for India with realistic distribution."""
        print("Generating India-wide sample data...")
        
        features = []
        
        # State-wise data distribution (approximate)
        states_data = {
            'Andhra Pradesh': {'lat': 15.9129, 'lon': 79.7400, 'scale': 0.8},
            'Arunachal Pradesh': {'lat': 28.2180, 'lon': 94.7278, 'scale': 0.6},
            'Assam': {'lat': 26.2006, 'lon': 92.9376, 'scale': 0.7},
            'Bihar': {'lat': 25.0961, 'lon': 85.3131, 'scale': 0.6},
            'Chhattisgarh': {'lat': 21.2787, 'lon': 81.8661, 'scale': 0.7},
            'Delhi': {'lat': 28.7041, 'lon': 77.1025, 'scale': 0.3},
            'Gujarat': {'lat': 23.0225, 'lon': 72.5714, 'scale': 0.8},
            'Haryana': {'lat': 29.0588, 'lon': 76.0856, 'scale': 0.5},
            'Himachal Pradesh': {'lat': 31.1048, 'lon': 77.1734, 'scale': 0.6},
            'Jharkhand': {'lat': 23.6102, 'lon': 85.2799, 'scale': 0.6},
            'Karnataka': {'lat': 15.3173, 'lon': 75.7139, 'scale': 0.8},
            'Kerala': {'lat': 10.8505, 'lon': 76.2711, 'scale': 0.5},
            'Madhya Pradesh': {'lat': 22.9734, 'lon': 78.6569, 'scale': 0.9},
            'Maharashtra': {'lat': 19.7515, 'lon': 75.7139, 'scale': 0.9},
            'Manipur': {'lat': 24.6637, 'lon': 93.9063, 'scale': 0.4},
            'Meghalaya': {'lat': 25.4670, 'lon': 91.3662, 'scale': 0.4},
            'Mizoram': {'lat': 23.1645, 'lon': 92.9376, 'scale': 0.4},
            'Nagaland': {'lat': 26.1584, 'lon': 94.5624, 'scale': 0.4},
            'Odisha': {'lat': 20.9517, 'lon': 85.0985, 'scale': 0.7},
            'Punjab': {'lat': 31.1471, 'lon': 75.3412, 'scale': 0.5},
            'Rajasthan': {'lat': 27.0238, 'lon': 74.2179, 'scale': 0.9},
            'Sikkim': {'lat': 27.5330, 'lon': 88.5122, 'scale': 0.3},
            'Tamil Nadu': {'lat': 11.1271, 'lon': 78.6569, 'scale': 0.7},
            'Telangana': {'lat': 18.1124, 'lon': 79.0193, 'scale': 0.6},
            'Tripura': {'lat': 23.9408, 'lon': 91.9882, 'scale': 0.4},
            'Uttar Pradesh': {'lat': 26.8467, 'lon': 80.9462, 'scale': 0.9},
            'Uttarakhand': {'lat': 30.0668, 'lon': 79.0193, 'scale': 0.5},
            'West Bengal': {'lat': 22.9868, 'lon': 87.8550, 'scale': 0.7}
        }
        
        # Class distribution based on India's land use patterns
        class_distribution = {
            'water': 0.08,
            'forest_dense': 0.15,
            'forest_open': 0.10,
            'agriculture_irrigated': 0.25,
            'agriculture_rainfed': 0.20,
            'urban': 0.05,
            'grassland': 0.08,
            'wasteland': 0.06,
            'wetland': 0.02,
            'mangrove': 0.01
        }
        
        for state_name, state_info in states_data.items():
            print(f"Generating data for {state_name}...")
            
            for class_name, class_id in self.class_mapping.items():
                # Calculate number of features based on distribution and state size
                num_features = max(1, int(class_distribution[class_name] * state_info['scale'] * 20))
                
                for i in range(num_features):
                    # Create realistic polygon around state center
                    base_lat = state_info['lat'] + np.random.uniform(-state_info['scale'], state_info['scale'])
                    base_lon = state_info['lon'] + np.random.uniform(-state_info['scale'], state_info['scale'])
                    
                    # Ensure coordinates are within India bounds
                    base_lat = max(self.india_bounds['south'], min(self.india_bounds['north'], base_lat))
                    base_lon = max(self.india_bounds['west'], min(self.india_bounds['east'], base_lon))
                    
                    # Create polygon with realistic size
                    size = np.random.uniform(0.01, 0.1) * state_info['scale']
                    
                    # Different shapes for different classes
                    if class_name in ['water', 'wetland']:
                        # Water bodies are more irregular
                        coords = self._create_irregular_polygon(base_lat, base_lon, size)
                    elif class_name in ['urban']:
                        # Urban areas are more rectangular
                        coords = self._create_rectangular_polygon(base_lat, base_lon, size)
                    else:
                        # Natural areas are more organic
                        coords = self._create_organic_polygon(base_lat, base_lon, size)
                    
                    feature = {
                        "type": "Feature",
                        "properties": {
                            "class": class_name,
                            "class_id": class_id,
                            "state": state_name,
                            "area_km2": round(np.random.uniform(1, 100), 2),
                            "confidence": round(np.random.uniform(0.75, 0.95), 2),
                            "population": np.random.randint(0, 10000) if class_name == 'urban' else 0,
                            "forest_type": self._get_forest_type(class_name),
                            "crop_type": self._get_crop_type(class_name),
                            "tribal_area": bool(np.random.choice([True, False], p=[0.3, 0.7]))
                        },
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [coords]
                        }
                    }
                    
                    features.append(feature)
        
        # Add FRA (Forest Rights Act) specific data
        fra_features = self._generate_fra_data()
        features.extend(fra_features)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features,
            "properties": {
                "generated_at": pd.Timestamp.now().isoformat(),
                "description": "Enhanced India land use classification with FRA data",
                "total_features": len(features),
                "classes": list(self.class_mapping.keys()),
                "states": list(states_data.keys()),
                "coverage": "India"
            }
        }
        
        return geojson
    
    def _create_irregular_polygon(self, lat, lon, size):
        """Create irregular polygon for water bodies."""
        angles = np.linspace(0, 2*np.pi, 8)
        radius = size * np.random.uniform(0.5, 1.5, len(angles))
        coords = []
        for angle, r in zip(angles, radius):
            x = lon + r * np.cos(angle)
            y = lat + r * np.sin(angle)
            coords.append([x, y])
        coords.append(coords[0])  # Close polygon
        return coords
    
    def _create_rectangular_polygon(self, lat, lon, size):
        """Create rectangular polygon for urban areas."""
        half_size = size / 2
        return [
            [lon - half_size, lat - half_size],
            [lon + half_size, lat - half_size],
            [lon + half_size, lat + half_size],
            [lon - half_size, lat + half_size],
            [lon - half_size, lat - half_size]
        ]
    
    def _create_organic_polygon(self, lat, lon, size):
        """Create organic polygon for natural areas."""
        angles = np.linspace(0, 2*np.pi, 12)
        radius = size * np.random.uniform(0.3, 1.0, len(angles))
        coords = []
        for angle, r in zip(angles, radius):
            x = lon + r * np.cos(angle)
            y = lat + r * np.sin(angle)
            coords.append([x, y])
        coords.append(coords[0])  # Close polygon
        return coords
    
    def _get_forest_type(self, class_name):
        """Get forest type based on class."""
        if class_name == 'forest_dense':
            return np.random.choice(['Tropical Evergreen', 'Tropical Semi-Evergreen', 'Tropical Moist Deciduous'])
        elif class_name == 'forest_open':
            return np.random.choice(['Tropical Dry Deciduous', 'Tropical Thorn', 'Subtropical Pine'])
        elif class_name == 'mangrove':
            return 'Mangrove'
        else:
            return None
    
    def _get_crop_type(self, class_name):
        """Get crop type based on class."""
        if class_name == 'agriculture_irrigated':
            return np.random.choice(['Rice', 'Wheat', 'Sugarcane', 'Cotton', 'Vegetables'])
        elif class_name == 'agriculture_rainfed':
            return np.random.choice(['Millets', 'Pulses', 'Oilseeds', 'Maize'])
        else:
            return None
    
    def _generate_fra_data(self):
        """Generate Forest Rights Act specific data."""
        fra_features = []
        
        # FRA categories
        fra_categories = {
            'individual_forest_rights': 0.4,
            'community_forest_rights': 0.3,
            'community_forest_resource_rights': 0.2,
            'habitat_rights': 0.1
        }
        
        # States with significant tribal populations
        tribal_states = ['Odisha', 'Chhattisgarh', 'Jharkhand', 'Madhya Pradesh', 'Maharashtra', 
                        'Andhra Pradesh', 'Telangana', 'Gujarat', 'Rajasthan', 'West Bengal']
        
        for state in tribal_states:
            for fra_type, probability in fra_categories.items():
                if np.random.random() < probability:
                    # Generate FRA claim area
                    base_lat = np.random.uniform(15, 25)  # Central India
                    base_lon = np.random.uniform(75, 85)
                    
                    size = np.random.uniform(0.05, 0.2)
                    coords = self._create_organic_polygon(base_lat, base_lon, size)
                    
                    feature = {
                        "type": "Feature",
                        "properties": {
                            "class": "fra_area",
                            "class_id": 11,
                            "state": state,
                            "fra_type": fra_type,
                            "claim_status": np.random.choice(['pending', 'approved', 'rejected'], p=[0.4, 0.5, 0.1]),
                            "claim_area_ha": round(np.random.uniform(1, 100), 2),
                            "tribal_community": np.random.choice(['Gond', 'Santal', 'Munda', 'Oraon', 'Ho', 'Kurukh']),
                            "village": f"Village_{np.random.randint(1, 1000)}",
                            "block": f"Block_{np.random.randint(1, 50)}",
                            "district": f"District_{np.random.randint(1, 20)}"
                        },
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [coords]
                        }
                    }
                    
                    fra_features.append(feature)
        
        return fra_features

def main():
    """Generate enhanced India land use data."""
    print("=== Enhanced India Land Use Classification ===")
    print("Generating comprehensive sample data for India...\n")
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    # Initialize classifier
    classifier = IndiaLandUseClassifier('output')
    
    # Generate sample data
    geojson_data = classifier.generate_india_sample_data()
    
    # Save to file
    output_path = 'output/india_assets.geojson'
    with open(output_path, 'w') as f:
        json.dump(geojson_data, f, indent=2)
    
    print(f"Enhanced data saved to: {output_path}")
    print(f"Total features: {len(geojson_data['features'])}")
    print(f"Classes: {', '.join(geojson_data['properties']['classes'])}")
    print(f"States covered: {len(geojson_data['properties']['states'])}")
    
    # Generate summary statistics
    df = pd.DataFrame([f['properties'] for f in geojson_data['features']])
    
    print("\n=== Summary Statistics ===")
    print("Class distribution:")
    print(df['class'].value_counts())
    
    print("\nState distribution:")
    print(df['state'].value_counts().head(10))
    
    print("\nFRA data:")
    fra_data = df[df['class'] == 'fra_area']
    if len(fra_data) > 0:
        print(f"Total FRA claims: {len(fra_data)}")
        print("FRA type distribution:")
        print(fra_data['fra_type'].value_counts())
        print("Claim status distribution:")
        print(fra_data['claim_status'].value_counts())
    
    print("\n=== Data Generation Complete ===")
    print("You can now start the enhanced Flask server to view the data:")
    print("python app_enhanced.py")

if __name__ == "__main__":
    main()
