#!/usr/bin/env python3

from db import get_conn
from app import generate_comprehensive_admin_data, admin_industries_data

print("=== Industry Authentication Debug ===")

# Check database users
print("\n1. Industry users in database:")
conn = get_conn()
cur = conn.cursor()
cur.execute("SELECT email, role, name FROM users WHERE role = 'industry'")
rows = cur.fetchall()
for row in rows:
    print(f"   - {dict(row)}")
conn.close()

# Check industry data
print("\n2. Industry data in memory:")
admin_industries_data.clear()  # Clear to regenerate fresh
generate_comprehensive_admin_data()
print(f"   Total industries: {len(admin_industries_data)}")
for i, ind in enumerate(admin_industries_data[:3]):
    print(f"   - Industry {i}: {ind['email']} (status: {ind['status']})")

print("\n3. Looking for test account match:")
test_email = "industry@example.com"
match = next((ind for ind in admin_industries_data if ind['email'] == test_email), None)
if match:
    print(f"   ✅ Found match for {test_email}: {match['name']} (status: {match['status']})")
else:
    print(f"   ❌ No match found for {test_email}")
    print(f"   Available emails: {[ind['email'] for ind in admin_industries_data[:5]]}")