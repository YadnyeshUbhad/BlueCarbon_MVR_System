"""
Blockchain Simulation Module for Blue Carbon MRV System
Simulates blockchain functionality including smart contracts and tokenization
"""

import hashlib
import time
import json
from datetime import datetime
from typing import Dict, List, Optional

class BlockchainTransaction:
    """Represents a blockchain transaction"""
    
    def __init__(self, transaction_type: str, data: dict, from_address: str = None, to_address: str = None):
        self.timestamp = time.time()
        self.transaction_type = transaction_type  # 'project_submit', 'credit_issue', 'credit_transfer', 'credit_retire'
        self.data = data
        self.from_address = from_address
        self.to_address = to_address
        self.tx_hash = self._generate_hash()
        self.block_number = None
        self.confirmations = 0
        
    def _json_default(self, obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)

    def _generate_hash(self) -> str:
        """Generate transaction hash"""
        transaction_string = f"{self.timestamp}{self.transaction_type}{json.dumps(self.data, sort_keys=True, default=self._json_default)}"
        return hashlib.sha256(transaction_string.encode()).hexdigest()
    
    def to_dict(self) -> dict:
        return {
            'tx_hash': self.tx_hash,
            'timestamp': self.timestamp,
            'datetime': datetime.fromtimestamp(self.timestamp).isoformat(),
            'type': self.transaction_type,
            'data': self.data,
            'from_address': self.from_address,
            'to_address': self.to_address,
            'block_number': self.block_number,
            'confirmations': self.confirmations
        }

class CarbonCreditToken:
    """Enhanced carbon credit token with advanced features"""
    
    def __init__(self, token_id: str, project_id: str, credits_amount: float, metadata: dict):
        self.token_id = token_id
        self.project_id = project_id
        self.credits_amount = credits_amount  # tCO2e
        self.available_amount = credits_amount  # Amount available for transfer/retirement
        self.metadata = metadata
        self.owner_address = "0x" + hashlib.md5(project_id.encode()).hexdigest()[:40]
        self.mint_timestamp = time.time()
        self.transfers = []
        self.retirements = []  # Track partial retirements
        self.retired = False
        self.retirement_timestamp = None
        self.fractional_owners = {self.owner_address: credits_amount}  # Track fractional ownership
        self.locked_amounts = {}  # Track locked amounts for pending transfers
        self.vintage_year = metadata.get('vintage_year', datetime.now().year)
        self.certification_standard = metadata.get('standard', 'VCS')
        self.additional_attributes = metadata.get('attributes', {})
        
    def transfer(self, from_address: str, to_address: str, amount: float = None) -> bool:
        """Transfer tokens with fractional ownership support"""
        if self.retired:
            return False
            
        transfer_amount = amount or self.fractional_owners.get(from_address, 0)
        
        # Check if sender has enough balance
        if from_address not in self.fractional_owners or self.fractional_owners[from_address] < transfer_amount:
            return False
            
        if transfer_amount <= 0:
            return False
            
        # Execute transfer
        self.fractional_owners[from_address] -= transfer_amount
        
        # Remove zero balances
        if self.fractional_owners[from_address] <= 0:
            del self.fractional_owners[from_address]
        
        # Add to recipient
        if to_address in self.fractional_owners:
            self.fractional_owners[to_address] += transfer_amount
        else:
            self.fractional_owners[to_address] = transfer_amount
            
        # Update primary owner to largest holder
        self.owner_address = max(self.fractional_owners, key=self.fractional_owners.get)
        
        # Record transfer
        self.transfers.append({
            'from': from_address,
            'to': to_address,
            'amount': transfer_amount,
            'timestamp': time.time(),
            'transaction_id': hashlib.sha256(f"{from_address}{to_address}{transfer_amount}{time.time()}".encode()).hexdigest()[:16]
        })
        
        return True
        
    def partial_retire(self, owner_address: str, amount: float, retire_reason: str = "Carbon offsetting") -> bool:
        """Retire a portion of tokens permanently"""
        if owner_address not in self.fractional_owners:
            return False
            
        if self.fractional_owners[owner_address] < amount:
            return False
            
        if amount <= 0:
            return False
            
        # Execute partial retirement
        self.fractional_owners[owner_address] -= amount
        self.available_amount -= amount
        
        # Remove zero balances
        if self.fractional_owners[owner_address] <= 0:
            del self.fractional_owners[owner_address]
            
        # Record retirement
        retirement_record = {
            'owner': owner_address,
            'amount': amount,
            'reason': retire_reason,
            'timestamp': time.time(),
            'retirement_id': hashlib.sha256(f"{owner_address}{amount}{time.time()}".encode()).hexdigest()[:16]
        }
        self.retirements.append(retirement_record)
        
        # Check if fully retired
        if self.available_amount <= 0:
            self.retired = True
            self.retirement_timestamp = time.time()
            
        return True
        
    def get_balance(self, address: str) -> float:
        """Get token balance for specific address"""
        return self.fractional_owners.get(address, 0.0)
        
    def get_total_retired(self) -> float:
        """Get total amount retired"""
        return sum(r['amount'] for r in self.retirements)
    
    
    def to_dict(self) -> dict:
        return {
            'token_id': self.token_id,
            'project_id': self.project_id,
            'credits_amount': self.credits_amount,
            'available_amount': self.available_amount,
            'retired_amount': self.get_total_retired(),
            'primary_owner': self.owner_address,
            'fractional_owners': self.fractional_owners,
            'mint_timestamp': self.mint_timestamp,
            'mint_date': datetime.fromtimestamp(self.mint_timestamp).isoformat(),
            'transfers': self.transfers,
            'retirements': self.retirements,
            'fully_retired': self.retired,
            'retirement_timestamp': self.retirement_timestamp,
            'retirement_date': datetime.fromtimestamp(self.retirement_timestamp).isoformat() if self.retirement_timestamp else None,
            'vintage_year': self.vintage_year,
            'certification_standard': self.certification_standard,
            'additional_attributes': self.additional_attributes,
            'metadata': self.metadata
        }

