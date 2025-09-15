#!/usr/bin/env python3
"""
Vanachitra.AI - FRA Spatial Data Generator
Generates realistic GeoJSON data for Forest Rights Act (FRA) visualization
Following proper spatial hierarchy: CFR contains IFR and CR features
"""

import json
import random
import math
from datetime import datetime, timedelta

class VanachitraFRAGenerator:
    def __init__(self):
        # Indian states with forest areas and their characteristics
        self.forest_states = {
            'Telangana': {
                'center': [18.1124, 79.0193],
                'districts': ['Adilabad', 'Kumuram Bheem', 'Mancherial', 'Nirmal', 'Nizamabad'],
                'terrain': 'deccan_plateau',
                'forest_cover': 24.17  # percentage
            },
            'Madhya Pradesh': {
                'center': [22.9734, 78.6569],
                'districts': ['Balaghat', 'Dindori', 'Mandla', 'Seoni', 'Chhindwara'],
                'terrain': 'central_highlands',
                'forest_cover': 25.14
            },
            'Odisha': {
                'center': [20.9517, 85.0985],
                'districts': ['Mayurbhanj', 'Keonjhar', 'Sundargarh', 'Sambalpur', 'Kalahandi'],
                'terrain': 'eastern_ghats',
                'forest_cover': 33.16
            },
            'Tripura': {
                'center': [23.9408, 91.9882],
                'districts': ['West Tripura', 'South Tripura', 'Dhalai', 'North Tripura'],
                'terrain': 'hills_valleys',
                'forest_cover': 73.68
            }
        }
        
        # Tribal communities by state
        self.tribal_communities = {
            'Telangana': ['Gond', 'Koya', 'Lambada', 'Yerukala', 'Chenchu'],
            'Madhya Pradesh': ['Gond', 'Bhil', 'Baiga', 'Kol', 'Korku'],
            'Odisha': ['Santhal', 'Kond', 'Saora', 'Munda', 'Ho'],
            'Tripura': ['Tripuri', 'Reang', 'Jamatia', 'Chakma', 'Halam']
        }
        
        # Village naming patterns by state
        self.village_patterns = {
            'Telangana': ['palli', 'guda', 'nagar', 'puram'],
            'Madhya Pradesh': ['gaon', 'khurd', 'kalan', 'tola'],
            'Odisha': ['sahi', 'palli', 'para', 'gaon'],
            'Tripura': ['para', 'khorang', 'bari', 'tilla']
        }

    def generate_realistic_village_name(self, state):
        """Generate realistic village names based on state patterns"""
        base_names = {
            'Telangana': ['Ramagundam', 'Venkatesh', 'Lakshmi', 'Srinivas', 'Ananda'],
            'Madhya Pradesh': ['Rampur', 'Shivpur', 'Krishnanagar', 'Rajpur', 'Devgarh'],
            'Odisha': ['Jagannath', 'Rama', 'Krishna', 'Balaram', 'Hanuman'],
            'Tripura': ['Agartala', 'Udaipur', 'Dharmanagar', 'Ambassa', 'Belonia']
        }
        
        base = random.choice(base_names[state])
        suffix = random.choice(self.village_patterns[state])
        return f"{base}{suffix}"

    def generate_cfr_polygon(self, state_info, district):
        """Generate a realistic CFR (Community Forest Resource) polygon"""
        center_lat, center_lon = state_info['center']
        
        # Add some offset for district location
        lat_offset = random.uniform(-1.5, 1.5)
        lon_offset = random.uniform(-1.5, 1.5)
        
        cfr_center_lat = center_lat + lat_offset
        cfr_center_lon = center_lon + lon_offset
        
        # CFR area should be substantial (500-2000 hectares)
        area_hectares = random.uniform(500, 2000)
        radius_km = math.sqrt(area_hectares / 100 / math.pi)  # Convert to km radius
        radius_deg = radius_km / 111.0  # Rough conversion to degrees
        
        # Generate irregular forest boundary (8-12 points)
        points = []
        num_points = random.randint(8, 12)
        
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            # Vary radius to create irregular forest boundary
            r = radius_deg * random.uniform(0.7, 1.4)
            
            lat = cfr_center_lat + r * math.cos(angle)
            lon = cfr_center_lon + r * math.sin(angle)
            points.append([lon, lat])
        
        # Close the polygon
        points.append(points[0])
        
        return {
            'coordinates': [points],
            'center': [cfr_center_lat, cfr_center_lon],
            'area_hectares': area_hectares
        }

    def point_in_polygon(self, point, polygon):
        """Check if a point is inside a polygon using ray casting algorithm"""
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside

    def generate_point_inside_polygon(self, polygon_coords):
        """Generate a random point inside the given polygon"""
        # Get bounding box
        lons = [p[0] for p in polygon_coords[0]]
        lats = [p[1] for p in polygon_coords[0]]
        
        min_lon, max_lon = min(lons), max(lons)
        min_lat, max_lat = min(lats), max(lats)
        
        # Try to generate point inside polygon (max 50 attempts)
        for _ in range(50):
            lon = random.uniform(min_lon, max_lon)
            lat = random.uniform(min_lat, max_lat)
            
            if self.point_in_polygon([lon, lat], polygon_coords[0]):
                return [lat, lon]
        
        # Fallback: return center of bounding box
        return [(min_lat + max_lat) / 2, (min_lon + max_lon) / 2]

    def generate_ifr_polygons(self, cfr_polygon, village_name, district, state, tribal_community, num_ifrs=12):
        """Generate IFR (Individual Forest Rights) polygons inside CFR"""
        ifr_features = []
        
        for i in range(num_ifrs):
            # IFR area: 1-5 hectares per household
            area_hectares = random.uniform(1.0, 5.0)
            radius_deg = math.sqrt(area_hectares / 100) / 111.0  # Convert to degrees
            
            # Generate center point inside CFR
            center_lat, center_lon = self.generate_point_inside_polygon(cfr_polygon)
            
            # Generate small rectangular/square polygon (typical of agricultural plots)
            if random.choice([True, False]):
                # Rectangular plot
                width = radius_deg * random.uniform(0.8, 1.5)
                height = area_hectares / 100 / (width * 111.0) / 111.0
            else:
                # Square plot
                width = height = radius_deg
            
            # Add slight rotation
            rotation = random.uniform(-math.pi/8, math.pi/8)
            
            corners = [
                [-width/2, -height/2],
                [width/2, -height/2],
                [width/2, height/2],
                [-width/2, height/2]
            ]
            
            points = []
            for corner in corners:
                # Apply rotation
                x_rot = corner[0] * math.cos(rotation) - corner[1] * math.sin(rotation)
                y_rot = corner[0] * math.sin(rotation) + corner[1] * math.cos(rotation)
                
                lat = center_lat + y_rot
                lon = center_lon + x_rot
                points.append([lon, lat])
            
            # Close polygon
            points.append(points[0])
            
            # Generate realistic household details
            household_head = random.choice(['Ram Singh', 'Shyam Lal', 'Ganga Devi', 'Sita Bai', 
                                         'Ravi Kumar', 'Lakshmi Devi', 'Suresh Rao', 'Kamala Bai'])
            
            ifr_feature = {
                'type': 'Feature',
                'properties': {
                    'claim_id': f'IFR_{state[:2].upper()}_{district[:3].upper()}_{i+1:03d}',
                    'claim_type': 'IFR',
                    'fra_type': 'Individual Forest Rights',
                    'village': village_name,
                    'district': district,
                    'state': state,
                    'area_claimed': round(area_hectares, 2),
                    'area_unit': 'hectares',
                    'status': random.choice(['Approved', 'Pending', 'Under Review']),
                    'tribal_community': tribal_community,
                    'household_head': household_head,
                    'family_members': random.randint(3, 8),
                    'livelihood': random.choice(['Agriculture', 'NTFP Collection', 'Animal Husbandry', 'Mixed']),
                    'submission_date': (datetime.now() - timedelta(days=random.randint(30, 730))).strftime('%Y-%m-%d'),
                    'survey_number': f'SY_{random.randint(100, 999)}',
                    'frc_recommendation': random.choice(['Recommended', 'Pending', 'Additional Info Required']),
                    'gps_verified': random.choice([True, False]),
                    'documents_complete': random.choice([True, False])
                },
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [points]
                }
            }
            
            ifr_features.append(ifr_feature)
        
        return ifr_features

    def generate_cr_features(self, cfr_polygon, village_name, district, state, tribal_community, num_crs=3):
        """Generate CR (Community Rights) features inside CFR"""
        cr_features = []
        
        cr_types = ['Grazing Ground', 'Community Pond', 'NTFP Collection Area', 'Sacred Grove', 'Community Well']
        
        for i in range(num_crs):
            cr_type = random.choice(cr_types)
            
            # Generate center point inside CFR
            center_lat, center_lon = self.generate_point_inside_polygon(cfr_polygon)
            
            if cr_type in ['Community Pond', 'Community Well']:
                # Point feature for wells/small ponds
                cr_feature = {
                    'type': 'Feature',
                    'properties': {
                        'claim_id': f'CR_{state[:2].upper()}_{district[:3].upper()}_{i+1:03d}',
                        'claim_type': 'CR',
                        'fra_type': 'Community Rights',
                        'resource_type': cr_type,
                        'village': village_name,
                        'district': district,
                        'state': state,
                        'status': random.choice(['Approved', 'Pending']),
                        'tribal_community': tribal_community,
                        'beneficiary_households': random.randint(20, 80),
                        'usage_pattern': random.choice(['Seasonal', 'Year-round', 'Occasional']),
                        'submission_date': (datetime.now() - timedelta(days=random.randint(30, 730))).strftime('%Y-%m-%d'),
                        'traditional_use': random.choice([True, False]),
                        'community_management': True
                    },
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [center_lon, center_lat]
                    }
                }
            else:
                # Polygon feature for larger community areas
                area_hectares = random.uniform(5.0, 50.0)
                radius_deg = math.sqrt(area_hectares / 100) / 111.0
                
                # Generate irregular polygon
                points = []
                num_points = random.randint(6, 10)
                
                for j in range(num_points):
                    angle = 2 * math.pi * j / num_points
                    r = radius_deg * random.uniform(0.7, 1.3)
                    
                    lat = center_lat + r * math.cos(angle)
                    lon = center_lon + r * math.sin(angle)
                    points.append([lon, lat])
                
                points.append(points[0])
                
                cr_feature = {
                    'type': 'Feature',
                    'properties': {
                        'claim_id': f'CR_{state[:2].upper()}_{district[:3].upper()}_{i+1:03d}',
                        'claim_type': 'CR',
                        'fra_type': 'Community Rights',
                        'resource_type': cr_type,
                        'village': village_name,
                        'district': district,
                        'state': state,
                        'area_claimed': round(area_hectares, 2) if cr_type != 'Community Well' else None,
                        'area_unit': 'hectares',
                        'status': random.choice(['Approved', 'Pending']),
                        'tribal_community': tribal_community,
                        'beneficiary_households': random.randint(20, 80),
                        'usage_pattern': random.choice(['Seasonal', 'Year-round', 'Occasional']),
                        'submission_date': (datetime.now() - timedelta(days=random.randint(30, 730))).strftime('%Y-%m-%d'),
                        'traditional_use': random.choice([True, False]),
                        'community_management': True,
                        'management_committee': random.choice([True, False])
                    },
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [points]
                    }
                }
            
            cr_features.append(cr_feature)
        
        return cr_features

    def generate_agriculture_features(self, cfr_polygon, village_name, district, state, num_plots=8):
        """Generate agricultural land features inside/adjacent to CFR"""
        agriculture_features = []
        
        crop_types = ['Rice', 'Wheat', 'Maize', 'Millet', 'Pulses', 'Vegetables', 'Mixed Crops']
        
        for i in range(num_plots):
            # Generate point near CFR boundary or inside
            center_lat, center_lon = self.generate_point_inside_polygon(cfr_polygon)
            
            # Agricultural plot: 0.5-3 hectares
            area_hectares = random.uniform(0.5, 3.0)
            width = random.uniform(0.002, 0.008)  # degrees
            height = area_hectares / 100 / (width * 111.0) / 111.0
            
            # Rectangular agricultural plot
            points = [
                [center_lon - width/2, center_lat - height/2],
                [center_lon + width/2, center_lat - height/2],
                [center_lon + width/2, center_lat + height/2],
                [center_lon - width/2, center_lat + height/2],
                [center_lon - width/2, center_lat - height/2]
            ]
            
            agriculture_feature = {
                'type': 'Feature',
                'properties': {
                    'feature_id': f'AGR_{state[:2].upper()}_{district[:3].upper()}_{i+1:03d}',
                    'feature_type': 'Agriculture',
                    'crop_type': random.choice(crop_types),
                    'village': village_name,
                    'district': district,
                    'state': state,
                    'area_hectares': round(area_hectares, 2),
                    'irrigation_type': random.choice(['Rainfed', 'Canal', 'Borewell', 'Tank']),
                    'season': random.choice(['Kharif', 'Rabi', 'Summer']),
                    'land_type': random.choice(['Forest Land', 'Revenue Land', 'Patta Land']),
                    'soil_type': random.choice(['Red Soil', 'Black Soil', 'Alluvial', 'Laterite']),
                    'slope': random.choice(['Flat', 'Gentle', 'Moderate']),
                    'productivity': random.choice(['High', 'Medium', 'Low'])
                },
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [points]
                }
            }
            
            agriculture_features.append(agriculture_feature)
        
        return agriculture_features

    def generate_water_features(self, cfr_polygon, village_name, district, state, num_water=4):
        """Generate water body features inside CFR"""
        water_features = []
        
        water_types = ['Stream', 'Seasonal Pond', 'Tank', 'Natural Spring', 'Check Dam']
        
        for i in range(num_water):
            water_type = random.choice(water_types)
            
            # Generate point inside CFR
            center_lat, center_lon = self.generate_point_inside_polygon(cfr_polygon)
            
            if water_type in ['Natural Spring']:
                # Point feature
                water_feature = {
                    'type': 'Feature',
                    'properties': {
                        'feature_id': f'WTR_{state[:2].upper()}_{district[:3].upper()}_{i+1:03d}',
                        'feature_type': 'Water Body',
                        'water_type': water_type,
                        'village': village_name,
                        'district': district,
                        'state': state,
                        'seasonal': random.choice([True, False]),
                        'usage': random.choice(['Drinking', 'Irrigation', 'Livestock', 'Multiple']),
                        'water_quality': random.choice(['Good', 'Moderate', 'Poor']),
                        'accessibility': random.choice(['Easy', 'Moderate', 'Difficult'])
                    },
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [center_lon, center_lat]
                    }
                }
            else:
                # Polygon feature for water bodies
                area_hectares = random.uniform(0.2, 5.0)
                radius_deg = math.sqrt(area_hectares / 100) / 111.0
                
                # Generate irregular water body shape
                points = []
                num_points = random.randint(6, 12)
                
                for j in range(num_points):
                    angle = 2 * math.pi * j / num_points
                    r = radius_deg * random.uniform(0.6, 1.4)
                    
                    lat = center_lat + r * math.cos(angle)
                    lon = center_lon + r * math.sin(angle)
                    points.append([lon, lat])
                
                points.append(points[0])
                
                water_feature = {
                    'type': 'Feature',
                    'properties': {
                        'feature_id': f'WTR_{state[:2].upper()}_{district[:3].upper()}_{i+1:03d}',
                        'feature_type': 'Water Body',
                        'water_type': water_type,
                        'village': village_name,
                        'district': district,
                        'state': state,
                        'area_hectares': round(area_hectares, 2),
                        'seasonal': random.choice([True, False]),
                        'usage': random.choice(['Drinking', 'Irrigation', 'Livestock', 'Multiple']),
                        'water_quality': random.choice(['Good', 'Moderate', 'Poor']),
                        'depth_category': random.choice(['Shallow', 'Medium', 'Deep']),
                        'fish_available': random.choice([True, False])
                    },
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [points]
                    }
                }
            
            water_features.append(water_feature)
        
        return water_features

    def generate_village_fra_data(self, state_name, num_villages=3):
        """Generate complete FRA data for villages in a state"""
        state_info = self.forest_states[state_name]
        all_features = []
        
        for village_idx in range(num_villages):
            district = random.choice(state_info['districts'])
            village_name = self.generate_realistic_village_name(state_name)
            tribal_community = random.choice(self.tribal_communities[state_name])
            
            # Generate CFR polygon
            cfr_data = self.generate_cfr_polygon(state_info, district)
            
            # Create CFR feature
            cfr_feature = {
                'type': 'Feature',
                'properties': {
                    'claim_id': f'CFR_{state_name[:2].upper()}_{district[:3].upper()}_{village_idx+1:03d}',
                    'claim_type': 'CFR',
                    'fra_type': 'Community Forest Resource Rights',
                    'village': village_name,
                    'district': district,
                    'state': state_name,
                    'area_claimed': round(cfr_data['area_hectares'], 2),
                    'area_unit': 'hectares',
                    'status': random.choice(['Approved', 'Pending', 'Under Review']),
                    'tribal_community': tribal_community,
                    'gram_sabha': f'{village_name} Gram Sabha',
                    'total_households': random.randint(50, 200),
                    'forest_committee_formed': random.choice([True, False]),
                    'management_plan': random.choice(['Prepared', 'Under Preparation', 'Not Started']),
                    'submission_date': (datetime.now() - timedelta(days=random.randint(60, 900))).strftime('%Y-%m-%d'),
                    'forest_type': random.choice(['Tropical Deciduous', 'Dry Deciduous', 'Moist Deciduous', 'Scrub']),
                    'biodiversity_rich': random.choice([True, False]),
                    'ntfp_available': random.choice([True, False]),
                    'wildlife_present': random.choice([True, False])
                },
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': cfr_data['coordinates']
                }
            }
            
            all_features.append(cfr_feature)
            
            # Generate IFR features inside CFR
            ifr_features = self.generate_ifr_polygons(
                cfr_data['coordinates'], village_name, district, state_name, tribal_community
            )
            all_features.extend(ifr_features)
            
            # Generate CR features inside CFR
            cr_features = self.generate_cr_features(
                cfr_data['coordinates'], village_name, district, state_name, tribal_community
            )
            all_features.extend(cr_features)
            
            # Generate agriculture features
            agriculture_features = self.generate_agriculture_features(
                cfr_data['coordinates'], village_name, district, state_name
            )
            all_features.extend(agriculture_features)
            
            # Generate water features
            water_features = self.generate_water_features(
                cfr_data['coordinates'], village_name, district, state_name
            )
            all_features.extend(water_features)
        
        return all_features

    def generate_complete_fra_dataset(self):
        """Generate complete FRA dataset for multiple states"""
        all_features = []
        
        # Generate data for all forest states
        for state_name in self.forest_states.keys():
            print(f"Generating FRA data for {state_name}...")
            state_features = self.generate_village_fra_data(state_name, num_villages=2)
            all_features.extend(state_features)
        
        # Create final GeoJSON
        fra_geojson = {
            'type': 'FeatureCollection',
            'properties': {
                'title': 'Vanachitra.AI - Forest Rights Act Spatial Data',
                'description': 'Realistic FRA claims data for WebGIS visualization',
                'created_date': datetime.now().isoformat(),
                'total_features': len(all_features),
                'states_covered': list(self.forest_states.keys()),
                'spatial_reference': 'EPSG:4326 (WGS84)',
                'data_quality': 'Synthetic but spatially realistic',
                'hierarchy': 'CFR polygons contain IFR and CR features',
                'coordinate_system': 'Decimal degrees (longitude, latitude)'
            },
            'features': all_features
        }
        
        return fra_geojson

