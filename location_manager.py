"""
Location Management System for Blue Carbon MRV System
Handles coordinate validation, geocoding, and coastal area identification
"""

import requests
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class LocationManager:
    """Manages project locations with accurate coordinates and validation"""
    
    def __init__(self):
        # Indian coastal boundaries for validation
        self.coastal_regions = {
            'west_coast': {
                'states': ['Gujarat', 'Maharashtra', 'Goa', 'Karnataka', 'Kerala'],
                'lat_range': (8.0, 24.0),
                'lng_range': (68.0, 76.0)
            },
            'east_coast': {
                'states': ['West Bengal', 'Odisha', 'Andhra Pradesh', 'Tamil Nadu', 'Puducherry'],
                'lat_range': (8.0, 22.5),
                'lng_range': (77.0, 93.0)
            },
            'islands': {
                'regions': ['Lakshadweep', 'Andaman and Nicobar'],
                'coordinates': [
                    {'name': 'Lakshadweep', 'lat': 10.5667, 'lng': 72.6417},
                    {'name': 'Andaman', 'lat': 11.7401, 'lng': 92.6586},
                    {'name': 'Nicobar', 'lat': 7.9403, 'lng': 93.9537}
                ]
            }
        }
        
        # Major coastal cities with accurate coordinates
        self.coastal_cities = {
            'mumbai': {'lat': 19.0176, 'lng': 72.8562, 'state': 'Maharashtra'},
            'chennai': {'lat': 13.0827, 'lng': 80.2707, 'state': 'Tamil Nadu'},
            'kochi': {'lat': 9.9312, 'lng': 76.2673, 'state': 'Kerala'},
            'kolkata': {'lat': 22.5726, 'lng': 88.3639, 'state': 'West Bengal'},
            'surat': {'lat': 21.1959, 'lng': 72.8302, 'state': 'Gujarat'},
            'visakhapatnam': {'lat': 17.7231, 'lng': 83.3012, 'state': 'Andhra Pradesh'},
            'mangalore': {'lat': 12.9141, 'lng': 74.8560, 'state': 'Karnataka'},
            'puducherry': {'lat': 11.9416, 'lng': 79.8083, 'state': 'Puducherry'},
            'goa': {'lat': 15.2993, 'lng': 74.1240, 'state': 'Goa'},
            'trivandrum': {'lat': 8.5241, 'lng': 76.9366, 'state': 'Kerala'},
            'bhubaneswar': {'lat': 20.2961, 'lng': 85.8245, 'state': 'Odisha'},
            'sundarbans': {'lat': 22.2587, 'lng': 91.7832, 'state': 'West Bengal'}
        }
        
        # Blue carbon ecosystem suitability zones
        self.ecosystem_zones = {
            'mangrove': {
                'suitable_areas': [
                    {'region': 'Sundarbans', 'lat': 22.2587, 'lng': 91.7832, 'suitability': 0.95},
                    {'region': 'Mumbai Coast', 'lat': 19.0176, 'lng': 72.8562, 'suitability': 0.85},
                    {'region': 'Kerala Backwaters', 'lat': 9.9312, 'lng': 76.2673, 'suitability': 0.90},
                    {'region': 'Andaman Coast', 'lat': 11.7401, 'lng': 92.6586, 'suitability': 0.92}
                ]
            },
            'seagrass': {
                'suitable_areas': [
                    {'region': 'Lakshadweep', 'lat': 10.5667, 'lng': 72.6417, 'suitability': 0.95},
                    {'region': 'Gulf of Mannar', 'lat': 9.2000, 'lng': 79.1000, 'suitability': 0.90},
                    {'region': 'Chilika Lake', 'lat': 19.9067, 'lng': 85.3206, 'suitability': 0.85}
                ]
            },
            'coastal_wetlands': {
                'suitable_areas': [
                    {'region': 'Keoladeo', 'lat': 27.1593, 'lng': 77.5250, 'suitability': 0.80},
                    {'region': 'Point Calimere', 'lat': 10.2769, 'lng': 79.8560, 'suitability': 0.88},
                    {'region': 'Pulicat Lake', 'lat': 13.6667, 'lng': 80.3167, 'suitability': 0.85}
                ]
            }
        }

    def validate_coordinates(self, latitude: float, longitude: float) -> Dict:
        """Validate if coordinates are within Indian coastal boundaries"""
        
        result = {
            'valid': False,
            'region': None,
            'coastal': False,
            'suitable_for_blue_carbon': False,
            'distance_to_coast': None,
            'recommendations': []
        }
        
        # Check if coordinates are in India
        if not (6.0 <= latitude <= 37.0 and 68.0 <= longitude <= 98.0):
            result['recommendations'].append('Coordinates are outside Indian territory')
            return result
        
        # Check coastal regions
        west_coast = self.coastal_regions['west_coast']
        east_coast = self.coastal_regions['east_coast']
        
        if (west_coast['lat_range'][0] <= latitude <= west_coast['lat_range'][1] and 
            west_coast['lng_range'][0] <= longitude <= west_coast['lng_range'][1]):
            result['valid'] = True
            result['region'] = 'West Coast'
            result['coastal'] = True
            result['suitable_for_blue_carbon'] = True
            
        elif (east_coast['lat_range'][0] <= latitude <= east_coast['lat_range'][1] and 
              east_coast['lng_range'][0] <= longitude <= east_coast['lng_range'][1]):
            result['valid'] = True
            result['region'] = 'East Coast'
            result['coastal'] = True
            result['suitable_for_blue_carbon'] = True
        
        # Check islands
        for island in self.coastal_regions['islands']['coordinates']:
            distance = self._calculate_distance(latitude, longitude, island['lat'], island['lng'])
            if distance < 100:  # Within 100km of islands
                result['valid'] = True
                result['region'] = island['name']
                result['coastal'] = True
                result['suitable_for_blue_carbon'] = True
                break
        
        if result['coastal']:
            result['distance_to_coast'] = self._calculate_distance_to_coast(latitude, longitude)
            
            if result['distance_to_coast'] > 50:  # More than 50km inland
                result['recommendations'].append('Location is far from coast - consider areas closer to shoreline')
                result['suitable_for_blue_carbon'] = False
        else:
            result['recommendations'].append('Location is not in a coastal region suitable for blue carbon projects')
        
        return result

    def geocode_location(self, location_name: str) -> Optional[Dict]:
        """Convert location name to coordinates using geocoding"""
        
        # First check if it's in our coastal cities database
        location_key = location_name.lower().replace(' ', '').replace(',', '')
        if location_key in self.coastal_cities:
            city_data = self.coastal_cities[location_key]
            return {
                'latitude': city_data['lat'],
                'longitude': city_data['lng'],
                'display_name': f"{location_name}, {city_data['state']}, India",
                'state': city_data['state'],
                'source': 'internal_database',
                'accuracy': 'high'
            }
        
        # Use Nominatim geocoding service
        try:
            url = f"https://nominatim.openstreetmap.org/search?format=json&q={location_name}&countrycodes=in&limit=1"
            headers = {'User-Agent': 'BlueCarbon-MRV/1.0'}
            
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            
            if data:
                location = data[0]
                return {
                    'latitude': float(location['lat']),
                    'longitude': float(location['lon']),
                    'display_name': location['display_name'],
                    'source': 'openstreetmap',
                    'accuracy': 'medium'
                }
        except Exception as e:
            print(f"Geocoding error: {e}")
        
        return None

    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict]:
        """Convert coordinates to location information"""
        
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}&countrycodes=in"
            headers = {'User-Agent': 'BlueCarbon-MRV/1.0'}
            
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            
            if 'address' in data:
                address = data['address']
                return {
                    'display_name': data.get('display_name', ''),
                    'state': address.get('state', ''),
                    'district': address.get('state_district', address.get('county', '')),
                    'city': address.get('city', address.get('town', address.get('village', ''))),
                    'postcode': address.get('postcode', ''),
                    'country': address.get('country', ''),
                    'formatted_address': data.get('display_name', '')
                }
        except Exception as e:
            print(f"Reverse geocoding error: {e}")
        
        return None

    def find_suitable_locations(self, ecosystem_type: str, area_required: float = None) -> List[Dict]:
        """Find suitable locations for specific ecosystem types"""
        
        ecosystem_key = ecosystem_type.lower().replace(' ', '_')
        
        if ecosystem_key not in self.ecosystem_zones:
            return []
        
        suitable_locations = []
        
        for area in self.ecosystem_zones[ecosystem_key]['suitable_areas']:
            location_info = {
                'region': area['region'],
                'latitude': area['lat'],
                'longitude': area['lng'],
                'suitability_score': area['suitability'],
                'ecosystem_type': ecosystem_type,
                'estimated_area_available': self._estimate_available_area(area),
                'recommended': area['suitability'] > 0.85
            }
            
            # Add additional context
            validation = self.validate_coordinates(area['lat'], area['lng'])
            location_info.update(validation)
            
            suitable_locations.append(location_info)
        
        # Sort by suitability score
        suitable_locations.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        return suitable_locations

    def calculate_area_from_coordinates(self, coordinates: List[Tuple[float, float]]) -> float:
        """Calculate area in hectares from polygon coordinates using Shoelace formula"""
        
        if len(coordinates) < 3:
            return 0.0
        
        # Convert coordinates to radians for more accurate calculation
        coords_rad = [(lat * 3.14159/180, lng * 3.14159/180) for lat, lng in coordinates]
        
        # Earth radius in meters
        R = 6371000
        
        # Calculate area using spherical excess formula for better accuracy
        area_rad = 0.0
        n = len(coords_rad)
        
        for i in range(n):
            j = (i + 1) % n
            area_rad += coords_rad[i][1] * coords_rad[j][0] - coords_rad[j][1] * coords_rad[i][0]
        
        area_rad = abs(area_rad) / 2.0
        area_m2 = area_rad * R * R
        
        # Convert to hectares
        return area_m2 / 10000.0

    def get_project_location_recommendations(self, project_data: Dict) -> Dict:
        """Get comprehensive recommendations for project location"""
        
        recommendations = {
            'location_validation': None,
            'ecosystem_suitability': None,
            'nearby_references': [],
            'optimization_suggestions': [],
            'regulatory_considerations': []
        }
        
        # Validate current location if coordinates provided
        if 'latitude' in project_data and 'longitude' in project_data:
            lat = float(project_data['latitude'])
            lng = float(project_data['longitude'])
            
            recommendations['location_validation'] = self.validate_coordinates(lat, lng)
            
            # Find nearby reference locations
            recommendations['nearby_references'] = self._find_nearby_references(lat, lng)
        
        # Check ecosystem suitability
        if 'ecosystem' in project_data:
            ecosystem = project_data['ecosystem']
            suitable_locations = self.find_suitable_locations(ecosystem)
            
            recommendations['ecosystem_suitability'] = {
                'ecosystem_type': ecosystem,
                'suitable_locations': suitable_locations[:3],  # Top 3 recommendations
                'total_suitable_areas': len(suitable_locations)
            }
        
        # Add optimization suggestions
        recommendations['optimization_suggestions'] = self._generate_optimization_suggestions(project_data)
        
        # Add regulatory considerations
        recommendations['regulatory_considerations'] = self._get_regulatory_info(project_data)
        
        return recommendations

    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        import math
        
        R = 6371  # Earth radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lng1_rad = math.radians(lng1)
        lat2_rad = math.radians(lat2)
        lng2_rad = math.radians(lng2)
        
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        a = (math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c

    def _calculate_distance_to_coast(self, latitude: float, longitude: float) -> float:
        """Calculate approximate distance to nearest coastline"""
        
        # Simplified calculation - find distance to nearest coastal city
        min_distance = float('inf')
        
        for city_data in self.coastal_cities.values():
            distance = self._calculate_distance(
                latitude, longitude, 
                city_data['lat'], city_data['lng']
            )
            min_distance = min(min_distance, distance)
        
        return min_distance

    def _estimate_available_area(self, location: Dict) -> float:
        """Estimate available area for restoration in hectares"""
        # Mock implementation - in reality would use satellite data
        base_area = 1000  # Base area in hectares
        suitability_factor = location['suitability']
        
        return base_area * suitability_factor

    def _find_nearby_references(self, latitude: float, longitude: float, radius_km: float = 100) -> List[Dict]:
        """Find nearby reference locations within specified radius"""
        
        nearby = []
        
        for city_name, city_data in self.coastal_cities.items():
            distance = self._calculate_distance(
                latitude, longitude,
                city_data['lat'], city_data['lng']
            )
            
            if distance <= radius_km:
                nearby.append({
                    'name': city_name.title(),
                    'distance_km': round(distance, 1),
                    'coordinates': {'lat': city_data['lat'], 'lng': city_data['lng']},
                    'state': city_data['state']
                })
        
        # Sort by distance
        nearby.sort(key=lambda x: x['distance_km'])
        return nearby

    def _generate_optimization_suggestions(self, project_data: Dict) -> List[str]:
        """Generate location optimization suggestions"""
        
        suggestions = []
        
        if 'area' in project_data:
            area = float(project_data['area'])
            if area > 500:
                suggestions.append("Consider dividing large projects into smaller phases for better management")
            elif area < 10:
                suggestions.append("Small project areas may benefit from clustering with nearby initiatives")
        
        if 'ecosystem' in project_data:
            ecosystem = project_data['ecosystem'].lower()
            if 'mangrove' in ecosystem:
                suggestions.append("Ensure access to tidal zones for mangrove establishment")
                suggestions.append("Check soil salinity levels for mangrove suitability")
            elif 'seagrass' in ecosystem:
                suggestions.append("Verify water depth and quality for seagrass growth")
                suggestions.append("Consider seasonal variations in water levels")
        
        return suggestions

    def _get_regulatory_info(self, project_data: Dict) -> List[str]:
        """Get relevant regulatory considerations"""
        
        considerations = [
            "Obtain Coastal Regulation Zone (CRZ) clearance before project implementation",
            "Coordinate with State Forest Department for mangrove restoration permits",
            "Ensure compliance with Environmental Impact Assessment requirements",
            "Engage with local Panchayati Raj institutions for community participation"
        ]
        
        if 'state' in project_data:
            state = project_data['state']
            if state in ['West Bengal', 'Sundarbans']:
                considerations.append("Special permissions required for Sundarbans Tiger Reserve area")
            elif state in ['Kerala']:
                considerations.append("Coordinate with Kerala State Coastal Area Development Corporation")
            elif state in ['Tamil Nadu']:
                considerations.append("Engage with Tamil Nadu Coastal Area Development Corporation")
        
        return considerations

# Global instance
location_manager = LocationManager()