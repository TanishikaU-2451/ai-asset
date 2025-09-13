#!/usr/bin/env python3
"""
Test script to verify the AI Land Use Classification MVP setup
"""

import os
import sys
import json
import subprocess

def test_python_version():
    """Test Python version compatibility."""
    print("Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} is not compatible (need 3.8+)")
        return False

def test_dependencies():
    """Test if required packages are installed."""
    print("\nTesting dependencies...")
    
    required_packages = [
        'flask', 'scikit-learn', 'rasterio', 'geopandas', 
        'numpy', 'pandas', 'matplotlib', 'folium'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def test_directory_structure():
    """Test if required directories exist."""
    print("\nTesting directory structure...")
    
    required_dirs = ['templates', 'static', 'scripts', 'output', 'data']
    missing_dirs = []
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✓ {directory}/")
        else:
            print(f"✗ {directory}/ (missing)")
            missing_dirs.append(directory)
    
    if missing_dirs:
        print(f"\nMissing directories: {', '.join(missing_dirs)}")
        return False
    
    return True

def test_files():
    """Test if required files exist."""
    print("\nTesting required files...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'templates/index.html',
        'static/style.css',
        'static/script.js',
        'scripts/train_and_classify.py',
        'scripts/generate_sample_data.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (missing)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\nMissing files: {', '.join(missing_files)}")
        return False
    
    return True

def test_sample_data():
    """Test if sample data can be generated."""
    print("\nTesting sample data generation...")
    
    try:
        # Run the sample data generator
        result = subprocess.run(
            [sys.executable, 'scripts/generate_sample_data.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✓ Sample data generated successfully")
            
            # Check if output file exists
            if os.path.exists('output/assets.geojson'):
                print("✓ GeoJSON file created")
                
                # Validate JSON structure
                with open('output/assets.geojson', 'r') as f:
                    data = json.load(f)
                
                if 'features' in data and len(data['features']) > 0:
                    print(f"✓ GeoJSON contains {len(data['features'])} features")
                    return True
                else:
                    print("✗ GeoJSON file is empty or invalid")
                    return False
            else:
                print("✗ GeoJSON file not created")
                return False
        else:
            print(f"✗ Sample data generation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing sample data: {e}")
        return False

def test_flask_app():
    """Test if Flask app can start (briefly)."""
    print("\nTesting Flask app...")
    
    try:
        # Import the Flask app
        from app import app
        
        # Test if app can be created
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("✓ Flask app responds to requests")
                return True
            else:
                print(f"✗ Flask app returned status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"✗ Flask app test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=== AI Land Use Classification MVP - Setup Test ===\n")
    
    tests = [
        ("Python Version", test_python_version),
        ("Dependencies", test_dependencies),
        ("Directory Structure", test_directory_structure),
        ("Required Files", test_files),
        ("Sample Data Generation", test_sample_data),
        ("Flask App", test_flask_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_name} test failed with error: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run: python app.py")
        print("2. Open: http://127.0.0.1:5000")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    exit(main())