class SmartContract:
    """Simulates smart contract functionality for carbon credits"""
    
    def __init__(self, contract_address: str):
        self.contract_address = contract_address
        self.deployed_timestamp = time.time()
        self.tokens = {}  # token_id -> CarbonCreditToken
        self.transactions = []
        self.total_supply = 0.0
        self.retired_supply = 0.0
        
    def mint_tokens(self, project_id: str, credits_amount: float, metadata: dict) -> str:
        """Mint new carbon credit tokens"""
        token_id = f"CC_{project_id}_{int(time.time())}"
        
        token = CarbonCreditToken(
            token_id=token_id,
            project_id=project_id,
            credits_amount=credits_amount,
            metadata=metadata
        )
        
        self.tokens[token_id] = token
        self.total_supply += credits_amount
        
        # Create transaction
        tx = BlockchainTransaction(
            transaction_type='credit_mint',
            data={
                'token_id': token_id,
                'project_id': project_id,
                'credits_amount': credits_amount,
                'metadata': metadata
            },
            to_address=token.owner_address
        )
        
        self.transactions.append(tx)
        return token_id
    
    def transfer_tokens(self, token_id: str, from_address: str, to_address: str, amount: float = None) -> bool:
        """Transfer tokens between addresses with enhanced fractional support"""
        if token_id not in self.tokens:
            return False
            
        token = self.tokens[token_id]
        
        # Check if sender has balance in this token
        if token.get_balance(from_address) <= 0:
            return False
            
        if token.transfer(from_address, to_address, amount):
            # Create transaction
            actual_amount = amount or token.get_balance(from_address)
            tx = BlockchainTransaction(
                transaction_type='credit_transfer',
                data={
                    'token_id': token_id,
                    'amount': actual_amount,
                    'from_balance_before': token.get_balance(from_address) + actual_amount,
                    'to_balance_before': token.get_balance(to_address) - actual_amount,
                    'from_balance_after': token.get_balance(from_address),
                    'to_balance_after': token.get_balance(to_address)
                },
                from_address=from_address,
                to_address=to_address
            )
            
            self.transactions.append(tx)
            return True
            
        return False
        
    def batch_transfer_tokens(self, transfers: list) -> dict:
        """Execute multiple token transfers in a single batch"""
        results = {'successful': [], 'failed': []}
        
        for transfer in transfers:
            token_id = transfer.get('token_id')
            from_address = transfer.get('from_address')
            to_address = transfer.get('to_address')
            amount = transfer.get('amount')
            
            success = self.transfer_tokens(token_id, from_address, to_address, amount)
            
            transfer_result = {
                'token_id': token_id,
                'from_address': from_address,
                'to_address': to_address,
                'amount': amount,
                'success': success
            }
            
            if success:
                results['successful'].append(transfer_result)
            else:
                results['failed'].append(transfer_result)
                
        # Create batch transaction record
        batch_tx = BlockchainTransaction(
            transaction_type='batch_transfer',
            data={
                'batch_size': len(transfers),
                'successful_count': len(results['successful']),
                'failed_count': len(results['failed']),
                'results': results
            }
        )
        
        self.transactions.append(batch_tx)
        return results
    
    def retire_tokens(self, token_id: str, owner_address: str, amount: float = None, reason: str = "Carbon offsetting") -> bool:
        """Retire tokens permanently with partial retirement support"""
        if token_id not in self.tokens:
            return False
            
        token = self.tokens[token_id]
        
        # Check if owner has balance in this token
        if token.get_balance(owner_address) <= 0:
            return False
            
        retire_amount = amount or token.get_balance(owner_address)
        
        if token.partial_retire(owner_address, retire_amount, reason):
            self.retired_supply += retire_amount
            
            # Create transaction
            tx = BlockchainTransaction(
                transaction_type='credit_retire',
                data={
                    'token_id': token_id,
                    'owner_address': owner_address,
                    'retired_amount': retire_amount,
                    'remaining_balance': token.get_balance(owner_address),
                    'total_retired_for_token': token.get_total_retired(),
                    'reason': reason,
                    'is_full_retirement': token.retired
                },
                from_address=owner_address
            )
            
            self.transactions.append(tx)
            return True
            
        return False
        
    def batch_retire_tokens(self, retirements: list) -> dict:
        """Execute multiple token retirements in a single batch"""
        results = {'successful': [], 'failed': []}
        
        for retirement in retirements:
            token_id = retirement.get('token_id')
            owner_address = retirement.get('owner_address')
            amount = retirement.get('amount')
            reason = retirement.get('reason', 'Carbon offsetting')
            
            success = self.retire_tokens(token_id, owner_address, amount, reason)
            
            retirement_result = {
                'token_id': token_id,
                'owner_address': owner_address,
                'amount': amount,
                'reason': reason,
                'success': success
            }
            
            if success:
                results['successful'].append(retirement_result)
            else:
                results['failed'].append(retirement_result)
                
        # Create batch transaction record
        batch_tx = BlockchainTransaction(
            transaction_type='batch_retire',
            data={
                'batch_size': len(retirements),
                'successful_count': len(results['successful']),
                'failed_count': len(results['failed']),
                'results': results
            }
        )
        
        self.transactions.append(batch_tx)
        return results
    
    def get_token_info(self, token_id: str) -> Optional[dict]:
        """Get token information"""
        if token_id in self.tokens:
            return self.tokens[token_id].to_dict()
        return None
    
    def get_token_balance(self, token_id: str, address: str) -> float:
        """Get token balance for specific address"""
        if token_id in self.tokens:
            return self.tokens[token_id].get_balance(address)
        return 0.0
        
    def get_address_portfolio(self, address: str) -> dict:
        """Get complete token portfolio for an address"""
        portfolio = {
            'address': address,
            'total_balance': 0.0,
            'tokens': [],
            'transactions': []
        }
        
        for token_id, token in self.tokens.items():
            balance = token.get_balance(address)
            if balance > 0:
                portfolio['tokens'].append({
                    'token_id': token_id,
                    'project_id': token.project_id,
                    'balance': balance,
                    'vintage_year': token.vintage_year,
                    'certification_standard': token.certification_standard
                })
                portfolio['total_balance'] += balance
                
        # Get transactions involving this address
        for tx in self.transactions:
            if (tx.from_address == address or 
                tx.to_address == address or 
                (hasattr(tx.data, 'owner_address') and tx.data.get('owner_address') == address)):
                portfolio['transactions'].append(tx.to_dict())
                
        return portfolio
        
    def get_tokens_by_vintage(self, vintage_year: int) -> list:
        """Get all tokens from a specific vintage year"""
        return [
            token.to_dict() for token in self.tokens.values() 
            if token.vintage_year == vintage_year
        ]
        
    def get_tokens_by_project(self, project_id: str) -> list:
        """Get all tokens for a specific project"""
        return [
            token.to_dict() for token in self.tokens.values() 
            if token.project_id == project_id
        ]
        
    def get_retirement_history(self, address: str = None) -> list:
        """Get retirement history, optionally filtered by address"""
        retirements = []
        
        for token in self.tokens.values():
            for retirement in token.retirements:
                if address is None or retirement['owner'] == address:
                    retirement_record = {
                        'token_id': token.token_id,
                        'project_id': token.project_id,
                        **retirement
                    }
                    retirements.append(retirement_record)
                    
        return sorted(retirements, key=lambda x: x['timestamp'], reverse=True)
        
    def get_contract_stats(self) -> dict:
        """Get enhanced contract statistics"""
        active_supply = self.total_supply - self.retired_supply
        
        # Calculate additional metrics
        vintage_breakdown = {}
        standard_breakdown = {}
        project_breakdown = {}
        
        for token in self.tokens.values():
            # Vintage year breakdown
            vintage = token.vintage_year
            if vintage not in vintage_breakdown:
                vintage_breakdown[vintage] = {'total': 0, 'retired': 0, 'active': 0}
            vintage_breakdown[vintage]['total'] += token.credits_amount
            vintage_breakdown[vintage]['retired'] += token.get_total_retired()
            vintage_breakdown[vintage]['active'] += token.available_amount
            
            # Standard breakdown
            standard = token.certification_standard
            if standard not in standard_breakdown:
                standard_breakdown[standard] = {'total': 0, 'retired': 0, 'active': 0}
            standard_breakdown[standard]['total'] += token.credits_amount
            standard_breakdown[standard]['retired'] += token.get_total_retired()
            standard_breakdown[standard]['active'] += token.available_amount
            
            # Project breakdown
            project = token.project_id
            if project not in project_breakdown:
                project_breakdown[project] = {'total': 0, 'retired': 0, 'active': 0}
            project_breakdown[project]['total'] += token.credits_amount
            project_breakdown[project]['retired'] += token.get_total_retired()
            project_breakdown[project]['active'] += token.available_amount
        
        return {
            'contract_address': self.contract_address,
            'deployed_timestamp': self.deployed_timestamp,
            'deployed_date': datetime.fromtimestamp(self.deployed_timestamp).isoformat(),
            'total_supply': self.total_supply,
            'active_supply': active_supply,
            'retired_supply': self.retired_supply,
            'retirement_rate': (self.retired_supply / self.total_supply * 100) if self.total_supply > 0 else 0,
            'total_tokens': len(self.tokens),
            'fully_retired_tokens': len([t for t in self.tokens.values() if t.retired]),
            'partially_retired_tokens': len([t for t in self.tokens.values() if t.get_total_retired() > 0 and not t.retired]),
            'active_tokens': len([t for t in self.tokens.values() if not t.retired]),
            'total_transactions': len(self.transactions),
            'unique_addresses': len(set([tx.from_address for tx in self.transactions if tx.from_address] + 
                                      [tx.to_address for tx in self.transactions if tx.to_address])),
            'vintage_breakdown': vintage_breakdown,
            'standard_breakdown': standard_breakdown,
            'project_breakdown': project_breakdown
        }

