#!/usr/bin/env python3
"""
AI Land Use Classification MVP
Phase 2: AI Model Training & Classification

This script trains a Random Forest classifier on satellite imagery
and classifies land use into Water, Forest, and Agriculture.
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

class LandUseClassifier:
    def __init__(self, satellite_image_path, training_data_dir, output_dir):
        self.satellite_image_path = satellite_image_path
        self.training_data_dir = training_data_dir
        self.output_dir = output_dir
        self.model = None
        self.class_mapping = {
            'water': 1,
            'forest': 2,
            'agriculture': 3
        }
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def load_training_data(self):
        """Load training polygons from shapefiles and extract pixel values."""
        print("Loading training data...")
        
        training_data = []
        training_labels = []
        
        for class_name, class_id in self.class_mapping.items():
            shapefile_path = os.path.join(self.training_data_dir, f"{class_name}_training.shp")
            
            if not os.path.exists(shapefile_path):
                print(f"Warning: {shapefile_path} not found. Skipping {class_name} class.")
                continue
            
            # Load shapefile
            gdf = gpd.read_file(shapefile_path)
            print(f"Loaded {len(gdf)} {class_name} training polygons")
            
            # Load satellite image
            with rasterio.open(self.satellite_image_path) as src:
                # Extract pixel values for each polygon
                for idx, geom in enumerate(gdf.geometry):
                    try:
                        # Create a mask for the polygon
                        mask = rasterio.features.geometry_mask(
                            [geom], 
                            out_shape=src.shape, 
                            transform=src.transform, 
                            invert=True
                        )
                        
                        # Extract pixel values where mask is True
                        for band_idx in range(src.count):
                            band_data = src.read(band_idx + 1)
                            pixel_values = band_data[mask]
                            
                            if len(pixel_values) > 0:
                                # For each pixel, create a feature vector with all bands
                                if band_idx == 0:
                                    feature_vector = pixel_values.reshape(-1, 1)
                                else:
                                    feature_vector = np.column_stack([
                                        feature_vector, 
                                        pixel_values.reshape(-1, 1)
                                    ])
                        
                        # Add labels for all pixels in this polygon
                        labels = np.full(len(pixel_values), class_id)
                        
                        training_data.append(feature_vector)
                        training_labels.extend(labels)
                        
                    except Exception as e:
                        print(f"Error processing polygon {idx} in {class_name}: {e}")
                        continue
        
        if not training_data:
            raise ValueError("No training data found. Please check your shapefiles.")
        
        # Combine all training data
        X = np.vstack(training_data)
        y = np.array(training_labels)
        
        print(f"Total training samples: {len(X)}")
        print(f"Feature dimensions: {X.shape[1]}")
        print(f"Class distribution: {np.bincount(y)}")
        
        return X, y
    
    def train_model(self, X, y):
        """Train Random Forest classifier."""
        print("Training Random Forest classifier...")
        
        # Split data for validation
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model accuracy: {accuracy:.3f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, 
                                  target_names=list(self.class_mapping.keys())))
        
        # Save model
        model_path = os.path.join(self.output_dir, 'land_classifier.pkl')
        joblib.dump(self.model, model_path)
        print(f"Model saved to: {model_path}")
        
        return accuracy
    
    def classify_image(self):
        """Classify the entire satellite image."""
        print("Classifying satellite image...")
        
        with rasterio.open(self.satellite_image_path) as src:
            # Read all bands
            image_data = src.read()
            
            # Reshape for classification (pixels x bands)
            original_shape = image_data.shape[1:]  # Height, Width
            image_2d = image_data.reshape(image_data.shape[0], -1).T
            
            print(f"Classifying {len(image_2d)} pixels...")
            
            # Classify in batches to manage memory
            batch_size = 10000
            predictions = []
            
            for i in range(0, len(image_2d), batch_size):
                batch = image_2d[i:i+batch_size]
                batch_pred = self.model.predict(batch)
                predictions.extend(batch_pred)
                
                if (i // batch_size) % 10 == 0:
                    print(f"Processed {i}/{len(image_2d)} pixels")
            
            # Reshape predictions back to image shape
            classified_image = np.array(predictions).reshape(original_shape)
            
            # Save classified raster
            output_path = os.path.join(self.output_dir, 'classified_map.tif')
            with rasterio.open(
                output_path, 'w',
                driver='GTiff',
                height=classified_image.shape[0],
                width=classified_image.shape[1],
                count=1,
                dtype=classified_image.dtype,
                crs=src.crs,
                transform=src.transform
            ) as dst:
                dst.write(classified_image, 1)
            
            print(f"Classified image saved to: {output_path}")
            
            return classified_image, src.crs, src.transform
    
    def raster_to_geojson(self, classified_image, crs, transform):
        """Convert classified raster to GeoJSON polygons."""
        print("Converting raster to GeoJSON...")
        
        # Create a mask for each class
        features = []
        
        for class_name, class_id in self.class_mapping.items():
            print(f"Processing {class_name} class...")
            
            # Create binary mask for this class
            mask = (classified_image == class_id)
            
            if not np.any(mask):
                print(f"No {class_name} pixels found, skipping...")
                continue
            
            # Convert raster to vector
            results = (
                {'properties': {'class': class_name, 'class_id': class_id}, 'geometry': s}
                for i, (s, v) in enumerate(
                    shapes(mask.astype(np.uint8), mask=mask, transform=transform)
                )
            )
            
            # Add to features list
            features.extend(list(results))
        
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame.from_features(features, crs=crs)
        
        # Simplify geometries to reduce file size
        gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.0001)
        
        # Save as GeoJSON
        geojson_path = os.path.join(self.output_dir, 'assets.geojson')
        gdf.to_file(geojson_path, driver='GeoJSON')
        
        print(f"GeoJSON saved to: {geojson_path}")
        print(f"Total features: {len(gdf)}")
        
        return geojson_path

def main():
    """Main execution function."""
    print("=== AI Land Use Classification MVP ===")
    print("Phase 2: AI Model Training & Classification\n")
    
    # Configuration
    satellite_image_path = "data/sentinel2_image.tif"
    training_data_dir = "data/training"
    output_dir = "output"
    
    # Check if satellite image exists
    if not os.path.exists(satellite_image_path):
        print(f"Error: Satellite image not found at {satellite_image_path}")
        print("Please download a Sentinel-2 image and place it in the data/ directory")
        return
    
    # Check if training data exists
    if not os.path.exists(training_data_dir):
        print(f"Error: Training data directory not found at {training_data_dir}")
        print("Please create training shapefiles using QGIS (see Phase 1 instructions)")
        return
    
    try:
        # Initialize classifier
        classifier = LandUseClassifier(satellite_image_path, training_data_dir, output_dir)
        
        # Load training data
        X, y = classifier.load_training_data()
        
        # Train model
        accuracy = classifier.train_model(X, y)
        
        # Classify image
        classified_image, crs, transform = classifier.classify_image()
        
        # Convert to GeoJSON
        geojson_path = classifier.raster_to_geojson(classified_image, crs, transform)
        
        print("\n=== Classification Complete ===")
        print(f"Model accuracy: {accuracy:.3f}")
        print(f"Output files:")
        print(f"  - Classified raster: {os.path.join(output_dir, 'classified_map.tif')}")
        print(f"  - GeoJSON: {geojson_path}")
        print(f"  - Model: {os.path.join(output_dir, 'land_classifier.pkl')}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
