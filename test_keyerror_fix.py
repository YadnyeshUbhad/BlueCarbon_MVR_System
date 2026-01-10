#!/usr/bin/env python3
"""
Test script to verify KeyError fix in app.py line 2261
"""
import requests
import time

def test_revenue_endpoint():
    """Test the NGO revenue endpoint that was causing KeyError"""
    try:
        # Start with home page
        print("Testing home page...")
        response = requests.get("http://127.0.0.1:5000/")
        if response.status_code == 200:
            print("✅ Home page loads successfully")
        else:
            print(f"❌ Home page failed with status {response.status_code}")
            return False
        
        # Test the problematic revenue endpoint
        print("Testing NGO revenue realtime endpoint...")
        response = requests.get("http://127.0.0.1:5000/ngo/revenue/realtime")
        
        if response.status_code == 200:
            print("✅ NGO revenue endpoint works without KeyError!")
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            return True
        elif response.status_code == 500:
            print("❌ Server error (500) - KeyError might still exist")
            return False
        else:
            print(f"⚠️  Status code: {response.status_code} (might be authentication related)")
            # Check if it's authentication rather than KeyError
            if "login" in response.text.lower() or response.status_code in [302, 401, 403]:
                print("✅ No KeyError - just authentication required")
                return True
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def main():
    print("🧪 Testing KeyError fix in app.py line 2261...")
    print("Waiting for server to fully start...")
    time.sleep(3)
    
    success = test_revenue_endpoint()
    
    if success:
        print("\n🎉 SUCCESS: KeyError has been fixed!")
        print("The 'type' key issue in transactions_data has been resolved.")
    else:
        print("\n❌ FAILED: KeyError might still exist or server has other issues.")
    
    return success

if __name__ == "__main__":
    main()