class BlockchainMRV:
    """Main blockchain MRV system"""
    
    def __init__(self):
        self.smart_contract = SmartContract("0xbluecarbon_mrv_contract")
        self.project_registry = {}  # project_id -> blockchain record
        self.verification_nodes = [
            "NCCR_Node_1",
            "NCCR_Node_2", 
            "Academic_Node_IISc",
            "NGO_Verification_Node"
        ]
        
    def _sanitize_for_json(self, data):
        """Recursively sanitize data for JSON serialization (convert datetimes)"""
        if isinstance(data, dict):
            return {k: self._sanitize_for_json(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self._sanitize_for_json(v) for v in data]
        if isinstance(data, datetime):
            return data.isoformat()
        return data

    def submit_project_to_blockchain(self, project_data: dict) -> str:
        """Submit project to blockchain and create initial record"""
        project_id = project_data['id']
        
        # Sanitize project data for JSON safety
        sanitized_project_data = self._sanitize_for_json(project_data)
        
        # Create immutable project record
        blockchain_record = {
            'project_id': project_id,
            'submission_timestamp': time.time(),
            'data_hash': self._hash_project_data(project_data),
            'project_data': sanitized_project_data,
            'verification_status': 'pending',
            'verification_nodes': [],
            'carbon_credits_issued': 0,
            'token_ids': []
        }
        
        # Create transaction
        tx = BlockchainTransaction(
            transaction_type='project_submit',
            data=blockchain_record,
            from_address=f"ngo_{project_data.get('ngo_id', 'unknown')}"
        )
        
        self.project_registry[project_id] = blockchain_record
        return tx.tx_hash
    
    def verify_project_on_blockchain(self, project_id: str, verifier_node: str, approval_data: dict) -> bool:
        """Verify project by authorized node"""
        if project_id not in self.project_registry:
            return False
            
        if verifier_node not in self.verification_nodes:
            return False
            
        project_record = self.project_registry[project_id]
        
        # Add verification
        verification = {
            'node': verifier_node,
            'timestamp': time.time(),
            'status': approval_data.get('status', 'approved'),
            'credits_approved': approval_data.get('credits_approved', 0),
            'verification_notes': approval_data.get('notes', '')
        }
        
        project_record['verification_nodes'].append(verification)
        
        # If approved, mint tokens
        if approval_data.get('status') == 'approved' and approval_data.get('credits_approved', 0) > 0:
            token_id = self.smart_contract.mint_tokens(
                project_id=project_id,
                credits_amount=approval_data['credits_approved'],
                metadata={
                    'project_name': project_record['project_data'].get('name', ''),
                    'ecosystem_type': project_record['project_data'].get('ecosystem', ''),
                    'location': project_record['project_data'].get('location', ''),
                    'tree_count': project_record['project_data'].get('number_of_trees', 0),
                    'verification_node': verifier_node,
                    'verification_timestamp': time.time()
                }
            )
            
            project_record['verification_status'] = 'verified'
            project_record['carbon_credits_issued'] = approval_data['credits_approved']
            project_record['token_ids'].append(token_id)
            
        return True
    
    def get_project_blockchain_info(self, project_id: str) -> Optional[dict]:
        """Get project blockchain information"""
        if project_id in self.project_registry:
            record = self.project_registry[project_id].copy()
            
            # Add token information
            if record['token_ids']:
                record['tokens'] = []
                for token_id in record['token_ids']:
                    token_info = self.smart_contract.get_token_info(token_id)
                    if token_info:
                        record['tokens'].append(token_info)
                        
            return record
            
        return None
    
    def record_field_data(self, field_data: dict) -> str:
        """Record field data collection on blockchain"""
        field_data_id = field_data['id']
        
        # Sanitize field data for JSON safety
        sanitized_field_data = self._sanitize_for_json(field_data)
        
        # Create immutable field data record
        blockchain_record = {
            'field_data_id': field_data_id,
            'project_id': field_data['project_id'],
            'ngo_id': field_data['ngo_id'],
            'collection_timestamp': time.time(),
            'data_hash': self._hash_field_data(field_data),
            'field_data': sanitized_field_data,
            'verification_status': 'recorded',
            'verification_nodes': []
        }
        
        # Create transaction
        tx = BlockchainTransaction(
            transaction_type='field_data_submit',
            data=blockchain_record,
            from_address=f"ngo_{field_data.get('ngo_id', 'unknown')}"
        )
        
        # Store in project registry linked to project
        if field_data['project_id'] in self.project_registry:
            project_record = self.project_registry[field_data['project_id']]
            if 'field_data_records' not in project_record:
                project_record['field_data_records'] = []
            project_record['field_data_records'].append(blockchain_record)
        
        return tx.tx_hash
        
    def _hash_field_data(self, field_data: dict) -> str:
        """Create hash of field data for integrity"""
        # Remove dynamic fields
        static_data = {k: v for k, v in field_data.items() 
                      if k not in ['submission_timestamp', 'blockchain_hash']}
        
        data_string = json.dumps(static_data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def _hash_project_data(self, project_data: dict) -> str:
        """Create hash of project data for integrity"""
        # Remove dynamic fields
        static_data = {k: v for k, v in project_data.items() 
                      if k not in ['last_updated', 'submission_date']}
        
        data_string = json.dumps(static_data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def get_blockchain_stats(self) -> dict:
        """Get overall blockchain statistics"""
        contract_stats = self.smart_contract.get_contract_stats()
        
        return {
            'blockchain': {
                'total_projects': len(self.project_registry),
                'verified_projects': len([p for p in self.project_registry.values() 
                                        if p['verification_status'] == 'verified']),
                'pending_projects': len([p for p in self.project_registry.values() 
                                       if p['verification_status'] == 'pending'])
            },
            'smart_contract': contract_stats,
            'verification_nodes': self.verification_nodes
        }

# Global blockchain MRV instance
blockchain_mrv = BlockchainMRV()