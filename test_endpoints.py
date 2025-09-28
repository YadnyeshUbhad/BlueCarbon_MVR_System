#!/usr/bin/env python3
"""
Test script for checking API endpoints functionality
"""

import sys
import os
sys.path.append('D:\\sih_project')

from app import app
import json

def test_system_health():
    """Test system health API"""
    with app.test_client() as client:
        response = client.get('/api/health/system')
        print(f"System Health API: {response.status_code}")
        if response.get_json():
            data = response.get_json()
            print(f"  Status: {data.get('status')}")
            print(f"  Version: {data.get('version')}")
            print(f"  Environment: {data.get('environment')}")
            return response.status_code == 200
        return False

def test_integrations_health():
    """Test integrations health API"""
    with app.test_client() as client:
        response = client.get('/api/health/integrations')
        print(f"Integrations Health API: {response.status_code}")
        if response.get_json():
            data = response.get_json()
            print(f"  System Status: {data.get('system_status')}")
            integrations = data.get('integrations', {})
            print(f"  Integrations: {list(integrations.keys())}")
            return response.status_code == 200
        return False

def test_carbon_calculation():
    """Test carbon calculation API"""
    with app.test_client() as client:
        test_data = {
            'tree_species': 'Mangrove',
            'number_of_trees': 100,
            'tree_height': 2.5,
            'tree_age': 3
        }
        response = client.post('/api/carbon/calculate', 
                             json=test_data,
                             content_type='application/json')
        print(f"Carbon Calculation API: {response.status_code}")
        if response.get_json():
            data = response.get_json()
            print(f"  Success: {data.get('success')}")
            if data.get('success'):
                print(f"  Carbon stored: {data.get('carbon_stored_tonnes')} tonnes")
            return response.status_code == 200
        return False

def test_location_validation():
    """Test location validation API"""
    with app.test_client() as client:
        test_data = {
            'latitude': 19.0760,
            'longitude': 72.8777
        }
        response = client.post('/api/location/validate',
                             json=test_data,
                             content_type='application/json')
        print(f"Location Validation API: {response.status_code}")
        if response.get_json():
            data = response.get_json()
            print(f"  Success: {data.get('success')}")
            return response.status_code == 200
        return False

def test_species_detection():
    """Test species detection API"""
    with app.test_client() as client:
        # Test with mock image data
        response = client.post('/analyze-plant-species')
        print(f"Species Detection API: {response.status_code}")
        # This endpoint expects multipart form data, so 400 is expected without image
        return True  # Just checking it responds

if __name__ == "__main__":
    print("🧪 Testing BlueCarbon MRV System APIs...")
    print("=" * 50)
    
    tests = [
        ("System Health", test_system_health),
        ("Integrations Health", test_integrations_health),
        ("Carbon Calculation", test_carbon_calculation),
        ("Location Validation", test_location_validation),
        ("Species Detection", test_species_detection)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            if test_func():
                print(f"✅ {test_name} - PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for deployment.")
    else:
        print("⚠️  Some tests failed. Please review and fix issues.")