#!/usr/bin/env python3
"""
Test script for Location Management System
Tests coordinate validation, geocoding, and area calculation
"""

from location_manager import location_manager
import json

def test_coordinate_validation():
    """Test coordinate validation for coastal areas"""
    print("🗺️  Testing Coordinate Validation...")
    
    # Test cases: [lat, lng, expected_result_description]
    test_coordinates = [
        (19.0176, 72.8562, "Mumbai West Coast"),
        (13.0827, 80.2707, "Chennai East Coast"), 
        (22.2587, 91.7832, "Sundarbans East Coast"),
        (10.5667, 72.6417, "Lakshadweep Islands"),
        (28.6139, 77.2090, "Delhi (non-coastal)"),
        (23.0225, 72.5714, "Ahmedabad (inland)")
    ]
    
    for lat, lng, description in test_coordinates:
        result = location_manager.validate_coordinates(lat, lng)
        status = "✅ Valid" if result['valid'] else "❌ Invalid" 
        coastal = "🌊 Coastal" if result['coastal'] else "🏜️ Inland"
        print(f"   {description}: {status} | {coastal} | Region: {result.get('region', 'Unknown')}")
        if result['recommendations']:
            for rec in result['recommendations'][:2]:  # Show first 2 recommendations
                print(f"      💡 {rec}")
    print()

def test_geocoding():
    """Test location name to coordinate conversion"""
    print("📍 Testing Geocoding...")
    
    test_locations = [
        "Mumbai, Maharashtra",
        "Sundarbans, West Bengal", 
        "Kochi, Kerala",
        "Chennai, Tamil Nadu"
    ]
    
    for location in test_locations:
        result = location_manager.geocode_location(location)
        if result:
            print(f"   {location}: ({result['latitude']:.4f}, {result['longitude']:.4f}) - {result['accuracy']} accuracy")
        else:
            print(f"   {location}: ❌ Not found")
    print()

def test_reverse_geocoding():
    """Test coordinate to location name conversion"""
    print("🔍 Testing Reverse Geocoding...")
    
    test_coordinates = [
        (19.0176, 72.8562, "Mumbai"),
        (13.0827, 80.2707, "Chennai"),
        (9.9312, 76.2673, "Kochi")
    ]
    
    for lat, lng, expected in test_coordinates:
        result = location_manager.reverse_geocode(lat, lng)
        if result:
            print(f"   ({lat}, {lng}) -> {result.get('city', 'Unknown')}, {result.get('state', 'Unknown')}")
        else:
            print(f"   ({lat}, {lng}) -> ❌ Location not found")
    print()

def test_suitable_locations():
    """Test finding suitable locations for ecosystems"""
    print("🌱 Testing Ecosystem Suitable Locations...")
    
    ecosystems = ['mangrove', 'seagrass', 'coastal_wetlands']
    
    for ecosystem in ecosystems:
        locations = location_manager.find_suitable_locations(ecosystem)
        print(f"   {ecosystem.title()}:")
        for loc in locations[:3]:  # Show top 3
            print(f"      • {loc['region']}: {loc['suitability_score']:.2f} score, {loc['estimated_area_available']:.0f} ha")
    print()

def test_area_calculation():
    """Test polygon area calculation"""
    print("📐 Testing Area Calculation...")
    
    # Test polygon coordinates (roughly a square in Mumbai coastal area)
    test_polygon = [
        (19.0176, 72.8562),  # Mumbai center
        (19.0276, 72.8562),  # North
        (19.0276, 72.8662),  # Northeast  
        (19.0176, 72.8662),  # East
        (19.0176, 72.8562)   # Back to start
    ]
    
    area = location_manager.calculate_area_from_coordinates(test_polygon)
    print(f"   Test polygon area: {area:.2f} hectares ({area * 2.47:.2f} acres)")
    print()

def test_project_recommendations():
    """Test comprehensive project location recommendations"""
    print("📋 Testing Project Location Recommendations...")
    
    test_project = {
        'latitude': 19.0176,
        'longitude': 72.8562,
        'ecosystem': 'mangrove',
        'area': 25.5,
        'state': 'Maharashtra'
    }
    
    recommendations = location_manager.get_project_location_recommendations(test_project)
    
    print(f"   Location Validation: {'✅ Valid' if recommendations['location_validation']['valid'] else '❌ Invalid'}")
    print(f"   Ecosystem Suitability: {len(recommendations['ecosystem_suitability']['suitable_locations'])} locations found")
    print(f"   Nearby References: {len(recommendations['nearby_references'])} nearby locations")
    print(f"   Optimization Suggestions: {len(recommendations['optimization_suggestions'])} suggestions")
    print(f"   Regulatory Considerations: {len(recommendations['regulatory_considerations'])} items")
    
    # Show a few suggestions
    if recommendations['optimization_suggestions']:
        print("   💡 Top Suggestions:")
        for suggestion in recommendations['optimization_suggestions'][:2]:
            print(f"      • {suggestion}")
    print()

def main():
    """Run all location manager tests"""
    print("="*60)
    print("🌊 BlueCarbon MRV Location Management System Test")
    print("="*60)
    print()
    
    try:
        test_coordinate_validation()
        test_geocoding() 
        test_reverse_geocoding()
        test_suitable_locations()
        test_area_calculation()
        test_project_recommendations()
        
        print("="*60)
        print("✅ All location management tests completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()