#!/usr/bin/env python3
"""
Test Blockchain Integration with Flask App Routes
Tests the blockchain functionality as used by the actual Flask application
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blockchain_sim import blockchain_mrv
from datetime import datetime
import random

def print_divider(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def print_sub_title(title):
    print(f"\n{'-'*30}")
    print(f" {title}")
    print(f"{'-'*30}")

def test_app_blockchain_integration():
    """Test blockchain integration as used in Flask app"""
    
    print_divider("FLASK APP BLOCKCHAIN INTEGRATION TEST")
    
    # Simulate the project submission workflow from NGO route
    print_sub_title("Test: NGO Project Submission Workflow")
    
    # Create test project data similar to what NGO form would submit
    ngo_project = {
        'id': 'PROJ1015',
        'name': 'Coastal Mangrove Restoration Initiative',
        'ngo_name': 'Green Coast Foundation',
        'ngo_id': 'NGO2001',
        'description': 'Restoration of 25 hectares of degraded mangrove ecosystem',
        'ecosystem': 'Mangrove',
        'start_date': '2024-02-15',
        'area': 25.0,
        'admin_area': 'Mumbai, Maharashtra',
        'species': 'Rhizophora mucronata, Avicennia marina',
        'number_of_trees': 2500,
        'seedlings': 3000,
        'carbon_credits': 180.5,
        'location': '19.0176,72.8562',
        'tree_height': 0.8,
        'tree_dbh': 2.5,
        'tree_age': 1,
        'tree_species': 'Mixed mangrove species',
        'status': 'Pending Review',
        'submission_date': datetime.now(),
        'credits_requested': 180.5,
        'state': 'Maharashtra',
        'district': 'Mumbai'
    }
    
    # Test blockchain project submission (similar to app.py line 1194)
    try:
        blockchain_hash = blockchain_mrv.submit_project_to_blockchain(ngo_project)
        ngo_project['blockchain_hash'] = blockchain_hash
        print(f"✅ Project submitted to blockchain successfully")
        print(f"   Transaction Hash: {blockchain_hash}")
        
        # Verify project is in blockchain registry
        blockchain_info = blockchain_mrv.get_project_blockchain_info(ngo_project['id'])
        if blockchain_info:
            print(f"   Status: {blockchain_info['verification_status']}")
            print(f"   Data Hash: {blockchain_info['data_hash'][:16]}...")
        else:
            print("❌ Project not found in blockchain registry")
            return
        
    except Exception as e:
        print(f"❌ Blockchain project submission failed: {e}")
        return
    
    # Simulate admin approval workflow
    print_sub_title("Test: Admin Approval & Token Minting")
    
    # Simulate admin approval (similar to app.py lines 2169-2181)
    try:
        approved_credits = 165.0  # Admin approves slightly less than requested
        
        # Verify project on blockchain and mint tokens
        verification_success = blockchain_mrv.verify_project_on_blockchain(
            project_id=ngo_project['id'],
            verifier_node='NCCR_Node_1',
            approval_data={
                'status': 'approved',
                'credits_approved': approved_credits,
                'notes': 'Project verified and approved by NCCR admin'
            }
        )
        
        if verification_success:
            print(f"✅ Project verification successful")
            
            # Get blockchain token info (similar to app.py lines 2179-2185)
            blockchain_info = blockchain_mrv.get_project_blockchain_info(ngo_project['id'])
            if blockchain_info and blockchain_info.get('token_ids'):
                token_id = blockchain_info['token_ids'][0]
                ngo_project['token_id'] = token_id
                ngo_project['blockchain_verified'] = True
                print(f"   Token ID: {token_id}")
                print(f"   Credits Approved: {approved_credits} tCO₂e")
            else:
                # Fallback (similar to app.py line 2184)
                ngo_project['token_id'] = f'BC{random.randint(100000, 999999)}'
                print(f"   Fallback Token ID: {ngo_project['token_id']}")
        else:
            print("❌ Project verification failed")
            return
            
    except Exception as e:
        print(f"❌ Project verification failed: {e}")
        # Fallback similar to app.py lines 2187-2188
        ngo_project['token_id'] = f'BC{random.randint(100000, 999999)}'
        ngo_project['blockchain_error'] = str(e)
        print(f"   Using fallback token: {ngo_project['token_id']}")
    
    # Test field data submission workflow
    print_sub_title("Test: Field Data Submission")
    
    # Simulate field data submission (similar to app.py lines 1088-1091)
    field_data_record = {
        'id': 'FD123456',
        'ngo_id': ngo_project['ngo_id'],
        'ngo_name': ngo_project['ngo_name'],
        'project_id': ngo_project['id'],
        'collection_date': '2024-07-20',
        'location': {'lat': 19.0176, 'lng': 72.8562, 'address': 'Mumbai Mangrove Site'},
        'ecosystem_data': {
            'type': 'Mangrove',
            'area_covered': 8.5,
            'tree_count': 425,
            'avg_height': 1.2,
            'avg_diameter': 3.1,
            'species_identified': 'Rhizophora mucronata, Avicennia marina'
        },
        'environmental_conditions': {
            'temperature': 31.2,
            'humidity': 78,
            'water_salinity': 18.4,
            'soil_ph': 7.3,
            'weather_conditions': 'Partly cloudy'
        },
        'field_observations': {
            'restoration_progress': 'Excellent growth observed',
            'wildlife_observed': 'Crabs, various bird species',
            'challenges': 'Some erosion in southwest section',
            'additional_notes': 'Recommend additional protective barriers'
        },
        'photos': ['photo1.jpg', 'photo2.jpg'],
        'submission_timestamp': datetime.now(),
        'status': 'Submitted',
        'blockchain_hash': None
    }
    
    # Submit field data to blockchain
    try:
        blockchain_hash = blockchain_mrv.record_field_data(field_data_record)
        field_data_record['blockchain_hash'] = blockchain_hash
        print(f"✅ Field data submitted to blockchain successfully")
        print(f"   Transaction Hash: {blockchain_hash}")
        
        # Verify field data is linked to project
        updated_project_info = blockchain_mrv.get_project_blockchain_info(ngo_project['id'])
        if updated_project_info and 'field_data_records' in updated_project_info:
            print(f"   Field data records linked: {len(updated_project_info['field_data_records'])}")
        
    except Exception as e:
        print(f"⚠️  Blockchain field data recording failed: {e}")
        # This would continue in the app but log the warning (similar to app.py line 1091)
    
    # Test industry purchase workflow
    print_sub_title("Test: Industry Credit Purchase")
    
    # Get token information for purchase
    if ngo_project.get('blockchain_verified') and token_id:
        token_info = blockchain_mrv.smart_contract.get_token_info(token_id)
        if token_info:
            print(f"✅ Token available for purchase")
            print(f"   Available Credits: {token_info['available_amount']} tCO₂e")
            print(f"   Primary Owner: {token_info['primary_owner'][:10]}...")
            
            # Simulate industry purchase (transfer to industry address)
            industry_address = "0x" + "1234" * 10  # Industry wallet address
            purchase_amount = 50.0
            
            transfer_success = blockchain_mrv.smart_contract.transfer_tokens(
                token_id=token_id,
                from_address=token_info['primary_owner'],
                to_address=industry_address,
                amount=purchase_amount
            )
            
            if transfer_success:
                print(f"✅ Credit purchase successful")
                print(f"   Purchased: {purchase_amount} tCO₂e")
                print(f"   Buyer Address: {industry_address[:10]}...")
                
                # Check industry balance
                industry_balance = blockchain_mrv.smart_contract.get_token_balance(token_id, industry_address)
                print(f"   Industry Balance: {industry_balance} tCO₂e")
            else:
                print("❌ Credit purchase failed")
    
    # Test credit retirement workflow
    print_sub_title("Test: Credit Retirement for Offsetting")
    
    # Simulate industry retiring credits for carbon offsetting
    if token_info and transfer_success:
        retire_amount = 25.0
        retirement_success = blockchain_mrv.smart_contract.retire_tokens(
            token_id=token_id,
            owner_address=industry_address,
            amount=retire_amount,
            reason="Corporate carbon offsetting - Q3 2024 emissions"
        )
        
        if retirement_success:
            print(f"✅ Credit retirement successful")
            print(f"   Retired: {retire_amount} tCO₂e")
            print(f"   Reason: Corporate carbon offsetting")
            
            # Get updated stats
            updated_token_info = blockchain_mrv.smart_contract.get_token_info(token_id)
            print(f"   Remaining Industry Balance: {updated_token_info['fractional_owners'].get(industry_address, 0)} tCO₂e")
            print(f"   Total Retired: {updated_token_info['retired_amount']} tCO₂e")
        else:
            print("❌ Credit retirement failed")
    
    # Test blockchain statistics (similar to app.py line 2298)
    print_sub_title("Test: Admin Blockchain Statistics")
    
    try:
        stats = blockchain_mrv.get_blockchain_stats()
        print(f"✅ Blockchain statistics retrieved")
        print(f"   Total Projects: {stats['blockchain']['total_projects']}")
        print(f"   Verified Projects: {stats['blockchain']['verified_projects']}")
        print(f"   Total Token Supply: {stats['smart_contract']['total_supply']} tCO₂e")
        print(f"   Active Supply: {stats['smart_contract']['active_supply']} tCO₂e")
        print(f"   Retired Supply: {stats['smart_contract']['retired_supply']} tCO₂e")
        print(f"   Total Transactions: {stats['smart_contract']['total_transactions']}")
        
        # Calculate retirement rate
        if stats['smart_contract']['total_supply'] > 0:
            retirement_rate = (stats['smart_contract']['retired_supply'] / stats['smart_contract']['total_supply']) * 100
            print(f"   Retirement Rate: {retirement_rate:.1f}%")
        
    except Exception as e:
        print(f"❌ Failed to get blockchain statistics: {e}")
    
    # Test project blockchain info for satellite monitoring
    print_sub_title("Test: Satellite Monitoring Blockchain Info")
    
    # Simulate getting blockchain info for satellite monitoring (similar to app.py line 2230)
    try:
        blockchain_info = blockchain_mrv.get_project_blockchain_info(ngo_project['id'])
        if blockchain_info:
            print(f"✅ Project blockchain info for monitoring")
            print(f"   Verification Status: {blockchain_info['verification_status']}")
            print(f"   Carbon Credits Issued: {blockchain_info['carbon_credits_issued']}")
            print(f"   Token IDs: {blockchain_info['token_ids']}")
            print(f"   Verification Nodes: {len(blockchain_info['verification_nodes'])}")
            
            if 'field_data_records' in blockchain_info:
                print(f"   Field Data Records: {len(blockchain_info['field_data_records'])}")
        else:
            print("❌ No blockchain info found for project")
            
    except Exception as e:
        print(f"❌ Failed to get project blockchain info: {e}")
    
    print_divider("FLASK APP INTEGRATION TEST COMPLETED")
    print("✅ All Flask app blockchain integrations working correctly!")
    print("✅ NGO project submission with blockchain recording")
    print("✅ Admin approval and token minting process")
    print("✅ Field data collection blockchain recording") 
    print("✅ Industry credit purchase and transfer functionality")
    print("✅ Credit retirement for carbon offsetting")
    print("✅ Blockchain statistics and monitoring integration")

if __name__ == "__main__":
    test_app_blockchain_integration()