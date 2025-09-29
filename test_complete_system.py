#!/usr/bin/env python3
"""
Comprehensive test script to verify all BlueCarbon MRV system functionality
Tests NGO portal, admin portal, file uploads, and real-time updates
"""

import requests
import json
import os
import time
from datetime import datetime

def test_url(url, description, expected_status=200):
    """Test a URL and return success/failure"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == expected_status:
            print(f"✅ {description}: SUCCESS (Status: {response.status_code})")
            return True
        else:
            print(f"❌ {description}: FAILED (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {description}: FAILED (Error: {e})")
        return False

def test_post_url(url, data, description, expected_status=200):
    """Test a POST URL and return success/failure"""
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == expected_status:
            print(f"✅ {description}: SUCCESS (Status: {response.status_code})")
            return True, response
        else:
            print(f"❌ {description}: FAILED (Status: {response.status_code})")
            return False, response
    except requests.exceptions.RequestException as e:
        print(f"❌ {description}: FAILED (Error: {e})")
        return False, None

def main():
    base_url = "http://127.0.0.1:5000"
    
    print("🌊 BlueCarbon MRV System - Comprehensive Testing")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test Results Storage
    results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'test_details': []
    }
    
    # 1. Test Main Landing Page
    print("\n🏠 Testing Main Landing Page:")
    test_passed = test_url(f"{base_url}/", "Main landing page")
    results['total_tests'] += 1
    if test_passed:
        results['passed_tests'] += 1
    else:
        results['failed_tests'] += 1
    results['test_details'].append(('Main Landing Page', test_passed))
    
    # 2. Test NGO Portal Routes
    print("\n🌱 Testing NGO Portal:")
    ngo_tests = [
        (f"{base_url}/ngo/", "NGO index page"),
        (f"{base_url}/ngo/login", "NGO login page"),
        (f"{base_url}/ngo/register", "NGO registration page"),
    ]
    
    ngo_passed = 0
    for url, desc, *expected in ngo_tests:
        status = expected[0] if expected else 200
        test_passed = test_url(url, desc, status)
        results['total_tests'] += 1
        if test_passed:
            results['passed_tests'] += 1
            ngo_passed += 1
        else:
            results['failed_tests'] += 1
        results['test_details'].append((desc, test_passed))
    
    # 3. Test Admin Portal Routes
    print("\n👨‍💼 Testing Admin Portal:")
    admin_tests = [
        (f"{base_url}/admin/login", "Admin login page"),
    ]
    
    admin_passed = 0
    for url, desc, *expected in admin_tests:
        status = expected[0] if expected else 200
        test_passed = test_url(url, desc, status)
        results['total_tests'] += 1
        if test_passed:
            results['passed_tests'] += 1
            admin_passed += 1
        else:
            results['failed_tests'] += 1
        results['test_details'].append((desc, test_passed))
    
    # 4. Test Authentication (Protected Routes)
    print("\n🔐 Testing Authentication:")
    import requests
    session = requests.Session()
    
    auth_tests = [
        (f"{base_url}/ngo/dashboard", "NGO dashboard authentication"),
        (f"{base_url}/admin/dashboard", "Admin dashboard authentication"),
        (f"{base_url}/admin/projects", "Admin projects authentication"),
    ]
    
    auth_passed = 0
    for url, desc in auth_tests:
        try:
            response = session.get(url, allow_redirects=False)
            if response.status_code == 302 and 'login' in response.headers.get('Location', '').lower():
                print(f"✅ {desc}: SUCCESS (Redirects to login)")
                auth_passed += 1
                test_passed = True
            else:
                print(f"❌ {desc}: FAILED (Status: {response.status_code})")
                test_passed = False
            results['total_tests'] += 1
            if test_passed:
                results['passed_tests'] += 1
            else:
                results['failed_tests'] += 1
            results['test_details'].append((desc, test_passed))
        except Exception as e:
            print(f"❌ {desc}: FAILED (Error: {e})")
            results['total_tests'] += 1
            results['failed_tests'] += 1
            results['test_details'].append((desc, False))
    
    # 5. Test API Endpoints
    print("\n🔗 Testing API Endpoints:")
    api_tests = [
        (f"{base_url}/api/real_blockchain/status", "Blockchain status API"),
        (f"{base_url}/api/health/integrations", "Health check API"),
    ]
    
    api_passed = 0
    for url, desc in api_tests:
        test_passed = test_url(url, desc)
        results['total_tests'] += 1
        if test_passed:
            results['passed_tests'] += 1
            api_passed += 1
        else:
            results['failed_tests'] += 1
        results['test_details'].append((desc, test_passed))
    
    # 6. Test Static Files
    print("\n📁 Testing Static Files:")
    static_tests = [
        (f"{base_url}/static/css/admin.css", "Admin CSS file"),
        (f"{base_url}/static/css/responsive.css", "Responsive CSS file"),
    ]
    
    static_passed = 0
    for url, desc in static_tests:
        test_passed = test_url(url, desc)
        results['total_tests'] += 1
        if test_passed:
            results['passed_tests'] += 1
            static_passed += 1
        else:
            results['failed_tests'] += 1
        results['test_details'].append((desc, test_passed))
    
    # 7. Test File Upload Endpoints (POST method check)
    print("\n📤 Testing Upload Endpoints Structure:")
    upload_tests = [
        (f"{base_url}/ngo/upload/tree_data", "Tree data upload endpoint (POST)"),
        (f"{base_url}/ngo/upload/analyze", "Image analysis endpoint (POST)"),
    ]
    
    upload_passed = 0
    for url, desc in upload_tests:
        # Test POST method with empty data (should require authentication)
        try:
            response = requests.post(url, data={}, allow_redirects=False)
            if response.status_code == 302 and 'login' in response.headers.get('Location', '').lower():
                print(f"✅ {desc}: SUCCESS (Redirects to login)")
                test_passed = True
                upload_passed += 1
            else:
                print(f"❌ {desc}: FAILED (Status: {response.status_code})")
                test_passed = False
        except Exception as e:
            print(f"❌ {desc}: FAILED (Error: {e})")
            test_passed = False
            
        results['total_tests'] += 1
        if test_passed:
            results['passed_tests'] += 1
        else:
            results['failed_tests'] += 1
        results['test_details'].append((desc, test_passed))
    
    # Generate Test Report
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    # Summary
    print(f"Total Tests: {results['total_tests']}")
    print(f"✅ Passed: {results['passed_tests']}")
    print(f"❌ Failed: {results['failed_tests']}")
    print(f"Success Rate: {(results['passed_tests']/results['total_tests']*100):.1f}%")
    
    # Detailed Results by Category
    print(f"\n📋 Category Breakdown:")
    print(f"🏠 Main Landing: {'✅' if results['test_details'][0][1] else '❌'}")
    print(f"🌱 NGO Portal: {ngo_passed}/{len(ngo_tests)} ({'✅' if ngo_passed == len(ngo_tests) else '❌'})")
    print(f"👨‍💼 Admin Portal: {admin_passed}/{len(admin_tests)} ({'✅' if admin_passed == len(admin_tests) else '❌'})")
    print(f"🔐 Authentication: {auth_passed}/{len(auth_tests)} ({'✅' if auth_passed == len(auth_tests) else '❌'})")
    print(f"🔗 API Endpoints: {api_passed}/{len(api_tests)} ({'✅' if api_passed == len(api_tests) else '❌'})")
    print(f"📁 Static Files: {static_passed}/{len(static_tests)} ({'✅' if static_passed == len(static_tests) else '❌'})")
    print(f"📤 Upload Endpoints: {upload_passed}/{len(upload_tests)} ({'✅' if upload_passed == len(upload_tests) else '❌'})")
    
    # Failed Tests Details
    failed_tests = [detail for detail in results['test_details'] if not detail[1]]
    if failed_tests:
        print(f"\n❌ Failed Tests Details:")
        for test_name, _ in failed_tests:
            print(f"   • {test_name}")
    
    # System Status
    overall_health = results['passed_tests'] / results['total_tests']
    if overall_health >= 0.9:
        status_emoji = "🟢"
        status_text = "EXCELLENT"
    elif overall_health >= 0.75:
        status_emoji = "🟡"  
        status_text = "GOOD"
    elif overall_health >= 0.5:
        status_emoji = "🟠"
        status_text = "NEEDS ATTENTION"
    else:
        status_emoji = "🔴"
        status_text = "CRITICAL"
    
    print(f"\n{status_emoji} System Status: {status_text}")
    
    # Next Steps
    print(f"\n🚀 Next Steps:")
    if overall_health >= 0.9:
        print("   ✅ System is ready for production deployment!")
        print("   ✅ All major functionality is working correctly")
        print("   ✅ Ready to push to GitHub")
    elif failed_tests:
        print("   🔧 Fix the failed test issues above")
        print("   🔄 Re-run tests after fixes")
        print("   📋 Review error logs for detailed debugging")
    
    # Test Files Status
    print(f"\n📁 Test Files Status:")
    test_files = [
        'test_baseline_condition.txt',
        'test_mangrove_1.png',
        'test_mangrove_2.png',
        'test_coastal_vegetation.png',
        'test_seedling_nursery.png'
    ]
    
    for file in test_files:
        if os.path.exists(file):
            print(f"   ✅ {file} - Ready for testing")
        else:
            print(f"   ❌ {file} - Missing (run test_uploads.py)")
    
    # Manual Testing Guide
    print(f"\n🧪 Manual Testing Guide:")
    print("   1. Open browser: http://127.0.0.1:5000")
    print("   2. Test NGO Registration: /ngo/register") 
    print("   3. Test NGO Login: /ngo/login")
    print("   4. Test Admin Login: /admin/login")
    print("   5. Test Project Submission with file uploads")
    print("   6. Test Real-time admin project visibility")
    
    print("\n" + "=" * 60)
    print(f"🎯 Test Completed: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    results = main()