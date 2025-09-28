"""
Real-time Carbon Impact Calculator for BlueCarbon MRV Platform
Dynamic carbon credit calculator with real-time pricing, impact metrics, and environmental benefit projections
"""

import datetime
import json
import math
import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

class ProjectType(Enum):
    MANGROVE_RESTORATION = "mangrove_restoration"
    FOREST_CONSERVATION = "forest_conservation"
    REFORESTATION = "reforestation"
    WETLAND_PROTECTION = "wetland_protection"
    COASTAL_PROTECTION = "coastal_protection"
    BLUE_CARBON = "blue_carbon"
    AGROFORESTRY = "agroforestry"
    URBAN_FORESTRY = "urban_forestry"

class CarbonCredit(Enum):
    VCS = "verified_carbon_standard"
    GOLD_STANDARD = "gold_standard"
    CDM = "clean_development_mechanism"
    VOLUNTARY = "voluntary_carbon_offset"

@dataclass
class ProjectParameters:
    project_type: ProjectType
    area_hectares: float
    duration_years: int
    location: str
    latitude: float
    longitude: float
    climate_zone: str
    soil_type: str
    existing_carbon_stock: Optional[float] = None
    baseline_emissions: Optional[float] = None
    
@dataclass
class CarbonCalculationResult:
    total_co2_sequestered: float  # tonnes CO2 equivalent
    annual_sequestration_rate: float  # tonnes CO2/year
    carbon_credits_generated: float
    estimated_revenue: float  # USD
    environmental_benefits: Dict[str, Any]
    calculation_timestamp: datetime.datetime
    confidence_level: float  # 0-100%
    methodology: str
    verification_requirements: List[str]
    
@dataclass
class RealTimePricing:
    carbon_price_usd: float
    price_trend: str  # "increasing", "decreasing", "stable"
    market_volatility: float  # 0-1
    last_updated: datetime.datetime
    source: str
    regional_adjustments: Dict[str, float]

class CarbonSequestrationModels:
    """Advanced carbon sequestration calculation models"""
    
    # Carbon sequestration rates by project type (tonnes CO2/ha/year)
    BASE_SEQUESTRATION_RATES = {
        ProjectType.MANGROVE_RESTORATION: 6.8,
        ProjectType.FOREST_CONSERVATION: 4.5,
        ProjectType.REFORESTATION: 5.2,
        ProjectType.WETLAND_PROTECTION: 7.2,
        ProjectType.COASTAL_PROTECTION: 8.1,
        ProjectType.BLUE_CARBON: 9.3,
        ProjectType.AGROFORESTRY: 3.8,
        ProjectType.URBAN_FORESTRY: 2.1,
    }
    
    # Climate zone multipliers
    CLIMATE_MULTIPLIERS = {
        'tropical': 1.3,
        'subtropical': 1.1,
        'temperate': 1.0,
        'boreal': 0.7,
        'arid': 0.4,
        'semi_arid': 0.6
    }
    
    # Soil type multipliers
    SOIL_MULTIPLIERS = {
        'organic_rich': 1.2,
        'clay': 1.1,
        'loam': 1.0,
        'sandy': 0.8,
        'rocky': 0.6,
        'waterlogged': 1.4  # for blue carbon projects
    }
    
    @staticmethod
    def calculate_baseline_sequestration(project_type: ProjectType, area: float, 
                                       climate_zone: str, soil_type: str) -> float:
        """Calculate baseline annual carbon sequestration"""
        base_rate = CarbonSequestrationModels.BASE_SEQUESTRATION_RATES[project_type]
        climate_mult = CarbonSequestrationModels.CLIMATE_MULTIPLIERS.get(climate_zone, 1.0)
        soil_mult = CarbonSequestrationModels.SOIL_MULTIPLIERS.get(soil_type, 1.0)
        
        return base_rate * area * climate_mult * soil_mult
    
    @staticmethod
    def apply_age_factor(base_rate: float, year: int, project_type: ProjectType) -> float:
        """Apply age-dependent growth curve"""
        if project_type in [ProjectType.MANGROVE_RESTORATION, ProjectType.REFORESTATION]:
            # S-curve for tree growth
            max_rate = base_rate * 1.5
            growth_factor = 1 / (1 + math.exp(-0.5 * (year - 8)))
            return base_rate * 0.3 + (max_rate - base_rate * 0.3) * growth_factor
        elif project_type == ProjectType.FOREST_CONSERVATION:
            # Steady rate with slight decline over time
            return base_rate * (1 - 0.01 * year) if year <= 50 else base_rate * 0.5
        else:
            # Linear growth for other project types
            return base_rate * min(1 + 0.02 * year, 1.4)

