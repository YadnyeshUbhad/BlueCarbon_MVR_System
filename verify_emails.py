#!/usr/bin/env python3
"""
Quick Email Verification Script
Test emails directly in application context to ensure they work properly
"""

import os
import sys
from dotenv import load_dotenv

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import email system
from email_notifications import email_system

def main():
    print("🔍 Verifying Email Configuration...")
    print(f"SMTP Host: {os.getenv('SMTP_HOST')}")
    print(f"SMTP Port: {os.getenv('SMTP_PORT')}")
    print(f"SMTP Username: {os.getenv('SMTP_USERNAME')}")
    print(f"From Email: {os.getenv('FROM_EMAIL')}")
    print(f"From Name: {os.getenv('FROM_NAME')}")
    
    print("\n📧 Testing NGO Registration Email...")
    
    success = email_system.send_ngo_registration_confirmation(
        email="ubhadsatishm@gmail.com",
        name="Satish Ubhadkar",
        org_name="Green Ocean Foundation"
    )
    
    if success:
        print("✅ Email sent successfully!")
        print("📨 Please check your inbox at ubhadsatishm@gmail.com")
    else:
        print("❌ Email sending failed!")
    
    return success

if __name__ == "__main__":
    main()