"""
Machine Learning Predictions Module for Blue Carbon MRV System
Implements predictive models for carbon sequestration forecasting and ecosystem health
"""

import numpy as np
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json

class CarbonSequestrationPredictor:
    """Predictive models for carbon sequestration forecasting"""
    
    def __init__(self):
        # Mock trained model parameters (in production, load actual ML models)
        self.model_version = "v2.1.0"
        self.last_training_date = "2024-01-15"
        
        # Species-specific growth and carbon sequestration parameters
        self.species_parameters = {
            'Rhizophora': {
                'max_height': 25.0,
                'max_dbh': 0.6,
                'growth_rate_height': 0.8,  # m/year
                'growth_rate_dbh': 0.025,   # m/year
                'carbon_coefficient': 0.47,
                'survival_rate_baseline': 0.85
            },
            'Avicennia': {
                'max_height': 20.0,
                'max_dbh': 0.5,
                'growth_rate_height': 0.6,
                'growth_rate_dbh': 0.02,
                'carbon_coefficient': 0.45,
                'survival_rate_baseline': 0.80
            },
            'Mangrove': {  # Generic mangrove
                'max_height': 22.0,
                'max_dbh': 0.55,
                'growth_rate_height': 0.7,
                'growth_rate_dbh': 0.022,
                'carbon_coefficient': 0.46,
                'survival_rate_baseline': 0.82
            }
        }
        
        # Environmental factors affecting growth
        self.environmental_factors = {
            'salinity_optimal': (2.0, 8.0),    # dS/m
            'ph_optimal': (6.5, 7.5),
            'temperature_optimal': (22, 30),   # Celsius
            'rainfall_optimal': (1000, 2500)  # mm/year
        }
    
    def predict_carbon_sequestration(self, project_data: Dict, forecast_years: int = 20) -> Dict:
        """Predict carbon sequestration over time for a project"""
        
        # Extract project parameters
        tree_count = project_data.get('number_of_trees', 1000)
        tree_species = project_data.get('tree_species', 'Mangrove')
        location = self._parse_location(project_data.get('location', '19.0176,72.8562'))
        current_height = project_data.get('tree_height', 2.0)
        current_dbh = project_data.get('tree_dbh', 0.05)
        current_age = project_data.get('tree_age', 1)
        
        # Get species parameters
        species_params = self.species_parameters.get(tree_species, self.species_parameters['Mangrove'])
        
        # Predict growth over time
        annual_predictions = []
        cumulative_carbon = 0
        
        for year in range(1, forecast_years + 1):
            current_age += 1
            
            # Predict growth (with diminishing returns as trees mature)
            age_factor = max(0.1, 1.0 - (current_age / 40))  # Growth slows with age
            
            height_growth = species_params['growth_rate_height'] * age_factor
            dbh_growth = species_params['growth_rate_dbh'] * age_factor
            
            # Apply environmental stress factors
            env_stress = self._calculate_environmental_stress(location)
            height_growth *= env_stress
            dbh_growth *= env_stress
            
            # Update dimensions (with maximum limits)
            current_height = min(species_params['max_height'], current_height + height_growth)
            current_dbh = min(species_params['max_dbh'], current_dbh + dbh_growth)
            
            # Calculate biomass using allometric equations
            above_ground_biomass = 0.0673 * ((current_dbh * 100) ** 2 * current_height) ** 0.976
            below_ground_biomass = above_ground_biomass * 0.22
            total_biomass = above_ground_biomass + below_ground_biomass
            
            # Calculate carbon content
            carbon_content_per_tree = total_biomass * species_params['carbon_coefficient']
            co2_sequestered_per_tree = (carbon_content_per_tree / 1000) * 3.67  # tonnes CO2
            
            # Apply survival rate (some trees may die over time)
            survival_rate = self._calculate_survival_rate(current_age, env_stress, species_params)
            effective_tree_count = tree_count * survival_rate
            
            # Total project carbon sequestration for this year
            annual_co2 = co2_sequestered_per_tree * effective_tree_count
            cumulative_carbon += annual_co2
            
            annual_predictions.append({
                'year': year,
                'tree_age': current_age,
                'surviving_trees': int(effective_tree_count),
                'avg_height': round(current_height, 2),
                'avg_dbh': round(current_dbh, 3),
                'co2_per_tree': round(co2_sequestered_per_tree, 4),
                'annual_co2_total': round(annual_co2, 2),
                'cumulative_co2': round(cumulative_carbon, 2),
                'survival_rate': round(survival_rate, 3)
            })
        
        # Generate summary statistics
        peak_annual_sequestration = max(pred['annual_co2_total'] for pred in annual_predictions)
        total_lifetime_sequestration = annual_predictions[-1]['cumulative_co2']
        avg_annual_sequestration = total_lifetime_sequestration / forecast_years
        
        return {
            'project_id': project_data.get('id', 'unknown'),
            'prediction_date': datetime.now().isoformat(),
            'model_version': self.model_version,
            'forecast_years': forecast_years,
            'input_parameters': {
                'initial_tree_count': tree_count,
                'tree_species': tree_species,
                'initial_height': current_height,
                'initial_dbh': current_dbh,
                'initial_age': current_age,
                'location': location
            },
            'predictions': {
                'annual_forecast': annual_predictions,
                'summary': {
                    'total_lifetime_co2': round(total_lifetime_sequestration, 2),
                    'avg_annual_co2': round(avg_annual_sequestration, 2),
                    'peak_annual_co2': round(peak_annual_sequestration, 2),
                    'final_tree_count': annual_predictions[-1]['surviving_trees'],
                    'final_survival_rate': annual_predictions[-1]['survival_rate']
                }
            },
            'confidence_intervals': self._generate_confidence_intervals(annual_predictions),
            'risk_factors': self._assess_risk_factors(project_data, location),
            'recommendations': self._generate_ml_recommendations(annual_predictions, project_data)
        }
    
    def predict_ecosystem_health(self, project_data: Dict, sensor_data: Optional[Dict] = None) -> Dict:
        """Predict ecosystem health trends based on current conditions"""
        
        # Current health indicators
        current_indicators = self._extract_health_indicators(project_data, sensor_data)
        
        # Predict health trends for next 5 years
        health_predictions = []
        current_health_score = current_indicators['overall_score']
        
        for year in range(1, 6):
            # Simulate health progression based on various factors
            stress_factors = self._calculate_stress_progression(project_data, year)
            management_effectiveness = random.uniform(0.8, 1.1)  # Management quality factor
            
            # Health score change
            base_change = random.uniform(-5, 10)  # Natural variation
            stress_impact = -sum(stress_factors.values()) * 10
            management_impact = (management_effectiveness - 1.0) * 20
            
            health_change = base_change + stress_impact + management_impact
            current_health_score = max(0, min(100, current_health_score + health_change))
            
            health_predictions.append({
                'year': year,
                'health_score': round(current_health_score, 1),
                'health_category': self._categorize_health(current_health_score),
                'primary_stressors': [k for k, v in stress_factors.items() if v > 0.3],
                'intervention_needed': current_health_score < 60
            })
        
        return {
            'project_id': project_data.get('id', 'unknown'),
            'current_health': current_indicators,
            'health_forecast': health_predictions,
            'trend_analysis': self._analyze_health_trend(health_predictions),
            'early_warning_indicators': self._identify_early_warnings(health_predictions)
        }
    
    def optimize_planting_strategy(self, site_conditions: Dict) -> Dict:
        """Recommend optimal planting strategy based on site conditions"""
        
        # Analyze site conditions
        location = site_conditions.get('location', {'lat': 19.0176, 'lon': 72.8562})
        area_hectares = site_conditions.get('area', 10.0)
        soil_conditions = site_conditions.get('soil', {})
        water_conditions = site_conditions.get('water', {})
        
        # Recommend species mix
        species_recommendations = self._recommend_species_mix(location, soil_conditions, water_conditions)
        
        # Calculate optimal density
        optimal_density = self._calculate_optimal_density(area_hectares, species_recommendations)
        
        # Recommend planting timeline
        planting_timeline = self._generate_planting_timeline(area_hectares, optimal_density)
        
        # Predict success probability
        success_probability = self._predict_success_probability(species_recommendations, site_conditions)
        
        return {
            'site_analysis': {
                'location': location,
                'area_hectares': area_hectares,
                'site_suitability_score': round(success_probability * 100, 1)
            },
            'species_recommendations': species_recommendations,
            'planting_design': {
                'total_trees': optimal_density['total_trees'],
                'trees_per_hectare': optimal_density['density_per_ha'],
                'spacing_meters': optimal_density['spacing'],
                'estimated_cost': optimal_density['estimated_cost']
            },
            'implementation_timeline': planting_timeline,
            'expected_outcomes': {
                'survival_rate_1_year': round(success_probability * 0.9, 2),
                'survival_rate_5_years': round(success_probability * 0.8, 2),
                'carbon_sequestration_20_years': round(optimal_density['total_trees'] * 2.5, 1),
                'ecosystem_services_value': round(optimal_density['total_trees'] * 50, 0)  # USD
            }
        }
    
    def _parse_location(self, location_str: str) -> Dict:
        """Parse location string to extract coordinates"""
        try:
            if ',' in location_str:
                coords = location_str.split(',')
                return {'lat': float(coords[0].strip()), 'lon': float(coords[1].strip())}
        except:
            pass
        
        return {'lat': 19.0176, 'lon': 72.8562}  # Default Mumbai coordinates
    
    def _calculate_environmental_stress(self, location: Dict) -> float:
        """Calculate environmental stress factor affecting growth"""
        # Mock calculation based on location (in production, use real environmental data)
        lat, lon = location['lat'], location['lon']
        
        # Coastal stress factors
        if self._is_coastal(lat, lon):
            salinity_stress = random.uniform(0.8, 1.0)
            cyclone_risk = random.uniform(0.9, 1.0)
        else:
            salinity_stress = 1.0
            cyclone_risk = 1.0
        
        pollution_stress = random.uniform(0.85, 1.0)
        climate_stress = random.uniform(0.9, 1.0)
        
        return salinity_stress * cyclone_risk * pollution_stress * climate_stress
    
    def _is_coastal(self, lat: float, lon: float) -> bool:
        """Check if location is coastal"""
        west_coast = 68 <= lon <= 76 and 8 <= lat <= 24
        east_coast = 77 <= lon <= 93 and 8 <= lat <= 22
        return west_coast or east_coast
    
    def _calculate_survival_rate(self, age: int, env_stress: float, species_params: Dict) -> float:
        """Calculate survival rate based on age and environmental stress"""
        base_survival = species_params['survival_rate_baseline']
        
        # Age factor (higher mortality in first few years)
        if age <= 2:
            age_factor = 0.7
        elif age <= 5:
            age_factor = 0.9
        else:
            age_factor = 0.95
        
        # Environmental stress factor
        stress_factor = env_stress
        
        # Random events (diseases, extreme weather)
        random_factor = random.uniform(0.98, 1.0)
        
        survival_rate = base_survival * age_factor * stress_factor * random_factor
        return max(0.1, min(1.0, survival_rate))  # Ensure reasonable bounds
    
    def _generate_confidence_intervals(self, predictions: List[Dict]) -> Dict:
        """Generate confidence intervals for predictions"""
        confidence_bands = {
            'lower_95': [],
            'upper_95': [],
            'lower_68': [],
            'upper_68': []
        }
        
        for pred in predictions:
            base_value = pred['cumulative_co2']
            
            # Calculate confidence intervals (simplified approach)
            std_dev = base_value * 0.15  # 15% standard deviation
            
            confidence_bands['lower_95'].append(round(base_value - 1.96 * std_dev, 2))
            confidence_bands['upper_95'].append(round(base_value + 1.96 * std_dev, 2))
            confidence_bands['lower_68'].append(round(base_value - 0.68 * std_dev, 2))
            confidence_bands['upper_68'].append(round(base_value + 0.68 * std_dev, 2))
        
        return confidence_bands
    
    def _assess_risk_factors(self, project_data: Dict, location: Dict) -> List[Dict]:
        """Assess various risk factors for the project"""
        risks = []
        
        # Climate change risks
        risks.append({
            'factor': 'Sea Level Rise',
            'probability': 0.3,
            'impact': 'Medium',
            'description': 'Rising sea levels may affect coastal plantations'
        })
        
        # Disease risks
        risks.append({
            'factor': 'Plant Diseases',
            'probability': 0.2,
            'impact': 'Medium',
            'description': 'Fungal and bacterial diseases in humid conditions'
        })
        
        # Extreme weather
        risks.append({
            'factor': 'Cyclones/Storms',
            'probability': 0.15,
            'impact': 'High',
            'description': 'Tropical storms can damage young plantations'
        })
        
        return risks
    
    def _generate_ml_recommendations(self, predictions: List[Dict], project_data: Dict) -> List[str]:
        """Generate ML-based recommendations"""
        recommendations = []
        
        # Analyze prediction trends
        final_survival = predictions[-1]['survival_rate']
        peak_year = max(predictions, key=lambda x: x['annual_co2_total'])['year']
        
        if final_survival < 0.7:
            recommendations.append("Consider species mix optimization to improve survival rates")
            recommendations.append("Implement enhanced monitoring and maintenance program")
        
        if peak_year < 10:
            recommendations.append("Fast-growing species selected - plan for replacement cycle")
        
        recommendations.append(f"Optimal harvest/management intervention around year {peak_year}")
        recommendations.append("Implement adaptive management based on monitoring data")
        
        return recommendations
    
    def _extract_health_indicators(self, project_data: Dict, sensor_data: Optional[Dict]) -> Dict:
        """Extract current health indicators"""
        # Mock health indicators calculation
        base_score = 75 + random.uniform(-15, 20)
        
        indicators = {
            'overall_score': round(base_score, 1),
            'vegetation_index': round(random.uniform(0.4, 0.8), 3),
            'soil_quality': round(random.uniform(60, 90), 1),
            'water_availability': round(random.uniform(65, 95), 1),
            'biodiversity_index': round(random.uniform(0.3, 0.7), 2)
        }
        
        # Incorporate sensor data if available
        if sensor_data:
            sensor_readings = sensor_data.get('sensor_readings', {})
            if 'soil_ph' in sensor_readings:
                ph_status = sensor_readings['soil_ph']['status']
                if ph_status == 'Optimal':
                    indicators['soil_quality'] *= 1.1
                elif ph_status == 'Critical':
                    indicators['soil_quality'] *= 0.8
        
        return indicators
    
    def _calculate_stress_progression(self, project_data: Dict, year: int) -> Dict:
        """Calculate how stress factors change over time"""
        return {
            'salinity': random.uniform(0, 0.4),
            'pollution': random.uniform(0, 0.3),
            'climate_change': year * 0.02,  # Increases over time
            'human_pressure': random.uniform(0, 0.2)
        }
    
    def _categorize_health(self, score: float) -> str:
        """Categorize health score"""
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 55:
            return "Fair"
        elif score >= 40:
            return "Poor"
        else:
            return "Critical"
    
    def _analyze_health_trend(self, predictions: List[Dict]) -> str:
        """Analyze overall health trend"""
        scores = [p['health_score'] for p in predictions]
        
        if scores[-1] > scores[0] + 10:
            return "Strongly Improving"
        elif scores[-1] > scores[0] + 5:
            return "Improving"
        elif scores[-1] < scores[0] - 10:
            return "Declining"
        elif scores[-1] < scores[0] - 5:
            return "Slightly Declining"
        else:
            return "Stable"
    
    def _identify_early_warnings(self, predictions: List[Dict]) -> List[str]:
        """Identify early warning indicators"""
        warnings = []
        
        for pred in predictions[:3]:  # First 3 years
            if pred['health_score'] < 60:
                warnings.append(f"Health score drops below 60 in year {pred['year']}")
            if pred['intervention_needed']:
                warnings.append(f"Intervention needed by year {pred['year']}")
        
        return warnings
    
    def _recommend_species_mix(self, location: Dict, soil: Dict, water: Dict) -> List[Dict]:
        """Recommend optimal species mix"""
        return [
            {
                'species': 'Rhizophora',
                'percentage': 40,
                'suitability_score': 85,
                'primary_benefits': ['High carbon sequestration', 'Wave protection']
            },
            {
                'species': 'Avicennia',
                'percentage': 35,
                'suitability_score': 80,
                'primary_benefits': ['Salt tolerance', 'Rapid establishment']
            },
            {
                'species': 'Mangrove',
                'percentage': 25,
                'suitability_score': 75,
                'primary_benefits': ['Biodiversity support', 'Soil stabilization']
            }
        ]
    
    def _calculate_optimal_density(self, area: float, species_mix: List[Dict]) -> Dict:
        """Calculate optimal planting density"""
        base_density = 2500  # trees per hectare
        total_trees = int(area * base_density)
        
        return {
            'total_trees': total_trees,
            'density_per_ha': base_density,
            'spacing': round(np.sqrt(10000 / base_density), 1),  # spacing in meters
            'estimated_cost': total_trees * 2.5  # USD per tree
        }
    
    def _generate_planting_timeline(self, area: float, density_info: Dict) -> List[Dict]:
        """Generate planting implementation timeline"""
        return [
            {
                'phase': 1,
                'duration_months': 6,
                'area_percentage': 40,
                'activities': ['Site preparation', 'Nursery establishment', 'Initial planting']
            },
            {
                'phase': 2,
                'duration_months': 4,
                'area_percentage': 35,
                'activities': ['Continued planting', 'Monitoring setup', 'Maintenance']
            },
            {
                'phase': 3,
                'duration_months': 3,
                'area_percentage': 25,
                'activities': ['Final planting', 'Infrastructure completion', 'Baseline assessment']
            }
        ]
    
    def _predict_success_probability(self, species_mix: List[Dict], site_conditions: Dict) -> float:
        """Predict overall project success probability"""
        # Mock calculation based on various factors
        species_suitability = np.mean([s['suitability_score'] for s in species_mix]) / 100
        site_factor = random.uniform(0.7, 0.95)
        management_factor = random.uniform(0.8, 0.95)
        
        return species_suitability * site_factor * management_factor

# Global ML predictor instance
ml_predictor = CarbonSequestrationPredictor()