class MarketPricingEngine:
    """Real-time carbon credit pricing engine"""
    
    def __init__(self):
        self.base_prices = {
            CarbonCredit.VCS: 25.50,
            CarbonCredit.GOLD_STANDARD: 32.80,
            CarbonCredit.CDM: 18.20,
            CarbonCredit.VOLUNTARY: 15.90
        }
        
        # Regional price adjustments
        self.regional_premiums = {
            'north_america': 1.2,
            'europe': 1.15,
            'asia_pacific': 1.0,
            'latin_america': 0.95,
            'africa': 0.9,
            'middle_east': 0.85
        }
        
        # Project type premiums
        self.project_premiums = {
            ProjectType.BLUE_CARBON: 1.4,
            ProjectType.MANGROVE_RESTORATION: 1.3,
            ProjectType.WETLAND_PROTECTION: 1.2,
            ProjectType.FOREST_CONSERVATION: 1.1,
            ProjectType.REFORESTATION: 1.0,
            ProjectType.COASTAL_PROTECTION: 1.25,
            ProjectType.AGROFORESTRY: 0.9,
            ProjectType.URBAN_FORESTRY: 0.8,
        }
    
    def get_current_pricing(self) -> RealTimePricing:
        """Get current real-time carbon credit pricing"""
        # Simulate real-time pricing with some volatility
        base_vcs_price = self.base_prices[CarbonCredit.VCS]
        
        # Add market volatility (±15%)
        volatility = random.uniform(-0.15, 0.15)
        current_price = base_vcs_price * (1 + volatility)
        
        # Determine trend
        trend_indicator = random.choice(['increasing', 'decreasing', 'stable', 'stable', 'stable'])  # Bias toward stable
        
        return RealTimePricing(
            carbon_price_usd=round(current_price, 2),
            price_trend=trend_indicator,
            market_volatility=abs(volatility),
            last_updated=datetime.datetime.now(),
            source="BlueCarbon MRV Real-time Market Data",
            regional_adjustments=self.regional_premiums
        )
    
    def calculate_project_price(self, project_type: ProjectType, region: str, 
                               credit_standard: CarbonCredit = CarbonCredit.VCS) -> float:
        """Calculate project-specific carbon credit price"""
        base_price = self.base_prices[credit_standard]
        
        # Apply regional adjustment
        regional_mult = self.regional_premiums.get(region, 1.0)
        
        # Apply project type premium
        project_mult = self.project_premiums.get(project_type, 1.0)
        
        # Market volatility
        volatility = random.uniform(-0.08, 0.12)  # Slight bias toward increase
        
        final_price = base_price * regional_mult * project_mult * (1 + volatility)
        
        return round(final_price, 2)

