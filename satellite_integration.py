"""
Satellite Data Integration Module for Blue Carbon MRV System
Integrates with NASA, ESA, and ISRO satellite data for remote monitoring
"""

import requests
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class SatelliteDataProcessor:
    """Handles satellite imagery and environmental data processing"""
    
    def __init__(self):
        # Mock API endpoints (in production, use real satellite APIs)
        self.nasa_api_key = "DEMO_NASA_API_KEY"  
        # self.esa_api_key = "DEMO_ESA_API_KEY"
        # self.isro_api_key = "DEMO_ISRO_API_KEY"
        
        # Supported satellites and sensors
        self.satellites = {
            'sentinel2': {'provider': 'ESA', 'resolution': 10, 'spectral_bands': 13},
            'landsat8': {'provider': 'NASA', 'resolution': 30, 'spectral_bands': 11},
            'resourcesat': {'provider': 'ISRO', 'resolution': 5.8, 'spectral_bands': 4},
            'cartosat': {'provider': 'ISRO', 'resolution': 2.5, 'spectral_bands': 1}
        }
    
    def get_satellite_imagery(self, latitude: float, longitude: float, 
                            date_range: Tuple[str, str], satellite: str = 'sentinel2') -> Dict:
        """Retrieve satellite imagery for specific coordinates and date range"""
        
        # Mock satellite data retrieval (in production, call actual APIs)
        mock_data = {
            'request_id': f"SAT_{int(datetime.now().timestamp())}",
            'satellite': satellite,
            'provider': self.satellites[satellite]['provider'],
            'coordinates': {'lat': latitude, 'lon': longitude},
            'date_range': date_range,
            'resolution_m': self.satellites[satellite]['resolution'],
            'cloud_coverage': random.uniform(5, 25),  # percentage
            'images_found': random.randint(3, 15),
            'processing_status': 'completed',
            'imagery_analysis': self._analyze_vegetation_indices(latitude, longitude, satellite),
            'download_links': [
                f"https://satellite-api.example.com/image_{i}.tif" 
                for i in range(1, random.randint(3, 8))
            ]
        }
        
        return mock_data
    
    def _analyze_vegetation_indices(self, lat: float, lon: float, satellite: str) -> Dict:
        """Calculate vegetation indices from satellite imagery"""
        
        # Simulate coastal mangrove vegetation characteristics
        base_ndvi = 0.6 + random.uniform(-0.2, 0.3)  # Healthy mangroves: 0.4-0.9
        base_evi = 0.4 + random.uniform(-0.1, 0.2)   # Enhanced Vegetation Index
        
        # Adjust based on location (coastal vs inland)
        if self._is_coastal_location(lat, lon):
            # Coastal areas typically have more variation
            base_ndvi *= random.uniform(0.8, 1.1)
            salinity_stress = random.uniform(0.9, 1.0)
        else:
            salinity_stress = 1.0
        
        return {
            'ndvi': round(base_ndvi, 3),  # Normalized Difference Vegetation Index
            'evi': round(base_evi, 3),    # Enhanced Vegetation Index
            'savi': round(base_ndvi * 0.9, 3),  # Soil Adjusted Vegetation Index
            'msavi': round(base_ndvi * 0.95, 3),  # Modified SAVI
            'vegetation_health': self._classify_vegetation_health(base_ndvi),
            'vegetation_density': self._classify_vegetation_density(base_ndvi),
            'change_detection': self._generate_change_analysis(lat, lon),
            'salinity_stress_indicator': round(salinity_stress, 3),
            'water_stress': round(random.uniform(0.1, 0.3), 3),
            'canopy_cover_percent': round(base_ndvi * 100, 1)
        }
    
    def _is_coastal_location(self, lat: float, lon: float) -> bool:
        """Check if location is coastal (simplified logic)"""
        # Indian coastal coordinates approximation
        west_coast = 68 <= lon <= 76 and 8 <= lat <= 24
        east_coast = 77 <= lon <= 93 and 8 <= lat <= 22
        return west_coast or east_coast
    
    def _classify_vegetation_health(self, ndvi: float) -> str:
        """Classify vegetation health based on NDVI"""
        if ndvi >= 0.7:
            return "Excellent"
        elif ndvi >= 0.5:
            return "Good" 
        elif ndvi >= 0.3:
            return "Fair"
        elif ndvi >= 0.1:
            return "Poor"
        else:
            return "Stressed/Dying"
    
    def _classify_vegetation_density(self, ndvi: float) -> str:
        """Classify vegetation density"""
        if ndvi >= 0.6:
            return "Dense"
        elif ndvi >= 0.4:
            return "Moderate"
        elif ndvi >= 0.2:
            return "Sparse"
        else:
            return "Very Sparse"
    
    def _generate_change_analysis(self, lat: float, lon: float) -> Dict:
        """Generate vegetation change analysis over time"""
        
        # Simulate change over past periods
        periods = ['6_months_ago', '1_year_ago', '2_years_ago']
        changes = {}
        
        for period in periods:
            # Random change simulation (positive for restoration areas)
            change = random.uniform(-0.1, 0.3)  # NDVI change
            changes[period] = {
                'ndvi_change': round(change, 3),
                'trend': 'improving' if change > 0.05 else 'declining' if change < -0.05 else 'stable',
                'confidence': round(random.uniform(0.7, 0.95), 2)
            }
        
        return changes
    
    def monitor_restoration_site(self, project_data: Dict) -> Dict:
        """Comprehensive monitoring of restoration site using satellite data"""
        
        # Extract coordinates from project location
        lat, lon = self._extract_coordinates(project_data.get('location', '19.0176,72.8562'))
        
        # Get current satellite data
        current_imagery = self.get_satellite_imagery(
            latitude=lat,
            longitude=lon,
            date_range=(
                (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                datetime.now().strftime('%Y-%m-%d')
            )
        )
        
        # Get historical baseline (before project start)
        if project_data.get('start_date'):
            baseline_date = datetime.strptime(project_data['start_date'], '%Y-%m-%d')
            baseline_imagery = self.get_satellite_imagery(
                latitude=lat,
                longitude=lon,
                date_range=(
                    (baseline_date - timedelta(days=90)).strftime('%Y-%m-%d'),
                    baseline_date.strftime('%Y-%m-%d')
                )
            )
        else:
            baseline_imagery = None
        
        # Calculate restoration progress
        progress_analysis = self._calculate_restoration_progress(
            current_imagery, baseline_imagery, project_data
        )
        
        return {
            'project_id': project_data.get('id', 'unknown'),
            'monitoring_date': datetime.now().isoformat(),
            'location': {'latitude': lat, 'longitude': lon},
            'current_satellite_data': current_imagery,
            'baseline_satellite_data': baseline_imagery,
            'restoration_progress': progress_analysis,
            'recommendations': self._generate_monitoring_recommendations(progress_analysis),
            'next_monitoring_date': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        }
    
    def _extract_coordinates(self, location_str: str) -> Tuple[float, float]:
        """Extract latitude and longitude from location string"""
        try:
            if ',' in location_str:
                coords = location_str.split(',')
                return float(coords[0].strip()), float(coords[1].strip())
        except:
            pass
        
        # Default to Mumbai coordinates if parsing fails
        return 19.0176, 72.8562
    
    def _calculate_restoration_progress(self, current_data: Dict, baseline_data: Optional[Dict], 
                                     project_data: Dict) -> Dict:
        """Calculate restoration progress using satellite analysis"""
        
        current_ndvi = current_data['imagery_analysis']['ndvi']
        current_canopy = current_data['imagery_analysis']['canopy_cover_percent']
        
        if baseline_data:
            baseline_ndvi = baseline_data['imagery_analysis']['ndvi']
            baseline_canopy = baseline_data['imagery_analysis']['canopy_cover_percent']
            
            ndvi_improvement = current_ndvi - baseline_ndvi
            canopy_improvement = current_canopy - baseline_canopy
            
        else:
            # Use project data to estimate improvement
            ndvi_improvement = random.uniform(0.1, 0.4)  # Assume positive improvement
            canopy_improvement = random.uniform(10, 30)  # Percentage improvement
            baseline_ndvi = current_ndvi - ndvi_improvement
            baseline_canopy = current_canopy - canopy_improvement
        
        # Calculate expected vs actual progress
        project_age_months = self._calculate_project_age_months(project_data)
        expected_improvement = project_age_months * 0.02  # Expected NDVI improvement per month
        
        progress_score = min(100, (ndvi_improvement / expected_improvement) * 100) if expected_improvement > 0 else 100
        
        return {
            'baseline_ndvi': round(baseline_ndvi, 3),
            'current_ndvi': round(current_ndvi, 3),
            'ndvi_improvement': round(ndvi_improvement, 3),
            'baseline_canopy_cover': round(baseline_canopy, 1),
            'current_canopy_cover': round(current_canopy, 1),
            'canopy_improvement': round(canopy_improvement, 1),
            'project_age_months': project_age_months,
            'progress_score': round(progress_score, 1),
            'status': self._categorize_progress(progress_score),
            'vegetation_establishment_rate': round(ndvi_improvement / max(project_age_months, 1), 3),
            'estimated_survival_rate': round(min(100, (current_ndvi / 0.6) * 100), 1)
        }
    
    def _calculate_project_age_months(self, project_data: Dict) -> int:
        """Calculate project age in months"""
        try:
            if project_data.get('start_date'):
                start_date = datetime.strptime(project_data['start_date'], '%Y-%m-%d')
                return max(1, (datetime.now() - start_date).days // 30)
        except:
            pass
        
        # Default to 6 months if no start date
        return 6
    
    def _categorize_progress(self, progress_score: float) -> str:
        """Categorize restoration progress"""
        if progress_score >= 85:
            return "Excellent Progress"
        elif progress_score >= 70:
            return "Good Progress"
        elif progress_score >= 50:
            return "Moderate Progress"
        elif progress_score >= 30:
            return "Slow Progress"
        else:
            return "Poor Progress - Intervention Needed"
    
    def _generate_monitoring_recommendations(self, progress_analysis: Dict) -> List[str]:
        """Generate recommendations based on monitoring results"""
        recommendations = []
        
        progress_score = progress_analysis.get('progress_score', 0)
        ndvi_improvement = progress_analysis.get('ndvi_improvement', 0)
        survival_rate = progress_analysis.get('estimated_survival_rate', 0)
        
        if progress_score < 50:
            recommendations.append("Consider replanting in areas with poor establishment")
            recommendations.append("Investigate potential stressors (salinity, pests, diseases)")
            
        if ndvi_improvement < 0.1:
            recommendations.append("Enhance maintenance and care practices")
            recommendations.append("Consider supplemental irrigation during dry periods")
            
        if survival_rate < 70:
            recommendations.append("Review species selection for site conditions")
            recommendations.append("Improve soil preparation and planting techniques")
            
        if progress_score > 85:
            recommendations.append("Excellent progress - continue current practices")
            recommendations.append("Consider expanding restoration to adjacent areas")
            
        # Default recommendations
        if not recommendations:
            recommendations.extend([
                "Continue regular monitoring and maintenance",
                "Document successful practices for replication",
                "Prepare for next phase of restoration if applicable"
            ])
        
        return recommendations

class EnvironmentalSensorNetwork:
    """Simulates IoT environmental sensor network for ecosystem monitoring"""
    
    def __init__(self):
        self.sensor_types = {
            'soil_ph': {'unit': 'pH', 'range': (6.0, 8.5), 'optimal': (6.5, 7.5)},
            'soil_salinity': {'unit': 'dS/m', 'range': (0.5, 15.0), 'optimal': (2.0, 8.0)},
            'soil_moisture': {'unit': '%', 'range': (10, 95), 'optimal': (40, 80)},
            'water_temperature': {'unit': '°C', 'range': (18, 35), 'optimal': (22, 30)},
            'air_humidity': {'unit': '%', 'range': (40, 95), 'optimal': (60, 85)},
            'tidal_level': {'unit': 'm', 'range': (-2.0, 3.0), 'optimal': (-1.0, 2.0)}
        }
    
    def get_sensor_readings(self, project_id: str, location: Tuple[float, float]) -> Dict:
        """Get current sensor readings for a project location"""
        
        readings = {}
        
        for sensor_type, config in self.sensor_types.items():
            # Generate realistic readings with some variation
            optimal_min, optimal_max = config['optimal']
            base_value = random.uniform(optimal_min, optimal_max)
            
            # Add some realistic variation
            variation = random.uniform(-0.1, 0.1) * (optimal_max - optimal_min)
            current_value = base_value + variation
            
            # Ensure within physical range
            range_min, range_max = config['range']
            current_value = max(range_min, min(range_max, current_value))
            
            readings[sensor_type] = {
                'value': round(current_value, 2),
                'unit': config['unit'],
                'status': self._evaluate_sensor_status(current_value, config),
                'timestamp': datetime.now().isoformat(),
                'sensor_id': f"{project_id}_{sensor_type}_001"
            }
        
        return {
            'project_id': project_id,
            'location': {'latitude': location[0], 'longitude': location[1]},
            'reading_timestamp': datetime.now().isoformat(),
            'sensor_readings': readings,
            'overall_health_score': self._calculate_ecosystem_health_score(readings),
            'alerts': self._generate_sensor_alerts(readings)
        }
    
    def _evaluate_sensor_status(self, value: float, config: Dict) -> str:
        """Evaluate if sensor reading is within optimal range"""
        optimal_min, optimal_max = config['optimal']
        range_min, range_max = config['range']
        
        if optimal_min <= value <= optimal_max:
            return "Optimal"
        elif range_min <= value <= range_max:
            return "Acceptable"
        else:
            return "Critical"
    
    def _calculate_ecosystem_health_score(self, readings: Dict) -> float:
        """Calculate overall ecosystem health score"""
        optimal_count = sum(1 for reading in readings.values() if reading['status'] == 'Optimal')
        acceptable_count = sum(1 for reading in readings.values() if reading['status'] == 'Acceptable')
        total_sensors = len(readings)
        
        score = (optimal_count * 100 + acceptable_count * 70) / total_sensors
        return round(score, 1)
    
    def _generate_sensor_alerts(self, readings: Dict) -> List[str]:
        """Generate alerts based on sensor readings"""
        alerts = []
        
        for sensor_type, reading in readings.items():
            if reading['status'] == 'Critical':
                alerts.append(f"Critical {sensor_type.replace('_', ' ').title()}: {reading['value']} {reading['unit']}")
        
        return alerts

# Global instances
satellite_processor = SatelliteDataProcessor()
sensor_network = EnvironmentalSensorNetwork()