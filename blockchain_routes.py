"""
Blockchain API Routes for BlueCarbon MRV System
Provides RESTful endpoints for blockchain operations
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import json
import random
import time

from blockchain_sim import blockchain_mrv
from token_visualization import token_viz_engine
try:
    from supabase_client import supabase_client
except ImportError:
    # Fallback if supabase is not available
    class MockSupabaseClient:
        mock_mode = True
        def get_projects(self, *args, **kwargs): return []
        def get_tokens(self, *args, **kwargs): return []
        def get_transactions(self, *args, **kwargs): return []
    supabase_client = MockSupabaseClient()

# Create blueprint
blockchain_bp = Blueprint('blockchain', __name__, url_prefix='/api/blockchain')

@blockchain_bp.route('/stats', methods=['GET'])
def get_blockchain_stats():
    """Get overall blockchain system statistics"""
    try:
        # Get stats from blockchain simulation
        stats = blockchain_mrv.get_blockchain_stats()
        
        # Enhance with Supabase data if available
        if not supabase_client.mock_mode:
            # Add real database stats
            projects = supabase_client.get_projects({'status': 'Verified'})
            tokens = supabase_client.get_tokens({'status': 'active'})
            transactions = supabase_client.get_transactions()
            
            stats['database_stats'] = {
                'verified_projects': len(projects),
                'active_tokens': len(tokens),
                'total_transactions': len(transactions),
                'last_updated': datetime.now().isoformat()
            }
        
        return jsonify({
            'success': True,
            'data': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@blockchain_bp.route('/projects/<project_id>/tokenize', methods=['POST'])
def tokenize_project(project_id):
    """Create blockchain tokens for an approved project"""
    try:
        data = request.get_json()
        credits_amount = data.get('credits_amount')
        project_metadata = data.get('metadata', {})
        
        if not credits_amount:
            return jsonify({
                'success': False,
                'error': 'Credits amount is required'
            }), 400
        
        # Mint tokens using blockchain simulation
        token_id = blockchain_mrv.smart_contract.mint_tokens(
            project_id=project_id,
            credits_amount=float(credits_amount),
            metadata={
                **project_metadata,
                'minted_at': datetime.now().isoformat(),
                'minted_by': 'admin'
            }
        )
        
        # Save to Supabase
        if not supabase_client.mock_mode:
            token_data = {
                'token_id': token_id,
                'project_id': project_id,
                'credits_amount': float(credits_amount),
                'owner_address': blockchain_mrv.smart_contract.tokens[token_id].owner_address,
                'status': 'active',
                'mint_transaction_hash': f"0x{random.randint(100000000000000000, 999999999999999999):016x}"
            }
            supabase_client.create_token(token_data)
        
        return jsonify({
            'success': True,
            'data': {
                'token_id': token_id,
                'project_id': project_id,
                'credits_amount': credits_amount,
                'blockchain_hash': blockchain_mrv.smart_contract.transactions[-1].tx_hash if blockchain_mrv.smart_contract.transactions else None,
                'created_at': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/tokens/<token_id>/transfer', methods=['POST'])
def transfer_token(token_id):
    """Transfer tokens between addresses"""
    try:
        data = request.get_json()
        from_address = data.get('from_address')
        to_address = data.get('to_address')
        amount = data.get('amount')
        
        if not all([from_address, to_address, amount]):
            return jsonify({
                'success': False,
                'error': 'from_address, to_address, and amount are required'
            }), 400
        
        # Execute transfer in blockchain simulation
        success = blockchain_mrv.smart_contract.transfer_tokens(
            token_id=token_id,
            from_address=from_address,
            to_address=to_address,
            amount=float(amount)
        )
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Transfer failed - check token ownership and balance'
            }), 400
        
        # Update Supabase
        if not supabase_client.mock_mode:
            supabase_client.transfer_token(
                token_id=token_id,
                from_address=from_address,
                to_address=to_address,
                amount=float(amount)
            )
        
        return jsonify({
            'success': True,
            'data': {
                'token_id': token_id,
                'from_address': from_address,
                'to_address': to_address,
                'amount': amount,
                'transaction_hash': blockchain_mrv.smart_contract.transactions[-1].tx_hash,
                'transferred_at': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/tokens/<token_id>/retire', methods=['POST'])
def retire_token(token_id):
    """Retire tokens permanently for carbon offsetting"""
    try:
        data = request.get_json()
        owner_address = data.get('owner_address')
        reason = data.get('reason', 'Carbon offsetting')
        
        if not owner_address:
            return jsonify({
                'success': False,
                'error': 'owner_address is required'
            }), 400
        
        # Execute retirement in blockchain simulation
        success = blockchain_mrv.smart_contract.retire_tokens(
            token_id=token_id,
            owner_address=owner_address,
            reason=reason
        )
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Retirement failed - check token ownership'
            }), 400
        
        # Update Supabase
        if not supabase_client.mock_mode:
            supabase_client.retire_token(
                token_id=token_id,
                owner_address=owner_address,
                reason=reason
            )
        
        return jsonify({
            'success': True,
            'data': {
                'token_id': token_id,
                'owner_address': owner_address,
                'reason': reason,
                'retirement_hash': blockchain_mrv.smart_contract.transactions[-1].tx_hash,
                'retired_at': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/tokens/<token_id>', methods=['GET'])
def get_token_info(token_id):
    """Get detailed information about a specific token"""
    try:
        # Get from blockchain simulation
        token_info = blockchain_mrv.smart_contract.get_token_info(token_id)
        
        if not token_info:
            return jsonify({
                'success': False,
                'error': 'Token not found'
            }), 404
        
        # Enhance with Supabase data
        if not supabase_client.mock_mode:
            db_tokens = supabase_client.get_tokens({'token_id': token_id})
            if db_tokens:
                token_info['database_record'] = db_tokens[0]
        
        return jsonify({
            'success': True,
            'data': token_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/tokens', methods=['GET'])
def list_tokens():
    """List all tokens with optional filtering"""
    try:
        # Get query parameters
        project_id = request.args.get('project_id')
        owner_address = request.args.get('owner_address')
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        
        # Build filters
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        if owner_address:
            filters['owner_address'] = owner_address
        if status:
            filters['status'] = status
        
        # Get from Supabase or mock data
        tokens = supabase_client.get_tokens(filters)
        
        # Limit results
        tokens = tokens[:limit]
        
        return jsonify({
            'success': True,
            'data': {
                'tokens': tokens,
                'count': len(tokens),
                'filters_applied': filters
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/transactions', methods=['GET'])
def list_transactions():
    """List blockchain transactions with filtering"""
    try:
        # Get query parameters
        transaction_type = request.args.get('type')
        token_id = request.args.get('token_id')
        address = request.args.get('address')
        limit = int(request.args.get('limit', 100))
        
        # Get all transactions from blockchain
        all_transactions = []
        for tx in blockchain_mrv.smart_contract.transactions:
            tx_data = tx.to_dict()
            
            # Apply filters
            if transaction_type and tx.transaction_type != transaction_type:
                continue
            if token_id and tx_data.get('data', {}).get('token_id') != token_id:
                continue
            if address and tx.from_address != address and tx.to_address != address:
                continue
                
            all_transactions.append(tx_data)
            
        # Limit results
        all_transactions = all_transactions[:limit]
        
        return jsonify({
            'success': True,
            'data': {
                'transactions': all_transactions,
                'count': len(all_transactions)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/tokens/batch-transfer', methods=['POST'])
def batch_transfer_tokens():
    """Execute batch token transfers"""
    try:
        data = request.get_json()
        transfers = data.get('transfers', [])
        
        if not transfers:
            return jsonify({
                'success': False,
                'error': 'No transfers provided'
            }), 400
            
        # Execute batch transfer
        results = blockchain_mrv.smart_contract.batch_transfer_tokens(transfers)
        
        return jsonify({
            'success': True,
            'data': {
                'batch_results': results,
                'total_transfers': len(transfers),
                'successful_transfers': len(results['successful']),
                'failed_transfers': len(results['failed']),
                'transaction_hash': blockchain_mrv.smart_contract.transactions[-1].tx_hash
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/tokens/batch-retire', methods=['POST'])
def batch_retire_tokens():
    """Execute batch token retirements"""
    try:
        data = request.get_json()
        retirements = data.get('retirements', [])
        
        if not retirements:
            return jsonify({
                'success': False,
                'error': 'No retirements provided'
            }), 400
            
        # Execute batch retirement
        results = blockchain_mrv.smart_contract.batch_retire_tokens(retirements)
        
        return jsonify({
            'success': True,
            'data': {
                'batch_results': results,
                'total_retirements': len(retirements),
                'successful_retirements': len(results['successful']),
                'failed_retirements': len(results['failed']),
                'transaction_hash': blockchain_mrv.smart_contract.transactions[-1].tx_hash
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/addresses/<address>/portfolio', methods=['GET'])
def get_address_portfolio(address):
    """Get complete token portfolio for an address"""
    try:
        portfolio = blockchain_mrv.smart_contract.get_address_portfolio(address)
        
        return jsonify({
            'success': True,
            'data': portfolio
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/tokens/vintage/<int:vintage_year>', methods=['GET'])
def get_tokens_by_vintage(vintage_year):
    """Get all tokens from a specific vintage year"""
    try:
        tokens = blockchain_mrv.smart_contract.get_tokens_by_vintage(vintage_year)
        
        return jsonify({
            'success': True,
            'data': {
                'vintage_year': vintage_year,
                'tokens': tokens,
                'count': len(tokens),
                'total_credits': sum(token['credits_amount'] for token in tokens)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/projects/<project_id>/tokens', methods=['GET'])
def get_project_tokens(project_id):
    """Get all tokens for a specific project"""
    try:
        tokens = blockchain_mrv.smart_contract.get_tokens_by_project(project_id)
        
        return jsonify({
            'success': True,
            'data': {
                'project_id': project_id,
                'tokens': tokens,
                'count': len(tokens),
                'total_credits': sum(token['credits_amount'] for token in tokens)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/retirements', methods=['GET'])
def get_retirement_history():
    """Get retirement history with optional address filter"""
    try:
        address = request.args.get('address')
        limit = int(request.args.get('limit', 100))
        
        retirements = blockchain_mrv.smart_contract.get_retirement_history(address)
        retirements = retirements[:limit]
        
        return jsonify({
            'success': True,
            'data': {
                'retirements': retirements,
                'count': len(retirements),
                'filtered_by_address': address
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/visualization/token-flow', methods=['GET'])
def get_token_flow_visualization():
    """Get token flow visualization data"""
    try:
        project_id = request.args.get('project_id')
        timeframe_days = int(request.args.get('timeframe_days', 365))
        
        # Generate visualization data
        viz_data = token_viz_engine.generate_token_flow_visualization(
            project_id=project_id,
            timeframe_days=timeframe_days
        )
        
        return jsonify({
            'success': True,
            'data': viz_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/visualization/real-time-dashboard', methods=['GET'])
def get_real_time_dashboard():
    """Get real-time blockchain dashboard data"""
    try:
        project_id = request.args.get('project_id')
        
        # Generate dashboard data
        dashboard_data = token_viz_engine.create_real_time_dashboard_data(
            project_id=project_id
        )
        
        return jsonify({
            'success': True,
            'data': dashboard_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/verify-transaction/<tx_hash>', methods=['GET'])
def verify_transaction(tx_hash):
    """Verify a blockchain transaction by hash"""
    try:
        # Find transaction in blockchain simulation
        transaction = None
        for tx in blockchain_mrv.smart_contract.transactions:
            if tx.tx_hash == tx_hash:
                transaction = tx.to_dict()
                break
        
        if not transaction:
            return jsonify({
                'success': False,
                'error': 'Transaction not found'
            }), 404
        
        # Add verification info
        verification_data = {
            'transaction': transaction,
            'verified': True,
            'confirmations': transaction.get('confirmations', 6),
            'network': 'BlueCarbon-Testnet',
            'verified_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': verification_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/wallet/<address>/balance', methods=['GET'])
def get_wallet_balance(address):
    """Get carbon credit balance for a wallet address"""
    try:
        total_balance = 0
        active_tokens = []
        
        # Check all tokens owned by this address
        for token_id, token in blockchain_mrv.smart_contract.tokens.items():
            if token.owner_address == address and not token.retired:
                total_balance += token.credits_amount
                active_tokens.append({
                    'token_id': token_id,
                    'project_id': token.project_id,
                    'credits_amount': token.credits_amount,
                    'mint_date': datetime.fromtimestamp(token.mint_timestamp).isoformat()
                })
        
        return jsonify({
            'success': True,
            'data': {
                'address': address,
                'total_balance': total_balance,
                'active_tokens': active_tokens,
                'tokens_count': len(active_tokens)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blockchain_bp.route('/smart-contract/info', methods=['GET'])
def get_smart_contract_info():
    """Get smart contract information and statistics"""
    try:
        contract = blockchain_mrv.smart_contract
        
        contract_info = {
            'contract_address': contract.contract_address,
            'deployed_at': datetime.fromtimestamp(contract.deployed_timestamp).isoformat(),
            'total_supply': contract.total_supply,
            'retired_supply': contract.retired_supply,
            'active_supply': contract.total_supply - contract.retired_supply,
            'total_tokens': len(contract.tokens),
            'active_tokens': len([t for t in contract.tokens.values() if not t.retired]),
            'total_transactions': len(contract.transactions),
            'transaction_types': {
                'mint': len([t for t in contract.transactions if t.transaction_type == 'credit_mint']),
                'transfer': len([t for t in contract.transactions if t.transaction_type == 'credit_transfer']),
                'retire': len([t for t in contract.transactions if t.transaction_type == 'credit_retire'])
            }
        }
        
        return jsonify({
            'success': True,
            'data': contract_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# WebSocket events for real-time updates
@blockchain_bp.route('/events/subscribe', methods=['POST'])
def subscribe_to_blockchain_events():
    """Subscribe to real-time blockchain events"""
    try:
        data = request.get_json()
        event_types = data.get('events', ['all'])
        callback_url = data.get('callback_url')
        
        # In a real implementation, this would set up WebSocket or webhook subscriptions
        subscription_id = f"sub_{int(time.time())}"
        
        return jsonify({
            'success': True,
            'data': {
                'subscription_id': subscription_id,
                'events': event_types,
                'callback_url': callback_url,
                'created_at': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500