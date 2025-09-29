#!/usr/bin/env python3
"""
Script to test and open NGO portal access
"""

import requests
import webbrowser
import time

def test_and_open_ngo_portal():
    base_url = "http://127.0.0.1:5000"
    
    print("🌊 BlueCarbon MRV - NGO Portal Access Test")
    print("=" * 50)
    
    # Test if server is running
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Server is running (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return False
    
    # Test key NGO portal URLs
    ngo_urls = [
        ("/ngo/", "NGO Portal Home"),
        ("/ngo/login", "NGO Login Page"),
        ("/ngo/register", "NGO Registration Page"),
    ]
    
    print(f"\n🧪 Testing NGO Portal URLs:")
    all_working = True
    
    for url, name in ngo_urls:
        try:
            full_url = f"{base_url}{url}"
            response = requests.get(full_url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: Working (Status: 200)")
                print(f"   URL: {full_url}")
            else:
                print(f"❌ {name}: Failed (Status: {response.status_code})")
                all_working = False
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            all_working = False
    
    if all_working:
        print(f"\n🚀 All NGO portal URLs are working!")
        print(f"Opening NGO portal in your browser...")
        
        # Open the main NGO portal page
        try:
            webbrowser.open(f"{base_url}/ngo/")
            print(f"✅ Browser opened to: {base_url}/ngo/")
        except Exception as e:
            print(f"❌ Could not open browser: {e}")
        
        print(f"\n📋 Direct URLs you can copy-paste:")
        print(f"🏠 NGO Home: {base_url}/ngo/")
        print(f"🔑 NGO Login: {base_url}/ngo/login")
        print(f"📝 NGO Register: {base_url}/ngo/register")
        
        # Test login credentials
        print(f"\n🔐 Test Login Credentials:")
        print(f"📧 Email: ngo@example.org")
        print(f"🔒 Password: password123")
        print(f"(These are demo credentials for testing)")
        
        return True
    else:
        print(f"\n❌ Some URLs are not working. Please check the server.")
        return False

if __name__ == "__main__":
    test_and_open_ngo_portal()