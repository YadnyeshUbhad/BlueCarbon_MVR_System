"""
Geo-tagging and Location Verification System for BlueCarbon MRV Platform
AI-powered location authenticity with satellite data cross-referencing
"""

import math
import json
import requests
import datetime
from typing import Dict, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass
from enum import Enum
import hashlib

class LocationVerificationStatus(Enum):
    VERIFIED = "verified"
    SUSPICIOUS = "suspicious"
    FRAUDULENT = "fraudulent"
    PENDING = "pending"
    INSUFFICIENT_DATA = "insufficient_data"

class LocationRiskLevel(Enum):
    VERY_LOW = "very_low"
    LOW = "low" 
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class GeoCoordinate:
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    timestamp: Optional[datetime.datetime] = None
    
    def __post_init__(self):
        if not (-90 <= self.latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if not (-180 <= self.longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees")

@dataclass
class SatelliteImageData:
    image_id: str
    coordinates: GeoCoordinate
    capture_date: datetime.datetime
    resolution: float  # meters per pixel
    cloud_coverage: float  # percentage
    vegetation_index: float  # NDVI or similar
    land_use_type: str
    image_hash: str
    source: str  # "sentinel", "landsat", etc.

@dataclass
class LocationVerificationResult:
    coordinates: GeoCoordinate
    verification_status: LocationVerificationStatus
    risk_level: LocationRiskLevel
    confidence_score: float  # 0-100
    verification_checks: Dict[str, bool]
    anomaly_flags: List[str]
    satellite_data: List[SatelliteImageData]
    verification_timestamp: datetime.datetime
    details: Dict[str, any]

class GeoVerificationEngine:
    """Advanced geo-location verification with AI-powered anomaly detection"""
    
    def __init__(self):
        self.earth_radius = 6371.0  # km
        self.max_location_drift = 100  # meters
        self.min_confidence_threshold = 70.0
        
        # Verification weights for different checks
        self.verification_weights = {
            'coordinate_validity': 15.0,
            'satellite_consistency': 25.0,
            'historical_comparison': 20.0,
            'land_use_verification': 15.0,
            'temporal_consistency': 10.0,
            'elevation_check': 10.0,
            'proximity_analysis': 5.0
        }
    
    def calculate_distance(self, coord1: GeoCoordinate, coord2: GeoCoordinate) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        lat1, lon1 = math.radians(coord1.latitude), math.radians(coord1.longitude)
        lat2, lon2 = math.radians(coord2.latitude), math.radians(coord2.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        return self.earth_radius * c * 1000  # return in meters
    
    def verify_coordinate_validity(self, coord: GeoCoordinate) -> Tuple[bool, str]:
        """Basic coordinate validity check"""
        try:
            # Check if coordinates are valid
            if not (-90 <= coord.latitude <= 90):
                return False, "Invalid latitude range"
            if not (-180 <= coord.longitude <= 180):
                return False, "Invalid longitude range"
                
            # Check for common fraud patterns (exact zeros, obvious fake coordinates)
            if coord.latitude == 0.0 and coord.longitude == 0.0:
                return False, "Null Island coordinates (likely default/fake)"
                
            # Check for coordinates in middle of ocean (suspicious for land projects)
            if self._is_open_ocean(coord):
                return False, "Coordinates in open ocean (suspicious for terrestrial projects)"
                
            return True, "Coordinates are valid"
            
        except Exception as e:
            return False, f"Coordinate validation error: {str(e)}"
    
    def _is_open_ocean(self, coord: GeoCoordinate) -> bool:
        """Simple check if coordinates are in open ocean"""
        # This is a simplified implementation
        # In production, you'd use a proper land/ocean dataset
        known_ocean_regions = [
            # Pacific Ocean center
            (0, -140, 20),  # lat, lon, radius_degrees
            # Atlantic Ocean center  
            (0, -30, 15),
            # Indian Ocean center
            (-20, 80, 15),
        ]
        
        for ocean_lat, ocean_lon, radius in known_ocean_regions:
            ocean_coord = GeoCoordinate(ocean_lat, ocean_lon)
            distance = self.calculate_distance(coord, ocean_coord)
            if distance < radius * 111000:  # Convert degrees to meters roughly
                return True
        return False
    
    def get_satellite_data(self, coord: GeoCoordinate, date_range: int = 30) -> List[SatelliteImageData]:
        """Simulate fetching satellite data for given coordinates"""
        # In production, this would call actual satellite APIs like Sentinel Hub, Google Earth Engine, etc.
        
        # Simulated satellite data
        satellite_data = []
        
        # Generate mock satellite images for the location
        base_date = datetime.datetime.now() - datetime.timedelta(days=date_range)
        
        for i in range(3):  # Simulate 3 satellite images
            image_date = base_date + datetime.timedelta(days=i * 10)
            
            # Simulate realistic satellite data
            image_data = SatelliteImageData(
                image_id=f"SENTINEL2_{image_date.strftime('%Y%m%d')}_{coord.latitude:.4f}_{coord.longitude:.4f}",
                coordinates=GeoCoordinate(
                    coord.latitude + (i * 0.0001),  # Small variation for realism
                    coord.longitude + (i * 0.0001)
                ),
                capture_date=image_date,
                resolution=10.0,  # 10m resolution
                cloud_coverage=15.0 + (i * 5),
                vegetation_index=0.6 + (i * 0.1),  # NDVI-like value
                land_use_type=self._determine_land_use(coord),
                image_hash=hashlib.md5(f"{coord.latitude}_{coord.longitude}_{i}".encode()).hexdigest(),
                source="sentinel-2"
            )
            satellite_data.append(image_data)
        
        return satellite_data
    
    def _determine_land_use(self, coord: GeoCoordinate) -> str:
        """Simulate land use determination from satellite data"""
        # In production, this would use actual ML models on satellite imagery
        
        # Simple heuristic based on coordinates
        if abs(coord.latitude) < 23.5:  # Tropics
            return "tropical_forest"
        elif abs(coord.latitude) > 60:  # Polar regions
            return "tundra"
        elif abs(coord.latitude) > 40:  # Temperate
            return "temperate_forest"
        else:
            return "grassland"
    
    def verify_satellite_consistency(self, coord: GeoCoordinate, satellite_data: List[SatelliteImageData]) -> Tuple[bool, str, float]:
        """Check consistency with satellite imagery"""
        if not satellite_data:
            return False, "No satellite data available", 0.0
        
        try:
            # Check coordinate consistency
            coordinate_variations = []
            for sat_data in satellite_data:
                distance = self.calculate_distance(coord, sat_data.coordinates)
                coordinate_variations.append(distance)
            
            avg_variation = sum(coordinate_variations) / len(coordinate_variations)
            
            if avg_variation > self.max_location_drift:
                return False, f"High coordinate variation: {avg_variation:.1f}m", 30.0
            
            # Check temporal consistency
            vegetation_values = [sat.vegetation_index for sat in satellite_data]
            vegetation_variation = max(vegetation_values) - min(vegetation_values)
            
            if vegetation_variation > 0.4:  # Suspicious vegetation change
                return False, "Suspicious vegetation index changes", 40.0
            
            # Check land use consistency
            land_uses = [sat.land_use_type for sat in satellite_data]
            if len(set(land_uses)) > 1:
                return False, "Inconsistent land use classification", 50.0
            
            # Calculate confidence based on data quality
            cloud_coverages = [sat.cloud_coverage for sat in satellite_data]
            avg_cloud_coverage = sum(cloud_coverages) / len(cloud_coverages)
            
            confidence = 100 - (avg_variation / 10) - (avg_cloud_coverage / 2)
            confidence = max(0, min(100, confidence))
            
            return True, "Satellite data consistent", confidence
            
        except Exception as e:
            return False, f"Satellite verification error: {str(e)}", 0.0
    
    def verify_historical_comparison(self, coord: GeoCoordinate) -> Tuple[bool, str, float]:
        """Compare with historical project locations in the area"""
        # In production, this would query historical project database
        
        # Simulate historical comparison
        try:
            # Mock: Check if there are other projects nearby
            # This could indicate clustering (good) or duplicate submissions (bad)
            
            # Simulate finding nearby projects
            nearby_projects = 2  # Mock data
            
            if nearby_projects == 0:
                return True, "No nearby projects (isolated location)", 80.0
            elif nearby_projects <= 3:
                return True, "Normal project density in area", 90.0
            elif nearby_projects <= 5:
                return True, "High project density (established area)", 85.0
            else:
                return False, "Suspicious project clustering", 30.0
                
        except Exception as e:
            return False, f"Historical comparison error: {str(e)}", 0.0
    
    def verify_land_use_appropriateness(self, coord: GeoCoordinate, project_type: str, satellite_data: List[SatelliteImageData]) -> Tuple[bool, str, float]:
        """Verify if land use is appropriate for project type"""
        if not satellite_data:
            return False, "No satellite data for land use verification", 0.0
        
        try:
            detected_land_use = satellite_data[0].land_use_type
            
            # Define appropriate land uses for different project types
            appropriate_land_uses = {
                'mangrove_restoration': ['tropical_forest', 'wetland', 'coastal'],
                'forest_conservation': ['tropical_forest', 'temperate_forest'],
                'reforestation': ['grassland', 'degraded_land', 'agricultural'],
                'wetland_protection': ['wetland', 'marsh', 'swamp'],
                'coastal_protection': ['coastal', 'beach', 'dune']
            }
            
            if project_type in appropriate_land_uses:
                if detected_land_use in appropriate_land_uses[project_type]:
                    return True, f"Land use ({detected_land_use}) appropriate for {project_type}", 95.0
                else:
                    return False, f"Land use ({detected_land_use}) inappropriate for {project_type}", 20.0
            else:
                # Unknown project type, give benefit of doubt
                return True, "Project type not specified, cannot verify land use", 60.0
                
        except Exception as e:
            return False, f"Land use verification error: {str(e)}", 0.0
    
    def verify_temporal_consistency(self, coord: GeoCoordinate, submitted_date: datetime.datetime, satellite_data: List[SatelliteImageData]) -> Tuple[bool, str, float]:
        """Verify temporal consistency of location data"""
        if not satellite_data:
            return False, "No satellite data for temporal verification", 0.0
        
        try:
            # Check if satellite data timeline makes sense
            satellite_dates = [sat.capture_date for sat in satellite_data]
            latest_satellite = max(satellite_dates)
            
            # Project submission should be after latest satellite data
            days_diff = (submitted_date - latest_satellite).days
            
            if days_diff < 0:
                return False, "Project submitted before latest satellite imagery", 10.0
            elif days_diff > 365:
                return False, "Project submitted too long after latest satellite data", 30.0
            else:
                confidence = 100 - (days_diff / 10)  # Decrease confidence with time gap
                return True, f"Temporal consistency good ({days_diff} days)", max(60, confidence)
                
        except Exception as e:
            return False, f"Temporal verification error: {str(e)}", 0.0
    
    def verify_elevation_consistency(self, coord: GeoCoordinate) -> Tuple[bool, str, float]:
        """Verify elevation data consistency"""
        # In production, this would use actual elevation APIs
        
        try:
            # Simulate elevation check
            # Mock: Get elevation from coordinate (simplified)
            simulated_elevation = abs(coord.latitude) * 100  # Very rough simulation
            
            if coord.altitude is not None:
                elevation_diff = abs(coord.altitude - simulated_elevation)
                
                if elevation_diff > 500:  # 500m difference
                    return False, f"Large elevation discrepancy: {elevation_diff:.1f}m", 20.0
                elif elevation_diff > 100:
                    return True, f"Moderate elevation discrepancy: {elevation_diff:.1f}m", 70.0
                else:
                    return True, f"Elevation consistent: {elevation_diff:.1f}m difference", 95.0
            else:
                return True, "No elevation data provided for comparison", 80.0
                
        except Exception as e:
            return False, f"Elevation verification error: {str(e)}", 0.0
    
    def analyze_proximity_patterns(self, coord: GeoCoordinate) -> Tuple[bool, str, float]:
        """Analyze proximity to other infrastructure/features"""
        # In production, this would check proximity to roads, cities, protected areas, etc.
        
        try:
            # Simulate proximity analysis
            # Mock: Check distance to nearest major feature
            
            # Simulate various distances
            distance_to_road = abs(coord.latitude * 1000) % 5000  # Mock road distance
            distance_to_city = abs(coord.longitude * 1000) % 50000  # Mock city distance
            
            proximity_flags = []
            
            if distance_to_road < 100:
                proximity_flags.append("Very close to road infrastructure")
            elif distance_to_road > 20000:
                proximity_flags.append("Very remote location")
            
            if distance_to_city < 5000:
                proximity_flags.append("Close to urban area")
            elif distance_to_city > 100000:
                proximity_flags.append("Extremely remote location")
            
            # Calculate confidence based on proximity patterns
            if len(proximity_flags) == 0:
                return True, "Normal proximity to infrastructure", 90.0
            elif len(proximity_flags) == 1:
                return True, f"Proximity note: {proximity_flags[0]}", 80.0
            else:
                return True, f"Multiple proximity flags: {'; '.join(proximity_flags)}", 70.0
                
        except Exception as e:
            return False, f"Proximity analysis error: {str(e)}", 0.0
    
    def calculate_overall_confidence(self, verification_results: Dict[str, Tuple[bool, str, float]]) -> float:
        """Calculate weighted overall confidence score"""
        total_weight = 0
        weighted_confidence = 0
        
        for check_name, (passed, message, confidence) in verification_results.items():
            weight = self.verification_weights.get(check_name, 1.0)
            total_weight += weight
            
            # If check failed, reduce confidence significantly
            if not passed:
                confidence = min(confidence, 30.0)
            
            weighted_confidence += confidence * weight
        
        if total_weight == 0:
            return 0.0
        
        return weighted_confidence / total_weight
    
    def determine_verification_status(self, confidence: float, anomaly_flags: List[str]) -> Tuple[LocationVerificationStatus, LocationRiskLevel]:
        """Determine verification status and risk level"""
        # Adjust confidence based on anomaly flags
        anomaly_penalty = len(anomaly_flags) * 10
        adjusted_confidence = confidence - anomaly_penalty
        
        # Determine status
        if adjusted_confidence >= 85:
            status = LocationVerificationStatus.VERIFIED
            risk = LocationRiskLevel.VERY_LOW
        elif adjusted_confidence >= 70:
            status = LocationVerificationStatus.VERIFIED
            risk = LocationRiskLevel.LOW
        elif adjusted_confidence >= 50:
            status = LocationVerificationStatus.SUSPICIOUS
            risk = LocationRiskLevel.MEDIUM
        elif adjusted_confidence >= 30:
            status = LocationVerificationStatus.SUSPICIOUS
            risk = LocationRiskLevel.HIGH
        else:
            status = LocationVerificationStatus.FRAUDULENT
            risk = LocationRiskLevel.VERY_HIGH
        
        return status, risk
    
    def verify_location(self, coord: GeoCoordinate, 
                       project_type: str = "unknown",
                       submitted_date: Optional[datetime.datetime] = None) -> LocationVerificationResult:
        """Main verification method that runs all checks"""
        
        if submitted_date is None:
            submitted_date = datetime.datetime.now()
        
        # Initialize results
        verification_checks = {}
        anomaly_flags = []
        
        try:
            # Get satellite data
            satellite_data = self.get_satellite_data(coord)
            
            # Run all verification checks
            checks = [
                ('coordinate_validity', self.verify_coordinate_validity(coord)),
                ('satellite_consistency', self.verify_satellite_consistency(coord, satellite_data)),
                ('historical_comparison', self.verify_historical_comparison(coord)),
                ('land_use_verification', self.verify_land_use_appropriateness(coord, project_type, satellite_data)),
                ('temporal_consistency', self.verify_temporal_consistency(coord, submitted_date, satellite_data)),
                ('elevation_check', self.verify_elevation_consistency(coord)),
                ('proximity_analysis', self.analyze_proximity_patterns(coord))
            ]
            
            verification_results = {}
            for check_name, (passed, message, confidence) in checks:
                verification_checks[check_name] = passed
                verification_results[check_name] = (passed, message, confidence)
                
                if not passed:
                    anomaly_flags.append(f"{check_name}: {message}")
            
            # Calculate overall confidence
            overall_confidence = self.calculate_overall_confidence(verification_results)
            
            # Determine status and risk level
            status, risk_level = self.determine_verification_status(overall_confidence, anomaly_flags)
            
            return LocationVerificationResult(
                coordinates=coord,
                verification_status=status,
                risk_level=risk_level,
                confidence_score=round(overall_confidence, 1),
                verification_checks=verification_checks,
                anomaly_flags=anomaly_flags,
                satellite_data=satellite_data,
                verification_timestamp=datetime.datetime.now(),
                details={
                    'check_results': verification_results,
                    'project_type': project_type,
                    'submitted_date': submitted_date.isoformat() if submitted_date else None
                }
            )
            
        except Exception as e:
            # Return error result
            return LocationVerificationResult(
                coordinates=coord,
                verification_status=LocationVerificationStatus.INSUFFICIENT_DATA,
                risk_level=LocationRiskLevel.VERY_HIGH,
                confidence_score=0.0,
                verification_checks={'system_error': False},
                anomaly_flags=[f"System error: {str(e)}"],
                satellite_data=[],
                verification_timestamp=datetime.datetime.now(),
                details={'error': str(e)}
            )

class GeoVerificationManager:
    """Management class for geo-verification system"""
    
    def __init__(self):
        self.engine = GeoVerificationEngine()
        self.verification_cache = {}  # Cache for recent verifications
    
    def verify_project_location(self, project_id: str, latitude: float, longitude: float, 
                               project_type: str = "unknown",
                               altitude: Optional[float] = None) -> LocationVerificationResult:
        """Verify location for a project"""
        
        coord = GeoCoordinate(latitude, longitude, altitude)
        
        # Check cache first
        cache_key = f"{latitude:.6f}_{longitude:.6f}_{project_type}"
        if cache_key in self.verification_cache:
            cached_result = self.verification_cache[cache_key]
            # Return cached result if less than 24 hours old
            if (datetime.datetime.now() - cached_result.verification_timestamp).hours < 24:
                return cached_result
        
        # Perform verification
        result = self.engine.verify_location(coord, project_type)
        
        # Cache result
        self.verification_cache[cache_key] = result
        
        return result
    
    def bulk_verify_locations(self, locations: List[Dict]) -> List[LocationVerificationResult]:
        """Verify multiple locations in batch"""
        results = []
        
        for location_data in locations:
            try:
                coord = GeoCoordinate(
                    location_data['latitude'],
                    location_data['longitude'],
                    location_data.get('altitude')
                )
                
                result = self.engine.verify_location(
                    coord, 
                    location_data.get('project_type', 'unknown')
                )
                results.append(result)
                
            except Exception as e:
                # Create error result
                error_result = LocationVerificationResult(
                    coordinates=GeoCoordinate(0, 0),
                    verification_status=LocationVerificationStatus.INSUFFICIENT_DATA,
                    risk_level=LocationRiskLevel.VERY_HIGH,
                    confidence_score=0.0,
                    verification_checks={'parsing_error': False},
                    anomaly_flags=[f"Location parsing error: {str(e)}"],
                    satellite_data=[],
                    verification_timestamp=datetime.datetime.now(),
                    details={'error': str(e), 'original_data': location_data}
                )
                results.append(error_result)
        
        return results
    
    def get_verification_summary(self, results: List[LocationVerificationResult]) -> Dict:
        """Generate summary statistics for verification results"""
        if not results:
            return {'error': 'No results to analyze'}
        
        total_locations = len(results)
        verified_count = sum(1 for r in results if r.verification_status == LocationVerificationStatus.VERIFIED)
        suspicious_count = sum(1 for r in results if r.verification_status == LocationVerificationStatus.SUSPICIOUS)
        fraudulent_count = sum(1 for r in results if r.verification_status == LocationVerificationStatus.FRAUDULENT)
        
        avg_confidence = sum(r.confidence_score for r in results) / total_locations
        
        risk_distribution = {
            'very_low': sum(1 for r in results if r.risk_level == LocationRiskLevel.VERY_LOW),
            'low': sum(1 for r in results if r.risk_level == LocationRiskLevel.LOW),
            'medium': sum(1 for r in results if r.risk_level == LocationRiskLevel.MEDIUM),
            'high': sum(1 for r in results if r.risk_level == LocationRiskLevel.HIGH),
            'very_high': sum(1 for r in results if r.risk_level == LocationRiskLevel.VERY_HIGH),
        }
        
        return {
            'total_locations': total_locations,
            'verification_status': {
                'verified': verified_count,
                'suspicious': suspicious_count,
                'fraudulent': fraudulent_count,
                'verified_percentage': round(verified_count / total_locations * 100, 1)
            },
            'average_confidence': round(avg_confidence, 1),
            'risk_distribution': risk_distribution,
            'common_anomalies': self._get_common_anomalies(results)
        }
    
    def _get_common_anomalies(self, results: List[LocationVerificationResult]) -> List[str]:
        """Extract most common anomaly types"""
        anomaly_counts = {}
        
        for result in results:
            for anomaly in result.anomaly_flags:
                anomaly_type = anomaly.split(':')[0] if ':' in anomaly else anomaly
                anomaly_counts[anomaly_type] = anomaly_counts.get(anomaly_type, 0) + 1
        
        # Return top 5 most common anomalies
        sorted_anomalies = sorted(anomaly_counts.items(), key=lambda x: x[1], reverse=True)
        return [f"{anomaly}: {count} occurrences" for anomaly, count in sorted_anomalies[:5]]

# Usage example and testing
def demo_geo_verification():
    """Demonstrate the geo-verification system"""
    manager = GeoVerificationManager()
    
    # Test locations
    test_locations = [
        {
            'latitude': 19.0760,
            'longitude': 72.8777,
            'project_type': 'mangrove_restoration',
            'description': 'Mumbai Mangrove Project'
        },
        {
            'latitude': 0.0,
            'longitude': 0.0,
            'project_type': 'forest_conservation',
            'description': 'Null Island (should fail)'
        },
        {
            'latitude': 28.6139,
            'longitude': 77.2090,
            'project_type': 'urban_forestry',
            'description': 'Delhi Urban Forest'
        }
    ]
    
    print("=== Geo-Location Verification Demo ===\n")
    
    results = []
    for location in test_locations:
        print(f"Verifying: {location['description']}")
        print(f"Coordinates: {location['latitude']}, {location['longitude']}")
        
        result = manager.verify_project_location(
            f"project_{len(results)}",
            location['latitude'],
            location['longitude'],
            location['project_type']
        )
        
        print(f"Status: {result.verification_status.value}")
        print(f"Risk Level: {result.risk_level.value}")
        print(f"Confidence: {result.confidence_score}%")
        
        if result.anomaly_flags:
            print("Anomalies:")
            for flag in result.anomaly_flags:
                print(f"  - {flag}")
        
        print(f"Satellite Images: {len(result.satellite_data)}")
        print("-" * 50)
        
        results.append(result)
    
    # Generate summary
    summary = manager.get_verification_summary(results)
    print("\n=== Verification Summary ===")
    print(f"Total Locations: {summary['total_locations']}")
    print(f"Verified: {summary['verification_status']['verified']} ({summary['verification_status']['verified_percentage']}%)")
    print(f"Average Confidence: {summary['average_confidence']}%")
    
    return manager, results

if __name__ == "__main__":
    demo_geo_verification()