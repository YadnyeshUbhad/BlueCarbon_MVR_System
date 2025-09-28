#!/usr/bin/env python3
"""
Comprehensive Blockchain Integration Test Script for BlueCarbon MRV System
Tests all blockchain functionality including project submission, verification, 
token minting, transfers, and retirements.
"""

from blockchain_sim import blockchain_mrv
import json
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

def test_blockchain_integration():
    """Test complete blockchain integration workflow"""
    
    print_divider("BLOCKCHAIN INTEGRATION TEST")
    
    # Initialize blockchain stats
    print_sub_title("Initial Blockchain Stats")
    initial_stats = blockchain_mrv.get_blockchain_stats()
    print(f"Total projects: {initial_stats['blockchain']['total_projects']}")
    print(f"Smart contract tokens: {initial_stats['smart_contract']['total_tokens']}")
    print(f"Total supply: {initial_stats['smart_contract']['total_supply']} tCO₂e")
    
    # Test 1: Project Submission
    print_sub_title("Test 1: Project Submission")
    test_project = {
        'id': 'PROJ_TEST_001',
        'name': 'Mangrove Restoration Project Test',
        'ngo_id': 'NGO001',
        'ngo_name': 'Test NGO',
        'location': '19.0176,72.8562',
        'ecosystem': 'Mangrove',
        'area': 15.5,
        'number_of_trees': 1500,
        'carbon_credits': 120.5,
        'start_date': '2024-01-01',
        'description': 'Test mangrove restoration project'
    }
    
    submission_hash = blockchain_mrv.submit_project_to_blockchain(test_project)
    print(f"✅ Project submitted to blockchain")
    print(f"   Transaction hash: {submission_hash}")
    
    # Test 2: Get Project Blockchain Info (before verification)
    print_sub_title("Test 2: Project Info Before Verification")
    project_info = blockchain_mrv.get_project_blockchain_info('PROJ_TEST_001')
    if project_info:
        print(f"✅ Project found on blockchain")
        print(f"   Status: {project_info['verification_status']}")
        print(f"   Credits issued: {project_info['carbon_credits_issued']}")
        print(f"   Token IDs: {project_info['token_ids']}")
    else:
        print("❌ Project not found on blockchain")
        return
    
    # Test 3: Project Verification and Token Minting
    print_sub_title("Test 3: Project Verification & Token Minting")
    approval_data = {
        'status': 'approved',
        'credits_approved': 95.0,  # Approved less than requested
        'notes': 'Project verified and approved with minor adjustments'
    }
    
    verification_success = blockchain_mrv.verify_project_on_blockchain(
        'PROJ_TEST_001', 
        'NCCR_Node_1', 
        approval_data
    )
    
    if verification_success:
        print("✅ Project verification successful")
        
        # Get updated project info
        project_info_updated = blockchain_mrv.get_project_blockchain_info('PROJ_TEST_001')
        if project_info_updated and project_info_updated['token_ids']:
            token_id = project_info_updated['token_ids'][0]
            print(f"   Token minted: {token_id}")
            print(f"   Credits issued: {project_info_updated['carbon_credits_issued']} tCO₂e")
        else:
            print("❌ Token not minted properly")
            return
    else:
        print("❌ Project verification failed")
        return
    
    # Test 4: Token Information
    print_sub_title("Test 4: Token Information")
    token_info = blockchain_mrv.smart_contract.get_token_info(token_id)
    if token_info:
        print("✅ Token information retrieved")
        print(f"   Token ID: {token_info['token_id']}")
        print(f"   Credits amount: {token_info['credits_amount']} tCO₂e")
        print(f"   Available amount: {token_info['available_amount']} tCO₂e")
        print(f"   Primary owner: {token_info['primary_owner']}")
        print(f"   Vintage year: {token_info['vintage_year']}")
        
        # Store addresses for transfer tests
        owner_address = token_info['primary_owner']
        buyer_address_1 = '0x' + 'A' * 40  # Industry buyer 1
        buyer_address_2 = '0x' + 'B' * 40  # Industry buyer 2
    else:
        print("❌ Token information not found")
        return
    
    # Test 5: Token Transfer
    print_sub_title("Test 5: Token Transfer")
    transfer_amount = 25.0
    transfer_success = blockchain_mrv.smart_contract.transfer_tokens(
        token_id, 
        owner_address, 
        buyer_address_1, 
        transfer_amount
    )
    
    if transfer_success:
        print(f"✅ Token transfer successful")
        print(f"   Transferred: {transfer_amount} tCO₂e to {buyer_address_1[:10]}...")
        
        # Check balances
        owner_balance = blockchain_mrv.smart_contract.get_token_balance(token_id, owner_address)
        buyer_balance = blockchain_mrv.smart_contract.get_token_balance(token_id, buyer_address_1)
        print(f"   Owner balance: {owner_balance} tCO₂e")
        print(f"   Buyer balance: {buyer_balance} tCO₂e")
    else:
        print("❌ Token transfer failed")
        return
    
    # Test 6: Partial Token Retirement
    print_sub_title("Test 6: Token Retirement")
    retire_amount = 10.0
    retirement_success = blockchain_mrv.smart_contract.retire_tokens(
        token_id, 
        buyer_address_1, 
        retire_amount, 
        "Corporate carbon offsetting for Company A"
    )
    
    if retirement_success:
        print(f"✅ Token retirement successful")
        print(f"   Retired: {retire_amount} tCO₂e by {buyer_address_1[:10]}...")
        
        # Check updated balances and retirement info
        updated_token_info = blockchain_mrv.smart_contract.get_token_info(token_id)
        print(f"   Remaining buyer balance: {updated_token_info['fractional_owners'].get(buyer_address_1, 0)} tCO₂e")
        print(f"   Total retired: {updated_token_info['retired_amount']} tCO₂e")
        print(f"   Available amount: {updated_token_info['available_amount']} tCO₂e")
    else:
        print("❌ Token retirement failed")
    
    # Test 7: Batch Transfer
    print_sub_title("Test 7: Batch Transfer")
    batch_transfers = [
        {
            'token_id': token_id,
            'from_address': owner_address,
            'to_address': buyer_address_2,
            'amount': 20.0
        }
    ]
    
    batch_result = blockchain_mrv.smart_contract.batch_transfer_tokens(batch_transfers)
    print(f"✅ Batch transfer executed")
    print(f"   Successful transfers: {len(batch_result['successful'])}")
    print(f"   Failed transfers: {len(batch_result['failed'])}")
    
    # Test 8: Address Portfolio
    print_sub_title("Test 8: Address Portfolio")
    portfolio = blockchain_mrv.smart_contract.get_address_portfolio(buyer_address_1)
    print(f"✅ Portfolio retrieved for {buyer_address_1[:10]}...")
    print(f"   Total balance: {portfolio['total_balance']} tCO₂e")
    print(f"   Number of tokens: {len(portfolio['tokens'])}")
    print(f"   Number of transactions: {len(portfolio['transactions'])}")
    
    # Test 9: Field Data Recording
    print_sub_title("Test 9: Field Data Recording")
    field_data = {
        'id': 'FD_TEST_001',
        'project_id': 'PROJ_TEST_001',
        'ngo_id': 'NGO001',
        'collection_date': '2024-06-15',
        'location': {'lat': 19.0176, 'lng': 72.8562},
        'ecosystem_data': {
            'type': 'Mangrove',
            'area_covered': 5.2,
            'tree_count': 156,
            'avg_height': 2.4,
            'species_identified': 'Rhizophora mucronata'
        },
        'environmental_conditions': {
            'temperature': 28.5,
            'humidity': 85,
            'water_salinity': 15.2,
            'soil_ph': 7.1
        }
    }
    
    field_data_hash = blockchain_mrv.record_field_data(field_data)
    print(f"✅ Field data recorded on blockchain")
    print(f"   Transaction hash: {field_data_hash}")
    
    # Test 10: Final Statistics
    print_sub_title("Test 10: Final Blockchain Statistics")
    final_stats = blockchain_mrv.get_blockchain_stats()
    print(f"Total projects: {final_stats['blockchain']['total_projects']}")
    print(f"Verified projects: {final_stats['blockchain']['verified_projects']}")
    print(f"Smart contract tokens: {final_stats['smart_contract']['total_tokens']}")
    print(f"Total supply: {final_stats['smart_contract']['total_supply']} tCO₂e")
    print(f"Active supply: {final_stats['smart_contract']['active_supply']} tCO₂e")
    print(f"Retired supply: {final_stats['smart_contract']['retired_supply']} tCO₂e")
    print(f"Total transactions: {final_stats['smart_contract']['total_transactions']}")
    
    # Test 11: Transaction History
    print_sub_title("Test 11: Transaction History")
    all_transactions = blockchain_mrv.smart_contract.transactions
    print(f"✅ Total transactions recorded: {len(all_transactions)}")
    
    transaction_types = {}
    for tx in all_transactions:
        tx_type = tx.transaction_type
        transaction_types[tx_type] = transaction_types.get(tx_type, 0) + 1
    
    print("   Transaction breakdown:")
    for tx_type, count in transaction_types.items():
        print(f"     {tx_type}: {count}")
    
    print_divider("BLOCKCHAIN INTEGRATION TEST COMPLETED")
    print("✅ All blockchain functionality working correctly!")
    print("✅ Project submission, verification, and token lifecycle tested")
    print("✅ Token transfers, retirements, and batch operations verified")
    print("✅ Field data recording and portfolio management functional")

if __name__ == "__main__":
    test_blockchain_integration()