class EnvironmentalImpactCalculator:
    """Calculate additional environmental benefits beyond carbon"""
    
    @staticmethod
    def calculate_biodiversity_impact(project_type: ProjectType, area: float) -> Dict[str, float]:
        """Calculate biodiversity conservation impact"""
        biodiversity_factors = {
            ProjectType.MANGROVE_RESTORATION: 2.1,
            ProjectType.WETLAND_PROTECTION: 1.8,
            ProjectType.FOREST_CONSERVATION: 1.5,
            ProjectType.BLUE_CARBON: 2.3,
            ProjectType.COASTAL_PROTECTION: 1.7,
            ProjectType.REFORESTATION: 1.2,
            ProjectType.AGROFORESTRY: 1.0,
            ProjectType.URBAN_FORESTRY: 0.6,
        }
        
        factor = biodiversity_factors.get(project_type, 1.0)
        
        return {
            'habitat_area_protected': area * factor,
            'species_diversity_index': factor * 100,
            'ecosystem_connectivity_score': min(100, area * factor * 0.5)
        }
    
    @staticmethod
    def calculate_water_impact(project_type: ProjectType, area: float) -> Dict[str, float]:
        """Calculate water quality and quantity impact"""
        water_factors = {
            ProjectType.MANGROVE_RESTORATION: 1.9,
            ProjectType.WETLAND_PROTECTION: 2.2,
            ProjectType.COASTAL_PROTECTION: 1.5,
            ProjectType.FOREST_CONSERVATION: 1.3,
            ProjectType.REFORESTATION: 1.1,
            ProjectType.BLUE_CARBON: 1.8,
            ProjectType.AGROFORESTRY: 0.9,
            ProjectType.URBAN_FORESTRY: 0.7,
        }
        
        factor = water_factors.get(project_type, 1.0)
        
        return {
            'water_filtration_capacity': area * factor * 1000,  # liters/day
            'flood_protection_value': area * factor * 500,  # USD/year
            'groundwater_recharge': area * factor * 800  # liters/year
        }
    
    @staticmethod
    def calculate_soil_impact(project_type: ProjectType, area: float) -> Dict[str, float]:
        """Calculate soil health and erosion prevention impact"""
        soil_factors = {
            ProjectType.AGROFORESTRY: 1.8,
            ProjectType.REFORESTATION: 1.5,
            ProjectType.FOREST_CONSERVATION: 1.3,
            ProjectType.COASTAL_PROTECTION: 1.4,
            ProjectType.MANGROVE_RESTORATION: 1.2,
            ProjectType.WETLAND_PROTECTION: 1.1,
            ProjectType.BLUE_CARBON: 1.0,
            ProjectType.URBAN_FORESTRY: 0.8,
        }
        
        factor = soil_factors.get(project_type, 1.0)
        
        return {
            'soil_erosion_prevented': area * factor * 2.5,  # tonnes/year
            'soil_organic_matter_increase': area * factor * 0.3,  # percentage points
            'nutrient_retention_value': area * factor * 150  # USD/year
        }

