#!/usr/bin/env python3
"""
Test Brevo SMTP Email Configuration
Tests the email functionality with the new Brevo SMTP settings
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import our email system
from email_notifications import email_system

def test_smtp_connection():
    """Test basic SMTP connection to Brevo"""
    print("🧪 Testing Brevo SMTP Connection...")
    
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    print(f"SMTP Host: {smtp_host}")
    print(f"SMTP Port: {smtp_port}")
    print(f"SMTP Username: {smtp_username}")
    print(f"SMTP Password: {'*' * len(smtp_password) if smtp_password else 'Not set'}")
    
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            print("✅ Connected to SMTP server")
            
            server.starttls()
            print("✅ TLS enabled")
            
            server.login(smtp_username, smtp_password)
            print("✅ Authentication successful")
            
        print("🎉 SMTP connection test passed!")
        return True
        
    except Exception as e:
        print(f"❌ SMTP connection failed: {str(e)}")
        return False

def test_simple_email():
    """Test sending a simple email"""
    print("\n📧 Testing Simple Email Send...")
    
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('FROM_EMAIL')
    
    # Test email - replace with your email for testing
    test_email = "ubhadsatishm@gmail.com"  # Your registered email
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = f"BlueCarbon MRV Test <{from_email}>"
        msg['To'] = test_email
        msg['Subject'] = "🧪 BlueCarbon MRV - Email Test"
        
        html_content = """
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #0077B6;">🌊 Email Test Successful!</h2>
            <p>This is a test email from your BlueCarbon MRV Platform.</p>
            <p><strong>Brevo SMTP Configuration:</strong> ✅ Working</p>
            <p><strong>Date:</strong> Today</p>
            <hr>
            <p style="font-size: 12px; color: #666;">
                BlueCarbon MRV Platform<br>
                Automated Test Email
            </p>
        </body>
        </html>
        """
        
        text_content = """
        🌊 Email Test Successful!
        
        This is a test email from your BlueCarbon MRV Platform.
        Brevo SMTP Configuration: ✅ Working
        
        BlueCarbon MRV Platform
        Automated Test Email
        """
        
        # Attach parts
        text_part = MIMEText(text_content, 'plain')
        html_part = MIMEText(html_content, 'html')
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print(f"✅ Test email sent successfully to {test_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test email: {str(e)}")
        return False

def test_email_system():
    """Test our email notification system"""
    print("\n🔧 Testing Email Notification System...")
    
    # Test email - replace with your email for testing
    test_email = "ubhadsatishm@gmail.com"
    
    try:
        success = email_system.send_ngo_registration_confirmation(
            email=test_email,
            name="Test User", 
            org_name="Test NGO Organization"
        )
        
        if success:
            print("✅ Email notification system test passed!")
            print(f"📨 NGO registration confirmation sent to {test_email}")
        else:
            print("❌ Email notification system test failed")
        
        return success
        
    except Exception as e:
        print(f"❌ Email system test failed: {str(e)}")
        return False

def test_project_approval_email():
    """Test project approval notification"""
    print("\n🎉 Testing Project Approval Email...")
    
    test_email = "ubhadsatishm@gmail.com"
    
    try:
        success = email_system.send_project_approval_notification(
            email=test_email,
            ngo_name="Test NGO",
            project_name="Mumbai Mangrove Restoration",
            credits_approved=150,
            token_id="TOKEN123456"
        )
        
        if success:
            print("✅ Project approval email test passed!")
            print(f"📨 Project approval notification sent to {test_email}")
        else:
            print("❌ Project approval email test failed")
        
        return success
        
    except Exception as e:
        print(f"❌ Project approval email test failed: {str(e)}")
        return False

def main():
    """Run all email tests"""
    print("="*60)
    print("🚀 BlueCarbon MRV - Email System Testing")
    print("="*60)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: SMTP Connection
    if test_smtp_connection():
        tests_passed += 1
    
    # Test 2: Simple Email
    if test_simple_email():
        tests_passed += 1
    
    # Test 3: Email System
    if test_email_system():
        tests_passed += 1
    
    # Test 4: Project Approval Email
    if test_project_approval_email():
        tests_passed += 1
    
    # Results
    print("\n" + "="*60)
    print("📊 Test Results:")
    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
    print(f"❌ Tests Failed: {total_tests - tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("\n🎉 All email tests passed! Your Brevo SMTP is working perfectly.")
    else:
        print(f"\n⚠️  {total_tests - tests_passed} test(s) failed. Please check the configuration.")
    
    print("="*60)
    
    return tests_passed == total_tests

if __name__ == "__main__":
    main()