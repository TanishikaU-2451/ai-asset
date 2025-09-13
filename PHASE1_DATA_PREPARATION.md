# Phase 1: Data Preparation Guide

This guide walks you through preparing satellite imagery and training data for the AI Land Use Classification MVP.

## Overview

Phase 1 involves:
1. Downloading Sentinel-2 satellite imagery
2. Creating training data using QGIS
3. Preparing data for the AI model

## Step 1: Download Sentinel-2 Imagery

### Option A: Copernicus Open Access Hub (Recommended)

1. **Create Account**: Go to [https://scihub.copernicus.eu/](https://scihub.copernicus.eu/)
2. **Register**: Create a free account
3. **Search for Data**:
   - Select "Sentinel-2" mission
   - Choose your area of interest (e.g., Adilabad district, Telangana)
   - Set date range (last 6 months for cloud-free images)
   - Select "L2A" products (atmospherically corrected)
   - Filter by cloud coverage (< 10%)

4. **Download**: Download the L2A product (usually 1-2 GB)

### Option B: Google Earth Engine (Alternative)

If you have access to Google Earth Engine, you can download Sentinel-2 data directly:

```javascript
// Google Earth Engine script
var geometry = ee.Geometry.Rectangle([78.5, 17.5, 80.0, 19.0]); // Adilabad area
var collection = ee.ImageCollection('COPERNICUS/S2_SR')
  .filterDate('2023-01-01', '2023-12-31')
  .filterBounds(geometry)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))
  .first();

Export.image.toDrive({
  image: collection,
  description: 'sentinel2_adilabad',
  folder: 'ai-asset',
  region: geometry,
  scale: 10,
  maxPixels: 1e9
});
```

## Step 2: Prepare Data in QGIS

### Install QGIS

1. Download QGIS from [https://qgis.org/](https://qgis.org/)
2. Install the latest LTR (Long Term Release) version

### Load Satellite Imagery

1. **Open QGIS**
2. **Add Raster Layer**: 
   - Go to Layer → Add Layer → Add Raster Layer
   - Navigate to your downloaded Sentinel-2 image
   - Select the main image file (usually ends with .tif)

3. **Configure Bands**:
   - Right-click the layer → Properties
   - Go to Symbology tab
   - Set Red: Band 4, Green: Band 3, Blue: Band 2 (RGB composite)
   - Adjust contrast if needed

### Create Training Data

1. **Create New Shapefiles**:
   - Right-click in Layers panel → New → New Shapefile Layer
   - Create three shapefiles:
     - `water_training.shp` (Polygon, CRS: EPSG:4326)
     - `forest_training.shp` (Polygon, CRS: EPSG:4326)
     - `agri_training.shp` (Polygon, CRS: EPSG:4326)

2. **Add Training Polygons**:
   - Select each shapefile and toggle editing mode
   - Use the "Add Polygon Feature" tool
   - Draw polygons over clear examples of each land use type:
     - **Water**: Rivers, lakes, ponds (blue/black in image)
     - **Forest**: Dense vegetation areas (dark green/red in image)
     - **Agriculture**: Farm fields, crop areas (light green/brown in image)

3. **Save Training Data**:
   - Save each shapefile in the `data/training/` directory
   - Ensure all files are in the same coordinate system (EPSG:4326)

### Training Data Tips

- **Quality over Quantity**: 15-20 polygons per class is sufficient for MVP
- **Representative Samples**: Choose polygons that clearly represent each class
- **Avoid Mixed Pixels**: Stay away from edges and transition zones
- **Consistent Size**: Keep polygon sizes similar (not too small, not too large)

## Step 3: Prepare Data Structure

Your `data/` directory should look like this:

```
data/
├── sentinel2_image.tif          # Main satellite image
└── training/
    ├── water_training.shp       # Water training polygons
    ├── water_training.shx       # Shapefile index
    ├── water_training.dbf       # Shapefile database
    ├── water_training.prj       # Projection file
    ├── forest_training.shp      # Forest training polygons
    ├── forest_training.shx
    ├── forest_training.dbf
    ├── forest_training.prj
    ├── agri_training.shp        # Agriculture training polygons
    ├── agri_training.shx
    ├── agri_training.dbf
    └── agri_training.prj
```

## Step 4: Verify Data

1. **Check Image Quality**:
   - Ensure the image covers your area of interest
   - Verify it's cloud-free in your training areas
   - Check that all bands are present

2. **Validate Training Data**:
   - Open each shapefile in QGIS
   - Verify polygons are correctly placed
   - Check that attributes are properly set
   - Ensure all files use the same CRS

## Troubleshooting

### Common Issues

1. **Coordinate System Mismatch**:
   - Ensure all data uses EPSG:4326 (WGS84)
   - Use QGIS to reproject if needed

2. **Missing Bands**:
   - Some Sentinel-2 downloads may be incomplete
   - Re-download if necessary

3. **Large File Sizes**:
   - Consider cropping the image to your area of interest
   - Use QGIS to clip the raster

### Getting Help

- QGIS Documentation: [https://docs.qgis.org/](https://docs.qgis.org/)
- Sentinel-2 User Guide: [https://sentinel.esa.int/web/sentinel/user-guides/sentinel-2-msi](https://sentinel.esa.int/web/sentinel/user-guides/sentinel-2-msi)
- Project Issues: Check the project README.md

## Next Steps

Once you have completed Phase 1:

1. **Run Setup**: `python setup.py`
2. **Train Model**: `python scripts/train_and_classify.py`
3. **Start Web Server**: `python app.py`
4. **View Results**: Open http://127.0.0.1:5000

## Sample Data

If you want to test the system without real data, you can use the sample data generator:

```bash
python scripts/generate_sample_data.py
```

This will create sample GeoJSON data for testing the web interface.
