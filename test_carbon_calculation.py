#!/usr/bin/env python3
"""
Carbon Calculation API Test Script

This script demonstrates how to test the tree carbon sequestration calculation APIs
implemented in the BlueCarbon NGO platform.
"""

import requests
import json

# API Base URL
BASE_URL = "http://localhost:5000/ngo"

def test_tree_carbon_calculation():
    """Test the tree carbon calculation API with various examples"""
    
    print("🌲 Testing Tree Carbon Sequestration Calculation API")
    print("=" * 60)
    
    # Test cases with different tree specifications
    test_cases = [
        {
            "name": "Large Neem Tree",
            "data": {
                "height": 12.5,
                "dbh": 0.45,
                "latitude": 20.5937,
                "longitude": 78.9629,
                "species": "Neem",
                "age": 25
            }
        },
        {
            "name": "Young Banyan Tree",
            "data": {
                "height": 8.0,
                "dbh": 0.25,
                "latitude": 19.0760,
                "longitude": 72.8777,
                "species": "Banyan",
                "age": 15
            }
        },
        {
            "name": "Mangrove Tree",
            "data": {
                "height": 6.5,
                "dbh": 0.18,
                "latitude": 10.8505,
                "longitude": 76.2711,
                "species": "Rhizophora",
                "age": 10
            }
        },
        {
            "name": "Teak Tree (No Age)",
            "data": {
                "height": 15.2,
                "dbh": 0.52,
                "latitude": 15.2993,
                "longitude": 74.1240,
                "species": "Teak"
            }
        },
        {
            "name": "Unknown Species Tree",
            "data": {
                "height": 10.0,
                "dbh": 0.30,
                "latitude": 28.7041,
                "longitude": 77.1025
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 40)
        
        try:
            # Make API request
            response = requests.post(
                f"{BASE_URL}/calculate/tree_carbon",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result['success']:
                    calc = result['calculation']
                    
                    # Display input parameters
                    print("📊 Input Parameters:")
                    params = calc['input_parameters']
                    print(f"   • Height: {params['height_m']} m")
                    print(f"   • DBH: {params['dbh_m']} m")
                    print(f"   • Location: {params['latitude']}, {params['longitude']}")
                    print(f"   • Species: {params['species']}")
                    print(f"   • Age: {params.get('age_years', 'Not specified')} years")
                    
                    # Display carbon sequestration results
                    print("\n🌱 Carbon Sequestration Results:")
                    carbon = calc['carbon_sequestration']
                    print(f"   • Total CO₂ Sequestered: {carbon['total_co2_sequestered_tonnes']} tonnes")
                    print(f"   • Annual CO₂ Sequestration: {carbon['annual_co2_sequestration_tonnes']} tonnes/year")
                    print(f"   • Climate Factor: {carbon['climate_adjustment_factor']}x")
                    
                    # Display biomass analysis
                    print("\n🔬 Biomass Analysis:")
                    biomass = calc['biomass_analysis']
                    print(f"   • Total Biomass: {biomass['total_biomass_kg']} kg")
                    print(f"   • Above Ground: {biomass['above_ground_biomass_kg']} kg")
                    print(f"   • Below Ground: {biomass['below_ground_biomass_kg']} kg")
                    print(f"   • Carbon Content: {biomass['carbon_content_kg']} kg")
                    
                    # Display environmental impact
                    print("\n🌍 Environmental Impact:")
                    impact = calc['environmental_impact']
                    print(f"   • Car Emissions Offset: {impact['equivalent_car_emissions_offset_days']} days")
                    print(f"   • Tree Years Equivalent: {impact['equivalent_tree_years']}")
                    print(f"   • Economic Value: ${impact['economic_value_usd']}")
                    
                else:
                    print(f"❌ Calculation failed: {result.get('error', 'Unknown error')}")
                    
            else:
                print(f"❌ API request failed with status {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

def test_image_analysis_simulation():
    """Simulate testing image analysis with tree measurements"""
    
    print("\n\n🖼️ Testing Image Analysis with Tree Measurements")
    print("=" * 60)
    
    # Simulate form data that would be sent with an image
    form_data = {
        'height': '10.5',
        'dbh': '0.35',
        'species': 'Neem',
        'age': '20'
    }
    
    print("📝 Simulated Form Data:")
    print(f"   • Tree Height: {form_data['height']} m")
    print(f"   • DBH: {form_data['dbh']} m") 
    print(f"   • Species: {form_data['species']}")
    print(f"   • Age: {form_data['age']} years")
    print("\n💡 This data would be combined with image analysis for precise calculations.")
    print("   When uploaded, the system would:")
    print("   1. Detect if image contains trees using computer vision")
    print("   2. Extract GPS coordinates from EXIF data")
    print("   3. Use provided measurements for scientific calculations")
    print("   4. Validate results against image analysis")

def display_calculation_summary():
    """Display a summary of the calculation methodology"""
    
    print("\n\n📚 Carbon Calculation Methodology Summary")
    print("=" * 60)
    
    methodology = """
🔬 SCIENTIFIC APPROACH:
   • Uses Chave et al. (2014) allometric equations
   • Incorporates species-specific wood density
   • Applies climate zone adjustments
   • Considers tree age for growth rates
   
📐 KEY FORMULAS:
   • AGB = 0.0673 × (ρ × DBH² × H)^0.976
   • Carbon = Biomass × 0.47
   • CO₂ = Carbon × (44/12)
   
🌍 VALIDATION FEATURES:
   • Tree detection in images using computer vision
   • GPS extraction from geo-tagged photos
   • Input validation and error handling
   • Cross-verification with multiple methods
   
🎯 ACCURACY LEVELS:
   • With measurements: ±10-15% accuracy
   • Image estimation: ±20-30% accuracy
   • Overall system: ±20-35% depending on data quality
"""
    
    print(methodology)

def main():
    """Main function to run all tests"""
    
    print("🌿 BlueCarbon Platform - Carbon Calculation Testing")
    print("🔬 Scientific Tree Carbon Sequestration Analysis")
    print("=" * 80)
    
    # Test the carbon calculation API
    test_tree_carbon_calculation()
    
    # Simulate image analysis testing
    test_image_analysis_simulation()
    
    # Display methodology summary
    display_calculation_summary()
    
    print("\n✅ Testing Complete!")
    print("\n📖 For detailed methodology, see:")
    print("   • CARBON_CALCULATION_METHODOLOGY.md")
    print("   • CARBON_CALCULATION_EXAMPLE.md")
    print("\n🚀 To test with real data, start the Flask app:")
    print("   python app_fixed.py")
    print("   Then visit: http://localhost:5000/ngo/projects/new")

if __name__ == "__main__":
    main()