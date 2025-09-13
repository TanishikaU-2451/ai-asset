#!/usr/bin/env python3
"""
Setup script for AI Land Use Classification MVP

This script helps set up the project environment and dependencies.
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error in {description}: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✓ Python version {version.major}.{version.minor}.{version.micro} is compatible")
        return True

def install_dependencies():
    """Install Python dependencies."""
    print("\n=== Installing Dependencies ===")
    
    # Check if pip is available
    if not run_command("pip --version", "Checking pip availability"):
        print("✗ pip is not available. Please install pip first.")
        return False
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python packages"):
        return False
    
    return True

def create_directories():
    """Create necessary directories."""
    print("\n=== Creating Directories ===")
    
    directories = ['data', 'data/training', 'models', 'output', 'templates', 'static']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory already exists: {directory}")
    
    return True

def generate_sample_data():
    """Generate sample data for testing."""
    print("\n=== Generating Sample Data ===")
    
    if not run_command("python scripts/generate_sample_data.py", "Generating sample GeoJSON data"):
        return False
    
    return True

def main():
    """Main setup function."""
    print("=== AI Land Use Classification MVP Setup ===")
    print("Setting up the project environment...\n")
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create directories
    if not create_directories():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Generate sample data
    if not generate_sample_data():
        return 1
    
    print("\n=== Setup Complete ===")
    print("✓ All dependencies installed")
    print("✓ Project directories created")
    print("✓ Sample data generated")
    print("\nNext steps:")
    print("1. For real data: Download Sentinel-2 imagery and create training shapefiles in QGIS")
    print("2. Run classification: python scripts/train_and_classify.py")
    print("3. Start web server: python app.py")
    print("4. Open browser to: http://127.0.0.1:5000")
    
    return 0

if __name__ == "__main__":
    exit(main())
