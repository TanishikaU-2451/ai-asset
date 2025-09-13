#!/usr/bin/env python3
"""
Sample Data Generator for AI Land Use Classification MVP

This script generates sample GeoJSON data for testing the web interface
when real satellite imagery and training data are not available.
"""

import json
import random
import os
from datetime import datetime

def generate_sample_geojson():
    """Generate sample GeoJSON data with land use classifications."""
    
    # Sample area around Telangana, India
    center_lat = 18.1124
    center_lon = 79.0193
    
    features = []
    
    # Generate random polygons for each class
    classes = ['water', 'forest', 'agriculture']
    class_colors = {
        'water': '#0066cc',
        'forest': '#00aa00', 
        'agriculture': '#ffaa00'
    }
    
    for i, class_name in enumerate(classes):
        # Generate 5-10 random polygons per class
        num_polygons = random.randint(5, 10)
        
        for j in range(num_polygons):
            # Create a random polygon around the center
            base_lat = center_lat + random.uniform(-0.5, 0.5)
            base_lon = center_lon + random.uniform(-0.5, 0.5)
            
            # Create a simple square polygon
            size = random.uniform(0.01, 0.05)
            coordinates = [[
                [base_lon - size, base_lat - size],
                [base_lon + size, base_lat - size],
                [base_lon + size, base_lat + size],
                [base_lon - size, base_lat + size],
                [base_lon - size, base_lat - size]
            ]]
            
            feature = {
                "type": "Feature",
                "properties": {
                    "class": class_name,
                    "class_id": i + 1,
                    "area_km2": round(random.uniform(1, 50), 2),
                    "confidence": round(random.uniform(0.7, 0.95), 2)
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": coordinates
                }
            }
            
            features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "generated_at": datetime.now().isoformat(),
            "description": "Sample land use classification data for MVP testing",
            "total_features": len(features),
            "classes": list(set(f["properties"]["class"] for f in features))
        }
    }
    
    return geojson

def main():
    """Generate sample data and save to output directory."""
    print("=== Sample Data Generator ===")
    print("Generating sample GeoJSON data for MVP testing...")
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Generate sample data
    geojson_data = generate_sample_geojson()
    
    # Save to file
    output_path = 'output/assets.geojson'
    with open(output_path, 'w') as f:
        json.dump(geojson_data, f, indent=2)
    
    print(f"Sample data saved to: {output_path}")
    print(f"Total features: {len(geojson_data['features'])}")
    print(f"Classes: {', '.join(geojson_data['properties']['classes'])}")
    print("\nYou can now start the Flask server to view the sample data:")
    print("python app.py")

if __name__ == "__main__":
    main()
