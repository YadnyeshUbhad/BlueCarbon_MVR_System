#!/usr/bin/env python3
"""
Manual authentication test to verify login redirections and authentication flow
"""

import requests
import time

def test_authentication():
    """Test authentication flow manually"""
    base_url = "http://127.0.0.1:5000"
    
    print("🔐 BlueCarbon MRV - Authentication Testing")
    print("=" * 50)
    
    # Test 1: Access protected route without login
    print("\n🚫 Test 1: Accessing protected routes without authentication")
    
    protected_routes = [
        ("/ngo/dashboard", "NGO Dashboard"),
        ("/admin/dashboard", "Admin Dashboard"),
        ("/admin/projects", "Admin Projects"),
        ("/ngo/profile", "NGO Profile"),
        ("/ngo/credits", "NGO Credits")
    ]
    
    session = requests.Session()  # Use session to track cookies
    
    for route, name in protected_routes:
        try:
            response = session.get(f"{base_url}{route}", allow_redirects=False)
            if response.status_code == 302:
                # Check redirect location
                location = response.headers.get('Location', '')
                if 'login' in location.lower():
                    print(f"✅ {name}: Correctly redirects to login (302 -> {location})")
                else:
                    print(f"⚠️ {name}: Redirects but not to login (302 -> {location})")
            elif response.status_code == 200:
                print(f"❌ {name}: Allows access without authentication (200)")
            else:
                print(f"❓ {name}: Unexpected status {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
    
    # Test 2: Test login functionality
    print(f"\n🔑 Test 2: Testing login functionality")
    
    # Test NGO login page
    try:
        response = session.get(f"{base_url}/ngo/login")
        if response.status_code == 200 and 'login' in response.text.lower():
            print("✅ NGO Login page accessible")
        else:
            print("❌ NGO Login page issues")
    except Exception as e:
        print(f"❌ NGO Login page error: {e}")
    
    # Test Admin login page
    try:
        response = session.get(f"{base_url}/admin/login")
        if response.status_code == 200 and 'login' in response.text.lower():
            print("✅ Admin Login page accessible")
        else:
            print("❌ Admin Login page issues")
    except Exception as e:
        print(f"❌ Admin Login page error: {e}")
    
    # Test 3: Test POST endpoints without authentication
    print(f"\n📤 Test 3: Testing POST endpoints authentication")
    
    post_endpoints = [
        ("/ngo/upload/tree_data", "Tree Data Upload"),
        ("/ngo/upload/analyze", "Image Analysis"),
        ("/ngo/projects/submit", "Project Submission")
    ]
    
    for endpoint, name in post_endpoints:
        try:
            response = session.post(f"{base_url}{endpoint}", data={}, allow_redirects=False)
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                if 'login' in location.lower():
                    print(f"✅ {name}: Correctly requires authentication (302 -> login)")
                else:
                    print(f"⚠️ {name}: Redirects but not to login (302 -> {location})")
            elif response.status_code == 405:
                print(f"⚠️ {name}: Method not allowed (405) - might need different approach")
            else:
                print(f"❓ {name}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
    
    print(f"\n📊 Summary:")
    print("- If routes return 200 without login: Authentication bypass issue")
    print("- If routes return 302 to login: Authentication working correctly")
    print("- If POST endpoints return 405: Normal behavior (wrong method)")
    
    return True

if __name__ == "__main__":
    test_authentication()