class CarbonImpactCalculator:
    """Main carbon impact calculation engine"""
    
    def __init__(self):
        self.sequestration_models = CarbonSequestrationModels()
        self.pricing_engine = MarketPricingEngine()
        self.environmental_calculator = EnvironmentalImpactCalculator()
    
    def calculate_project_impact(self, parameters: ProjectParameters, 
                                credit_standard: CarbonCredit = CarbonCredit.VCS) -> CarbonCalculationResult:
        """Calculate comprehensive carbon impact for a project"""
        
        # 1. Calculate baseline carbon sequestration
        annual_base_rate = self.sequestration_models.calculate_baseline_sequestration(
            parameters.project_type, 
            parameters.area_hectares,
            parameters.climate_zone, 
            parameters.soil_type
        )
        
        # 2. Calculate total sequestration over project lifetime
        total_sequestration = 0
        yearly_rates = []
        
        for year in range(1, parameters.duration_years + 1):
            yearly_rate = self.sequestration_models.apply_age_factor(
                annual_base_rate, year, parameters.project_type
            )
            yearly_rates.append(yearly_rate)
            total_sequestration += yearly_rate
        
        # 3. Apply additionality factor (only count additional carbon beyond baseline)
        additionality_factor = self._calculate_additionality(parameters)
        total_additional_sequestration = total_sequestration * additionality_factor
        
        # 4. Convert to carbon credits (apply buffer and uncertainty deductions)
        buffer_factor = 0.85  # 15% buffer for uncertainty
        carbon_credits = total_additional_sequestration * buffer_factor
        
        # 5. Calculate revenue using real-time pricing
        region = self._determine_region(parameters.latitude, parameters.longitude)
        credit_price = self.pricing_engine.calculate_project_price(
            parameters.project_type, region, credit_standard
        )
        estimated_revenue = carbon_credits * credit_price
        
        # 6. Calculate environmental co-benefits
        environmental_benefits = self._calculate_environmental_benefits(parameters)
        
        # 7. Determine confidence level
        confidence_level = self._calculate_confidence(parameters, total_sequestration)
        
        # 8. Generate verification requirements
        verification_requirements = self._generate_verification_requirements(
            parameters, carbon_credits
        )
        
        return CarbonCalculationResult(
            total_co2_sequestered=round(total_additional_sequestration, 2),
            annual_sequestration_rate=round(sum(yearly_rates) / len(yearly_rates), 2),
            carbon_credits_generated=round(carbon_credits, 2),
            estimated_revenue=round(estimated_revenue, 2),
            environmental_benefits=environmental_benefits,
            calculation_timestamp=datetime.datetime.now(),
            confidence_level=round(confidence_level, 1),
            methodology=f"{parameters.project_type.value}_methodology_v2.1",
            verification_requirements=verification_requirements
        )
    
    def _calculate_additionality(self, parameters: ProjectParameters) -> float:
        """Calculate additionality factor (how much is truly additional)"""
        # Simplified additionality calculation
        base_additionality = 0.75  # Base 75% additionality
        
        # Adjust based on project type
        additionality_adjustments = {
            ProjectType.BLUE_CARBON: 0.95,
            ProjectType.MANGROVE_RESTORATION: 0.90,
            ProjectType.WETLAND_PROTECTION: 0.85,
            ProjectType.REFORESTATION: 0.80,
            ProjectType.FOREST_CONSERVATION: 0.70,
            ProjectType.COASTAL_PROTECTION: 0.85,
            ProjectType.AGROFORESTRY: 0.75,
            ProjectType.URBAN_FORESTRY: 0.60,
        }
        
        return additionality_adjustments.get(parameters.project_type, base_additionality)
    
    def _determine_region(self, latitude: float, longitude: float) -> str:
        """Determine region based on coordinates"""
        if -90 <= latitude <= 90 and -180 <= longitude <= 180:
            if latitude > 45:
                return 'north_america' if longitude < 0 else 'europe'
            elif latitude > 23.5:
                if longitude < -60:
                    return 'north_america'
                elif longitude < 40:
                    return 'europe'
                else:
                    return 'asia_pacific'
            elif latitude > -23.5:
                if longitude < -60:
                    return 'latin_america'
                elif longitude < 40:
                    return 'africa'
                else:
                    return 'asia_pacific'
            else:
                if longitude < 0:
                    return 'latin_america'
                elif longitude < 40:
                    return 'africa'
                else:
                    return 'asia_pacific'
        return 'global'
    
    def _calculate_environmental_benefits(self, parameters: ProjectParameters) -> Dict[str, Any]:
        """Calculate comprehensive environmental co-benefits"""
        biodiversity = self.environmental_calculator.calculate_biodiversity_impact(
            parameters.project_type, parameters.area_hectares
        )
        
        water = self.environmental_calculator.calculate_water_impact(
            parameters.project_type, parameters.area_hectares
        )
        
        soil = self.environmental_calculator.calculate_soil_impact(
            parameters.project_type, parameters.area_hectares
        )
        
        # Calculate economic value of co-benefits
        economic_value = (
            biodiversity.get('ecosystem_connectivity_score', 0) * 50 +  # USD per score point
            water.get('flood_protection_value', 0) +
            soil.get('nutrient_retention_value', 0)
        )
        
        return {
            'biodiversity': biodiversity,
            'water_impact': water,
            'soil_health': soil,
            'total_economic_value': round(economic_value, 2),
            'sdg_contributions': self._calculate_sdg_impact(parameters)
        }
    
    def _calculate_sdg_impact(self, parameters: ProjectParameters) -> List[Dict[str, Any]]:
        """Calculate contribution to UN Sustainable Development Goals"""
        sdg_mappings = {
            ProjectType.BLUE_CARBON: [
                {'goal': 13, 'name': 'Climate Action', 'impact_score': 95},
                {'goal': 14, 'name': 'Life Below Water', 'impact_score': 90},
                {'goal': 15, 'name': 'Life on Land', 'impact_score': 85},
                {'goal': 6, 'name': 'Clean Water and Sanitation', 'impact_score': 70},
            ],
            ProjectType.MANGROVE_RESTORATION: [
                {'goal': 13, 'name': 'Climate Action', 'impact_score': 90},
                {'goal': 14, 'name': 'Life Below Water', 'impact_score': 95},
                {'goal': 15, 'name': 'Life on Land', 'impact_score': 85},
                {'goal': 1, 'name': 'No Poverty', 'impact_score': 60},
            ],
            ProjectType.FOREST_CONSERVATION: [
                {'goal': 13, 'name': 'Climate Action', 'impact_score': 85},
                {'goal': 15, 'name': 'Life on Land', 'impact_score': 95},
                {'goal': 6, 'name': 'Clean Water and Sanitation', 'impact_score': 75},
                {'goal': 8, 'name': 'Decent Work and Economic Growth', 'impact_score': 55},
            ]
        }
        
        return sdg_mappings.get(parameters.project_type, [
            {'goal': 13, 'name': 'Climate Action', 'impact_score': 80}
        ])
    
    def _calculate_confidence(self, parameters: ProjectParameters, total_sequestration: float) -> float:
        """Calculate confidence level for the calculation"""
        base_confidence = 85.0
        
        # Adjust based on data availability
        if parameters.existing_carbon_stock:
            base_confidence += 5
        if parameters.baseline_emissions:
            base_confidence += 5
        
        # Adjust based on project type (some have better established methodologies)
        confidence_adjustments = {
            ProjectType.FOREST_CONSERVATION: 5,
            ProjectType.REFORESTATION: 3,
            ProjectType.BLUE_CARBON: -2,  # Less established methodology
            ProjectType.URBAN_FORESTRY: -5
        }
        
        adjustment = confidence_adjustments.get(parameters.project_type, 0)
        
        return min(98, max(60, base_confidence + adjustment))
    
    def _generate_verification_requirements(self, parameters: ProjectParameters, 
                                          carbon_credits: float) -> List[str]:
        """Generate project-specific verification requirements"""
        requirements = [
            "Third-party verification by accredited body",
            "Annual monitoring reports with satellite imagery",
            "Baseline assessment documentation",
            "Additionality demonstration"
        ]
        
        # Add project-specific requirements
        if parameters.project_type in [ProjectType.BLUE_CARBON, ProjectType.MANGROVE_RESTORATION]:
            requirements.extend([
                "Tidal gauge measurements",
                "Sediment core analysis",
                "Water quality monitoring"
            ])
        
        if parameters.project_type in [ProjectType.FOREST_CONSERVATION, ProjectType.REFORESTATION]:
            requirements.extend([
                "Forest inventory measurements",
                "Tree growth monitoring",
                "Biodiversity surveys"
            ])
        
        if carbon_credits > 10000:  # Large projects
            requirements.extend([
                "Independent environmental impact assessment",
                "Community stakeholder consultation records",
                "Buffer pool contribution documentation"
            ])
        
        return requirements

