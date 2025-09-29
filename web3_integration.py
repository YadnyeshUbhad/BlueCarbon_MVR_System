"""
Web3 Integration for Blue Carbon MRV System
Connects Flask app to deployed smart contracts
"""

import os
import json
from web3 import Web3
from dotenv import load_dotenv
import logging
from datetime import datetime

load_dotenv()

class Web3Integration:
    def __init__(self):
        """Initialize Web3 connection and contracts"""
        self.logger = logging.getLogger(__name__)
        
        # Load contract addresses from deployment
        self.load_contract_addresses()
        
        # Initialize Web3 connection
        self.w3 = None
        self.mrv_contract = None
        self.carbon_contract = None
        
        self.connect()
        self.load_contracts()
    
    def load_contract_addresses(self):
        """Load contract addresses from .env.contracts"""
        env_contracts_path = os.path.join('blockchain', '.env.contracts')
        
        if not os.path.exists(env_contracts_path):
            self.logger.error("Contract addresses file not found. Please deploy contracts first.")
            raise Exception("Contracts not deployed")
        
        with open(env_contracts_path, 'r') as f:
            content = f.read()
            
        # Parse contract addresses
        self.mrv_address = None
        self.carbon_address = None
        
        for line in content.split('\n'):
            if line.startswith('MRV_REGISTRY_ADDRESS='):
                self.mrv_address = line.split('=')[1]
            elif line.startswith('CARBON_TOKEN_ADDRESS='):
                self.carbon_address = line.split('=')[1]
        
        if not self.mrv_address or not self.carbon_address:
            raise Exception("Contract addresses not found in .env.contracts")
        
        self.logger.info(f"Loaded contract addresses: MRV={self.mrv_address}, Carbon={self.carbon_address}")
    
    def connect(self):
        """Connect to blockchain network"""
        try:
            # For local development, use Hardhat network
            rpc_url = os.getenv('WEB3_PROVIDER_URL', "http://127.0.0.1:8545")
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            if self.w3.is_connected():
                self.logger.info(f"Connected to blockchain at {rpc_url}")
                self.logger.info(f"Chain ID: {self.w3.eth.chain_id}")
            else:
                self.logger.error("Failed to connect to blockchain")
                raise Exception("Blockchain connection failed")
                
        except Exception as e:
            self.logger.error(f"Error connecting to blockchain: {e}")
            # Fallback to simulation mode
            self.w3 = None
    
    def load_contracts(self):
        """Load contract ABIs and create contract instances"""
        if not self.w3:
            return
        
        try:
            # Load ABIs from compiled contracts
            artifacts_path = 'blockchain/artifacts/contracts'
            
            # Load MRV Registry ABI
            mrv_abi_path = os.path.join(artifacts_path, 'MRVRegistry.sol', 'MRVRegistry.json')
            with open(mrv_abi_path, 'r') as f:
                mrv_artifact = json.load(f)
                mrv_abi = mrv_artifact['abi']
            
            # Load Carbon Token ABI
            carbon_abi_path = os.path.join(artifacts_path, 'CarbonCreditToken.sol', 'CarbonCreditToken.json')
            with open(carbon_abi_path, 'r') as f:
                carbon_artifact = json.load(f)
                carbon_abi = carbon_artifact['abi']
            
            # Create contract instances
            self.mrv_contract = self.w3.eth.contract(
                address=self.mrv_address,
                abi=mrv_abi
            )
            
            self.carbon_contract = self.w3.eth.contract(
                address=self.carbon_address,
                abi=carbon_abi
            )
            
            self.logger.info("Contracts loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading contracts: {e}")
            self.mrv_contract = None
            self.carbon_contract = None
    
    def is_connected(self):
        """Check if Web3 is connected"""
        return self.w3 is not None and self.w3.is_connected()
    
    def get_account(self):
        """Get the default account for transactions"""
        if not self.w3:
            return None
        
        # Iterate through accounts to find one with a balance
        for account in self.w3.eth.accounts:
            balance = self.w3.eth.get_balance(account)
            self.logger.info(f"Checking account: {account}, balance: {self.w3.from_wei(balance, 'ether')} ETH")
            if balance > 0:
                self.logger.info(f"Using funded account: {account} with balance: {self.w3.from_wei(balance, 'ether')} ETH")
                return account
        
        self.logger.error("No funded accounts found on the connected blockchain. Transactions will fail.")
        return None
    
    def create_mrv_record(self, project_name, location, carbon_amount):
        """Create a new MRV record on blockchain"""
        if not self.mrv_contract:
            self.logger.warning("MRV contract not available, using simulation")
            return f"sim_{int(datetime.now().timestamp())}"
        
        try:
            account = self.get_account()
            
            # Call contract function
            tx_hash = self.mrv_contract.functions.createRecord(
                project_name,
                location, 
                int(carbon_amount * 1000)  # Convert to integer (scaled by 1000)
            ).transact({'from': account})
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Get the record ID from events
            record_id = None
            for log in receipt.logs:
                try:
                    decoded = self.mrv_contract.events.MRVRecordCreated().processLog(log)
                    record_id = decoded.args.recordId
                    break
                except:
                    continue
            
            self.logger.info(f"MRV record created with ID: {record_id}")
            return record_id
            
        except Exception as e:
            self.logger.error(f"Error creating MRV record: {e}")
            return None
    
    def verify_mrv_record(self, record_id):
        """Verify an MRV record"""
        if not self.mrv_contract:
            self.logger.warning("MRV contract not available, using simulation")
            return True
        
        try:
            account = self.get_account()
            
            tx_hash = self.mrv_contract.functions.verifyRecord(
                record_id
            ).transact({'from': account})
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            self.logger.info(f"MRV record {record_id} verified")
            return True
            
        except Exception as e:
            self.logger.error(f"Error verifying MRV record: {e}")
            return False
    
    def mint_carbon_credits(self, ngo_address, project_id, project_name, amount):
        """Mint carbon credit tokens"""
        if not self.carbon_contract:
            self.logger.warning("Carbon contract not available, using simulation")
            return f"token_{int(datetime.now().timestamp())}"
        
        try:
            account = self.get_account()
            
            # Mint credits
            tx_hash = self.carbon_contract.functions.mintCredits(
                ngo_address,
                project_id,
                project_name,
                int(amount * 1000)  # Convert to integer (scaled by 1000)
            ).transact({'from': account})
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Get token ID from events
            token_id = None
            for log in receipt.logs:
                try:
                    decoded = self.carbon_contract.events.CreditsMinted().processLog(log)
                    token_id = decoded.args.tokenId
                    break
                except:
                    continue
            
            self.logger.info(f"Carbon credits minted with token ID: {token_id}")
            return token_id
            
        except Exception as e:
            self.logger.error(f"Error minting carbon credits: {e}")
            return None
    
    def transfer_credits(self, from_address, to_address, token_id, amount):
        """Transfer carbon credits between addresses"""
        if not self.carbon_contract:
            self.logger.warning("Carbon contract not available, using simulation")
            return True
        
        try:
            account = self.get_account()
            
            # Note: This is a simplified version. Real ERC-1155 transfers need approval
            tx_hash = self.carbon_contract.functions.safeTransferFrom(
                from_address,
                to_address,
                token_id,
                int(amount * 1000),  # Convert to integer
                b''  # Empty data
            ).transact({'from': account})
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            self.logger.info(f"Credits transferred: {amount} tokens from {from_address} to {to_address}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error transferring credits: {e}")
            return False
    
    def get_credit_balance(self, address, token_id):
        """Get carbon credit balance for an address"""
        if not self.carbon_contract:
            return 0
        
        try:
            balance = self.carbon_contract.functions.balanceOf(address, token_id).call()
            return balance / 1000  # Scale back down
            
        except Exception as e:
            self.logger.error(f"Error getting balance: {e}")
            return 0
    
    def get_blockchain_stats(self):
        """Get blockchain statistics"""
        stats = {
            'connected': self.is_connected(),
            'network': 'Hardhat Local' if self.is_connected() else 'Simulation',
            'timestamp': datetime.now().isoformat()
        }
        
        if self.is_connected():
            try:
                stats['chain_id'] = self.w3.eth.chain_id
                stats['block_number'] = self.w3.eth.block_number
                
                account = self.get_account()

                if self.mrv_contract:
                    try:
                        stats['total_mrv_records'] = self.mrv_contract.functions.getTotalRecords().call({'from': account})
                    except Exception as e:
                        self.logger.error(f"Error calling getTotalRecords on MRV contract: {e}")
                        stats['total_mrv_records'] = 'Error'
                
                if self.carbon_contract:
                    try:
                        stats['total_token_batches'] = self.carbon_contract.functions.getTotalBatches().call({'from': account})
                        stats['total_credits_issued'] = self.carbon_contract.functions.totalCreditsIssued().call({'from': account}) / 1000
                    except Exception as e:
                        self.logger.error(f"Error calling Carbon contract functions (getTotalBatches/totalCreditsIssued): {e}")
                        stats['total_token_batches'] = 'Error'
                        stats['total_credits_issued'] = 'Error'
                    
            except Exception as e:
                self.logger.error(f"Error getting blockchain stats: {e}")
        
        return stats

# Create global instance
web3_integration = Web3Integration()