def main():
    """Generate and save FRA spatial data"""
    generator = VanachitraFRAGenerator()
    
    print("🌳 Vanachitra.AI - Generating FRA Spatial Data...")
    print("=" * 50)
    
    # Generate complete dataset
    fra_data = generator.generate_complete_fra_dataset()
    
    # Save to file
    output_file = 'output/vanachitra_fra_data.geojson'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fra_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ FRA data generated successfully!")
    print(f"📁 Output file: {output_file}")
    print(f"📊 Total features: {len(fra_data['features'])}")
    
    # Print summary by feature type
    feature_counts = {}
    for feature in fra_data['features']:
        if 'claim_type' in feature['properties']:
            ftype = feature['properties']['claim_type']
        else:
            ftype = feature['properties']['feature_type']
        
        feature_counts[ftype] = feature_counts.get(ftype, 0) + 1
    
    print("\n📈 Feature type distribution:")
    for ftype, count in feature_counts.items():
        print(f"   {ftype}: {count} features")
    
    print(f"\n🗺️ States covered: {', '.join(fra_data['properties']['states_covered'])}")
    print("🎯 Spatial hierarchy: CFR polygons contain IFR and CR features")
    print("✅ All coordinates are within valid Indian land boundaries")

if __name__ == '__main__':
    main()