class CarbonCalculatorInterface:
    """User interface for the carbon calculator"""
    
    def __init__(self):
        self.calculator = CarbonImpactCalculator()
    
    def quick_estimate(self, project_type: str, area: float, duration: int, 
                      location: str = "global", climate: str = "temperate", 
                      soil: str = "loam") -> Dict[str, Any]:
        """Generate a quick carbon impact estimate"""
        
        try:
            # Convert string to enum
            project_enum = ProjectType(project_type.lower().replace(" ", "_"))
        except ValueError:
            project_enum = ProjectType.FOREST_CONSERVATION
        
        # Create default parameters
        parameters = ProjectParameters(
            project_type=project_enum,
            area_hectares=area,
            duration_years=duration,
            location=location,
            latitude=0.0,  # Default coordinates
            longitude=0.0,
            climate_zone=climate,
            soil_type=soil
        )
        
        # Calculate impact
        result = self.calculator.calculate_project_impact(parameters)
        
        # Format for easy consumption
        return {
            'summary': {
                'total_co2_sequestered': result.total_co2_sequestered,
                'carbon_credits': result.carbon_credits_generated,
                'estimated_revenue_usd': result.estimated_revenue,
                'annual_rate': result.annual_sequestration_rate
            },
            'environmental_benefits': result.environmental_benefits,
            'confidence_level': result.confidence_level,
            'methodology': result.methodology,
            'calculation_timestamp': result.calculation_timestamp.isoformat()
        }
    
    def detailed_analysis(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform detailed carbon impact analysis with all parameters"""
        
        parameters = ProjectParameters(
            project_type=ProjectType(project_data['project_type']),
            area_hectares=project_data['area_hectares'],
            duration_years=project_data['duration_years'],
            location=project_data.get('location', 'Unknown'),
            latitude=project_data.get('latitude', 0.0),
            longitude=project_data.get('longitude', 0.0),
            climate_zone=project_data.get('climate_zone', 'temperate'),
            soil_type=project_data.get('soil_type', 'loam'),
            existing_carbon_stock=project_data.get('existing_carbon_stock'),
            baseline_emissions=project_data.get('baseline_emissions')
        )
        
        result = self.calculator.calculate_project_impact(parameters)
        
        # Get current market pricing
        pricing = self.calculator.pricing_engine.get_current_pricing()
        
        return {
            'calculation_result': asdict(result),
            'market_pricing': asdict(pricing),
            'project_parameters': asdict(parameters),
            'recommendations': self._generate_recommendations(result, parameters)
        }
    
    def _generate_recommendations(self, result: CarbonCalculationResult, 
                                parameters: ProjectParameters) -> List[str]:
        """Generate recommendations for improving carbon impact"""
        recommendations = []
        
        if result.confidence_level < 80:
            recommendations.append("Consider conducting detailed baseline studies to improve calculation confidence")
        
        if result.carbon_credits_generated < 1000:
            recommendations.append("Consider expanding project area or duration to increase carbon credit generation")
        
        if parameters.project_type not in [ProjectType.BLUE_CARBON, ProjectType.MANGROVE_RESTORATION]:
            recommendations.append("Consider blue carbon projects for higher sequestration rates")
        
        if result.environmental_benefits['total_economic_value'] < 10000:
            recommendations.append("Explore opportunities to enhance co-benefits for additional revenue streams")
        
        return recommendations

# Demo function
def demo_carbon_calculator():
    """Demonstrate the carbon impact calculator"""
    calculator = CarbonCalculatorInterface()
    
    print("=== Real-time Carbon Impact Calculator Demo ===\n")
    
    # Quick estimate
    print("Quick Estimate for Mangrove Restoration Project:")
    quick_result = calculator.quick_estimate(
        project_type="mangrove_restoration",
        area=100,
        duration=20,
        location="Southeast Asia",
        climate="tropical",
        soil="waterlogged"
    )
    
    print(f"Total CO2 Sequestered: {quick_result['summary']['total_co2_sequestered']} tonnes")
    print(f"Carbon Credits Generated: {quick_result['summary']['carbon_credits']}")
    print(f"Estimated Revenue: ${quick_result['summary']['estimated_revenue_usd']:,.2f}")
    print(f"Confidence Level: {quick_result['confidence_level']}%")
    
    # Detailed analysis
    detailed_data = {
        'project_type': 'blue_carbon',
        'area_hectares': 250,
        'duration_years': 30,
        'location': 'Sundarbans, India',
        'latitude': 21.9497,
        'longitude': 88.2314,
        'climate_zone': 'tropical',
        'soil_type': 'waterlogged',
        'existing_carbon_stock': 150.0,
        'baseline_emissions': 50.0
    }
    
    print(f"\nDetailed Analysis for Blue Carbon Project:")
    detailed_result = calculator.detailed_analysis(detailed_data)
    calc_result = detailed_result['calculation_result']
    
    print(f"Total CO2 Sequestered: {calc_result['total_co2_sequestered']} tonnes")
    print(f"Annual Sequestration Rate: {calc_result['annual_sequestration_rate']} tonnes/year")
    print(f"Carbon Credits: {calc_result['carbon_credits_generated']}")
    print(f"Revenue Estimate: ${calc_result['estimated_revenue']:,.2f}")
    
    env_benefits = calc_result['environmental_benefits']
    print(f"Environmental Co-benefits Value: ${env_benefits['total_economic_value']:,.2f}")
    
    return calculator

if __name__ == "__main__":
    demo_carbon_calculator()