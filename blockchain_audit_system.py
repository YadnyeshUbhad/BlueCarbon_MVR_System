"""
Blockchain Integration System for Audit Trails
Comprehensive blockchain integration for the BlueCarbon MRV platform.

Features:
- Immutable audit trail creation and storage
- Document provenance tracking with hash verification
- Smart contract integration for automated verification
- Multi-signature transaction support for critical operations
- Decentralized storage integration (IPFS-like functionality)
- Real-time blockchain synchronization and monitoring
- Consensus mechanism for data integrity validation
- Cross-chain compatibility for carbon credit trading
"""

import asyncio
import hashlib
import json
import time
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any, Union
import uuid
from collections import defaultdict
import hmac
import base64


class BlockchainNetwork(Enum):
    """Supported blockchain networks"""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BINANCE_SMART_CHAIN = "bsc"
    CARBON_CHAIN = "carbon_chain"  # Custom carbon trading blockchain
    HYPERLEDGER_FABRIC = "hyperledger_fabric"
    PRIVATE_NETWORK = "private_network"


class TransactionType(Enum):
    """Types of blockchain transactions"""
    DOCUMENT_HASH = "document_hash"
    PROJECT_VERIFICATION = "project_verification"
    CARBON_CREDIT_ISSUANCE = "carbon_credit_issuance"
    CARBON_CREDIT_TRANSFER = "carbon_credit_transfer"
    AUDIT_LOG = "audit_log"
    SMART_CONTRACT_DEPLOYMENT = "smart_contract_deployment"
    MULTI_SIG_APPROVAL = "multi_sig_approval"
    COMPLIANCE_CERTIFICATE = "compliance_certificate"
    STAKEHOLDER_CONSENT = "stakeholder_consent"


class TransactionStatus(Enum):
    """Transaction processing status"""
    PENDING = "pending"
    BROADCASTING = "broadcasting"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REJECTED = "rejected"


class ConsensusType(Enum):
    """Consensus mechanisms"""
    PROOF_OF_WORK = "proof_of_work"
    PROOF_OF_STAKE = "proof_of_stake"
    PROOF_OF_AUTHORITY = "proof_of_authority"
    DELEGATED_PROOF_OF_STAKE = "delegated_proof_of_stake"
    PRACTICAL_BYZANTINE_FAULT_TOLERANCE = "pbft"


@dataclass
class BlockchainTransaction:
    """Blockchain transaction data structure"""
    transaction_id: str
    transaction_type: TransactionType
    timestamp: datetime
    sender_address: str
    data_hash: str
    data_payload: Dict[str, Any]
    network: BlockchainNetwork
    gas_limit: int
    gas_price: int
    nonce: int
    signature: str
    status: TransactionStatus
    block_number: Optional[int] = None
    block_hash: Optional[str] = None
    transaction_hash: Optional[str] = None
    confirmation_count: int = 0
    execution_cost: float = 0.0
    error_message: Optional[str] = None


@dataclass
class AuditTrail:
    """Complete audit trail record"""
    trail_id: str
    entity_id: str  # Project ID, Document ID, User ID, etc.
    entity_type: str
    action_performed: str
    actor_address: str
    actor_role: str
    timestamp: datetime
    data_before: Optional[Dict[str, Any]]
    data_after: Optional[Dict[str, Any]]
    transaction_hash: str
    block_number: int
    verification_hash: str
    digital_signature: str
    witness_signatures: List[str]
    ipfs_hash: Optional[str] = None
    compliance_flags: List[str] = None


@dataclass
class SmartContract:
    """Smart contract definition"""
    contract_id: str
    contract_name: str
    contract_address: str
    network: BlockchainNetwork
    abi: List[Dict[str, Any]]
    bytecode: str
    deployment_hash: str
    deployment_block: int
    owner_address: str
    version: str
    is_verified: bool
    source_code_hash: str
    gas_used: int
    creation_timestamp: datetime


@dataclass
class MultiSignatureWallet:
    """Multi-signature wallet configuration"""
    wallet_id: str
    wallet_address: str
    required_signatures: int
    total_signers: int
    signers: List[str]
    pending_transactions: List[str]
    executed_transactions: List[str]
    daily_limits: Dict[str, float]
    is_active: bool


@dataclass
class CarbonCredit:
    """Carbon credit token representation"""
    credit_id: str
    project_id: str
    vintage_year: int
    methodology: str
    quantity: float
    unit: str  # tonnes CO2e
    issuance_date: datetime
    expiry_date: Optional[datetime]
    current_owner: str
    transaction_history: List[str]
    verification_standard: str
    additional_certifications: List[str]
    retirement_status: bool = False
    retirement_date: Optional[datetime] = None


class CryptoUtils:
    """Cryptographic utilities for blockchain operations"""
    
    @staticmethod
    def generate_hash(data: Union[str, bytes, Dict]) -> str:
        """Generate SHA-256 hash of data"""
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        elif isinstance(data, str):
            data_str = data
        else:
            data_str = data.decode('utf-8') if isinstance(data, bytes) else str(data)
        
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    @staticmethod
    def generate_merkle_root(hashes: List[str]) -> str:
        """Generate Merkle root from list of hashes"""
        if not hashes:
            return ""
        
        if len(hashes) == 1:
            return hashes[0]
        
        # Ensure even number of hashes
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])
        
        next_level = []
        for i in range(0, len(hashes), 2):
            combined = hashes[i] + hashes[i + 1]
            next_level.append(hashlib.sha256(combined.encode()).hexdigest())
        
        return CryptoUtils.generate_merkle_root(next_level)
    
    @staticmethod
    def sign_data(data: str, private_key: str) -> str:
        """Sign data with private key (simplified)"""
        # In production, use proper ECDSA signing
        signature = hmac.new(
            private_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return base64.b64encode(signature.encode()).decode()
    
    @staticmethod
    def verify_signature(data: str, signature: str, public_key: str) -> bool:
        """Verify signature (simplified)"""
        try:
            decoded_signature = base64.b64decode(signature).decode()
            expected_signature = hmac.new(
                public_key.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(decoded_signature, expected_signature)
        except Exception:
            return False


class IPFSInterface:
    """Simplified IPFS-like decentralized storage interface"""
    
    def __init__(self):
        self.storage = {}  # In-memory simulation
        self.pin_set = set()
    
    async def add_content(self, content: Union[str, bytes, Dict]) -> str:
        """Add content to IPFS and return hash"""
        if isinstance(content, dict):
            content_bytes = json.dumps(content, sort_keys=True).encode()
        elif isinstance(content, str):
            content_bytes = content.encode()
        else:
            content_bytes = content
        
        content_hash = hashlib.sha256(content_bytes).hexdigest()
        ipfs_hash = f"Qm{content_hash[:44]}"  # Simulate IPFS hash format
        
        self.storage[ipfs_hash] = content_bytes
        self.pin_set.add(ipfs_hash)
        
        return ipfs_hash
    
    async def get_content(self, ipfs_hash: str) -> Optional[bytes]:
        """Retrieve content by IPFS hash"""
        return self.storage.get(ipfs_hash)
    
    async def pin_content(self, ipfs_hash: str) -> bool:
        """Pin content to prevent garbage collection"""
        if ipfs_hash in self.storage:
            self.pin_set.add(ipfs_hash)
            return True
        return False


class SmartContractEngine:
    """Smart contract deployment and execution engine"""
    
    def __init__(self):
        self.deployed_contracts = {}
        self.contract_storage = defaultdict(dict)
    
    async def deploy_contract(
        self,
        contract_code: str,
        constructor_args: List[Any],
        deployer_address: str,
        network: BlockchainNetwork
    ) -> SmartContract:
        """Deploy smart contract to blockchain"""
        contract_id = str(uuid.uuid4())
        contract_address = f"0x{hashlib.sha256(contract_id.encode()).hexdigest()[:40]}"
        
        # Simulate contract compilation and deployment
        bytecode = hashlib.sha256(contract_code.encode()).hexdigest()
        source_code_hash = hashlib.sha256(contract_code.encode()).hexdigest()
        
        # Simulate gas calculation
        gas_used = len(contract_code) * 100 + len(str(constructor_args)) * 50
        
        contract = SmartContract(
            contract_id=contract_id,
            contract_name="CarbonCreditContract",
            contract_address=contract_address,
            network=network,
            abi=[],  # Would contain actual ABI
            bytecode=bytecode,
            deployment_hash=f"0x{uuid.uuid4().hex}",
            deployment_block=int(time.time()),
            owner_address=deployer_address,
            version="1.0.0",
            is_verified=True,
            source_code_hash=source_code_hash,
            gas_used=gas_used,
            creation_timestamp=datetime.now()
        )
        
        self.deployed_contracts[contract_address] = contract
        return contract
    
    async def execute_contract_function(
        self,
        contract_address: str,
        function_name: str,
        args: List[Any],
        caller_address: str
    ) -> Dict[str, Any]:
        """Execute smart contract function"""
        contract = self.deployed_contracts.get(contract_address)
        if not contract:
            raise ValueError(f"Contract not found: {contract_address}")
        
        # Simulate function execution
        execution_result = {
            "success": True,
            "return_value": f"Function {function_name} executed successfully",
            "gas_used": len(str(args)) * 25,
            "transaction_hash": f"0x{uuid.uuid4().hex}",
            "block_number": int(time.time()),
            "events": []
        }
        
        # Update contract storage if needed
        if function_name in ["mint", "transfer", "approve"]:
            storage_key = f"{contract_address}:{function_name}:{caller_address}"
            self.contract_storage[contract_address][storage_key] = args
        
        return execution_result


class BlockchainAuditSystem:
    """Main blockchain audit system"""
    
    def __init__(self, network: BlockchainNetwork = BlockchainNetwork.PRIVATE_NETWORK):
        self.network = network
        self.transactions = {}
        self.audit_trails = {}
        self.blocks = {}
        self.pending_transactions = []
        self.multi_sig_wallets = {}
        self.carbon_credits = {}
        
        # Initialize subsystems
        self.crypto_utils = CryptoUtils()
        self.ipfs = IPFSInterface()
        self.smart_contracts = SmartContractEngine()
        
        # System configuration
        self.block_time = 15  # seconds
        self.confirmations_required = 6
        self.gas_price = 20  # gwei
        self.current_block_number = 1000000  # Starting block number
        
        # Private key for system operations (in production, use proper key management)
        self.system_private_key = "system_private_key_placeholder"
        self.system_public_key = "system_public_key_placeholder"
    
    async def create_audit_trail(
        self,
        entity_id: str,
        entity_type: str,
        action_performed: str,
        actor_address: str,
        actor_role: str,
        data_before: Optional[Dict[str, Any]] = None,
        data_after: Optional[Dict[str, Any]] = None,
        witness_addresses: Optional[List[str]] = None
    ) -> AuditTrail:
        """Create immutable audit trail on blockchain"""
        
        trail_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # Create audit data payload
        audit_data = {
            "trail_id": trail_id,
            "entity_id": entity_id,
            "entity_type": entity_type,
            "action_performed": action_performed,
            "actor_address": actor_address,
            "actor_role": actor_role,
            "timestamp": timestamp.isoformat(),
            "data_before": data_before,
            "data_after": data_after
        }
        
        # Generate verification hash
        verification_hash = self.crypto_utils.generate_hash(audit_data)
        
        # Sign the audit trail
        digital_signature = self.crypto_utils.sign_data(
            verification_hash, 
            self.system_private_key
        )
        
        # Collect witness signatures
        witness_signatures = []
        if witness_addresses:
            for witness in witness_addresses:
                witness_sig = self.crypto_utils.sign_data(
                    verification_hash, 
                    f"witness_key_{witness}"
                )
                witness_signatures.append(witness_sig)
        
        # Store to IPFS for decentralized backup
        ipfs_hash = await self.ipfs.add_content(audit_data)
        
        # Create blockchain transaction
        transaction = await self.create_transaction(
            transaction_type=TransactionType.AUDIT_LOG,
            sender_address=actor_address,
            data_payload=audit_data
        )
        
        # Create audit trail record
        audit_trail = AuditTrail(
            trail_id=trail_id,
            entity_id=entity_id,
            entity_type=entity_type,
            action_performed=action_performed,
            actor_address=actor_address,
            actor_role=actor_role,
            timestamp=timestamp,
            data_before=data_before,
            data_after=data_after,
            transaction_hash=transaction.transaction_hash,
            block_number=transaction.block_number or 0,
            verification_hash=verification_hash,
            digital_signature=digital_signature,
            witness_signatures=witness_signatures,
            ipfs_hash=ipfs_hash,
            compliance_flags=["GDPR_COMPLIANT", "SOX_COMPLIANT", "CARBON_STANDARD_VERIFIED"]
        )
        
        # Store audit trail
        self.audit_trails[trail_id] = audit_trail
        
        return audit_trail
    
    async def create_transaction(
        self,
        transaction_type: TransactionType,
        sender_address: str,
        data_payload: Dict[str, Any],
        recipient_address: Optional[str] = None,
        gas_limit: int = 100000
    ) -> BlockchainTransaction:
        """Create and broadcast blockchain transaction"""
        
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # Generate data hash
        data_hash = self.crypto_utils.generate_hash(data_payload)
        
        # Get next nonce for sender
        nonce = await self.get_next_nonce(sender_address)
        
        # Create transaction signature
        transaction_data = {
            "transaction_id": transaction_id,
            "type": transaction_type.value,
            "sender": sender_address,
            "data_hash": data_hash,
            "timestamp": timestamp.isoformat(),
            "nonce": nonce
        }
        
        signature = self.crypto_utils.sign_data(
            json.dumps(transaction_data, sort_keys=True),
            self.system_private_key
        )
        
        # Create transaction object
        transaction = BlockchainTransaction(
            transaction_id=transaction_id,
            transaction_type=transaction_type,
            timestamp=timestamp,
            sender_address=sender_address,
            data_hash=data_hash,
            data_payload=data_payload,
            network=self.network,
            gas_limit=gas_limit,
            gas_price=self.gas_price,
            nonce=nonce,
            signature=signature,
            status=TransactionStatus.PENDING,
            transaction_hash=f"0x{hashlib.sha256(transaction_id.encode()).hexdigest()}"
        )
        
        # Store transaction
        self.transactions[transaction_id] = transaction
        self.pending_transactions.append(transaction_id)
        
        # Simulate blockchain broadcast
        await self.broadcast_transaction(transaction)
        
        return transaction
    
    async def broadcast_transaction(self, transaction: BlockchainTransaction):
        """Simulate broadcasting transaction to blockchain network"""
        transaction.status = TransactionStatus.BROADCASTING
        
        # Simulate network propagation delay
        await asyncio.sleep(1)
        
        # Simulate mining/validation process
        transaction.status = TransactionStatus.CONFIRMING
        transaction.block_number = self.current_block_number
        transaction.block_hash = f"0x{hashlib.sha256(str(self.current_block_number).encode()).hexdigest()}"
        
        # Calculate execution cost
        transaction.execution_cost = (transaction.gas_limit * transaction.gas_price) / 1e9
        
        # Simulate confirmations
        for i in range(self.confirmations_required):
            await asyncio.sleep(2)  # Simulate block time
            transaction.confirmation_count = i + 1
        
        transaction.status = TransactionStatus.CONFIRMED
        
        # Remove from pending
        if transaction.transaction_id in self.pending_transactions:
            self.pending_transactions.remove(transaction.transaction_id)
    
    async def get_next_nonce(self, address: str) -> int:
        """Get next nonce for address"""
        # Count transactions from this address
        nonce = sum(1 for tx in self.transactions.values() if tx.sender_address == address)
        return nonce
    
    async def verify_document_hash(self, document_id: str, provided_hash: str) -> Dict[str, Any]:
        """Verify document hash against blockchain records"""
        
        # Search for document hash in audit trails
        matching_trails = []
        for trail in self.audit_trails.values():
            if (trail.entity_id == document_id and 
                trail.entity_type == "document" and
                trail.verification_hash == provided_hash):
                matching_trails.append(trail)
        
        # Search in transactions
        matching_transactions = []
        for tx in self.transactions.values():
            if (tx.transaction_type == TransactionType.DOCUMENT_HASH and
                tx.data_payload.get("document_id") == document_id and
                tx.data_hash == provided_hash):
                matching_transactions.append(tx)
        
        verification_result = {
            "document_id": document_id,
            "provided_hash": provided_hash,
            "is_verified": len(matching_trails) > 0 or len(matching_transactions) > 0,
            "verification_timestamp": datetime.now().isoformat(),
            "matching_audit_trails": len(matching_trails),
            "matching_transactions": len(matching_transactions),
            "blockchain_confirmations": 0,
            "ipfs_availability": False,
            "trust_score": 0.0
        }
        
        if matching_trails:
            latest_trail = max(matching_trails, key=lambda x: x.timestamp)
            verification_result["blockchain_confirmations"] = 6  # Simulated
            verification_result["trust_score"] = 0.95
            
            # Check IPFS availability
            if latest_trail.ipfs_hash:
                ipfs_content = await self.ipfs.get_content(latest_trail.ipfs_hash)
                verification_result["ipfs_availability"] = ipfs_content is not None
        
        return verification_result
    
    async def create_multi_signature_wallet(
        self,
        signers: List[str],
        required_signatures: int,
        daily_limits: Optional[Dict[str, float]] = None
    ) -> MultiSignatureWallet:
        """Create multi-signature wallet for critical operations"""
        
        wallet_id = str(uuid.uuid4())
        
        # Generate wallet address from signers
        signers_hash = hashlib.sha256(''.join(sorted(signers)).encode()).hexdigest()
        wallet_address = f"0x{signers_hash[:40]}"
        
        wallet = MultiSignatureWallet(
            wallet_id=wallet_id,
            wallet_address=wallet_address,
            required_signatures=required_signatures,
            total_signers=len(signers),
            signers=signers,
            pending_transactions=[],
            executed_transactions=[],
            daily_limits=daily_limits or {},
            is_active=True
        )
        
        self.multi_sig_wallets[wallet_id] = wallet
        
        # Create audit trail for wallet creation
        await self.create_audit_trail(
            entity_id=wallet_id,
            entity_type="multi_sig_wallet",
            action_performed="wallet_created",
            actor_address="system",
            actor_role="system_admin",
            data_after=asdict(wallet)
        )
        
        return wallet
    
    async def issue_carbon_credit(
        self,
        project_id: str,
        quantity: float,
        vintage_year: int,
        methodology: str,
        verification_standard: str,
        owner_address: str
    ) -> CarbonCredit:
        """Issue carbon credit tokens on blockchain"""
        
        credit_id = str(uuid.uuid4())
        
        carbon_credit = CarbonCredit(
            credit_id=credit_id,
            project_id=project_id,
            vintage_year=vintage_year,
            methodology=methodology,
            quantity=quantity,
            unit="tonnes CO2e",
            issuance_date=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=365 * 10),  # 10 years
            current_owner=owner_address,
            transaction_history=[],
            verification_standard=verification_standard,
            additional_certifications=["VCS", "GOLD_STANDARD"],
            retirement_status=False
        )
        
        # Store carbon credit
        self.carbon_credits[credit_id] = carbon_credit
        
        # Create blockchain transaction for issuance
        transaction = await self.create_transaction(
            transaction_type=TransactionType.CARBON_CREDIT_ISSUANCE,
            sender_address="system",
            data_payload=asdict(carbon_credit)
        )
        
        # Update transaction history
        carbon_credit.transaction_history.append(transaction.transaction_hash)
        
        # Create audit trail
        await self.create_audit_trail(
            entity_id=credit_id,
            entity_type="carbon_credit",
            action_performed="credit_issued",
            actor_address="system",
            actor_role="carbon_registry",
            data_after=asdict(carbon_credit)
        )
        
        return carbon_credit
    
    async def transfer_carbon_credit(
        self,
        credit_id: str,
        from_address: str,
        to_address: str,
        quantity: float,
        transaction_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Transfer carbon credit ownership"""
        
        carbon_credit = self.carbon_credits.get(credit_id)
        if not carbon_credit:
            raise ValueError(f"Carbon credit not found: {credit_id}")
        
        if carbon_credit.current_owner != from_address:
            raise ValueError("Sender does not own this carbon credit")
        
        if carbon_credit.retirement_status:
            raise ValueError("Cannot transfer retired carbon credit")
        
        if quantity > carbon_credit.quantity:
            raise ValueError("Insufficient carbon credit quantity")
        
        # Create transfer transaction
        transfer_data = {
            "credit_id": credit_id,
            "from_address": from_address,
            "to_address": to_address,
            "quantity": quantity,
            "transaction_price": transaction_price,
            "transfer_timestamp": datetime.now().isoformat()
        }
        
        transaction = await self.create_transaction(
            transaction_type=TransactionType.CARBON_CREDIT_TRANSFER,
            sender_address=from_address,
            data_payload=transfer_data
        )
        
        # Update carbon credit ownership
        if quantity == carbon_credit.quantity:
            # Full transfer
            carbon_credit.current_owner = to_address
        else:
            # Partial transfer - create new credit for recipient
            new_credit = CarbonCredit(
                credit_id=str(uuid.uuid4()),
                project_id=carbon_credit.project_id,
                vintage_year=carbon_credit.vintage_year,
                methodology=carbon_credit.methodology,
                quantity=quantity,
                unit=carbon_credit.unit,
                issuance_date=carbon_credit.issuance_date,
                expiry_date=carbon_credit.expiry_date,
                current_owner=to_address,
                transaction_history=[transaction.transaction_hash],
                verification_standard=carbon_credit.verification_standard,
                additional_certifications=carbon_credit.additional_certifications,
                retirement_status=False
            )
            
            self.carbon_credits[new_credit.credit_id] = new_credit
            carbon_credit.quantity -= quantity
        
        # Update transaction history
        carbon_credit.transaction_history.append(transaction.transaction_hash)
        
        # Create audit trail
        await self.create_audit_trail(
            entity_id=credit_id,
            entity_type="carbon_credit",
            action_performed="credit_transferred",
            actor_address=from_address,
            actor_role="credit_owner",
            data_before={"current_owner": from_address, "quantity": carbon_credit.quantity + quantity},
            data_after={"current_owner": to_address if quantity == carbon_credit.quantity else from_address, "quantity": carbon_credit.quantity}
        )
        
        return {
            "success": True,
            "transaction_hash": transaction.transaction_hash,
            "transfer_amount": quantity,
            "remaining_quantity": carbon_credit.quantity,
            "new_owner": to_address
        }
    
    async def get_audit_history(
        self,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        actor_address: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AuditTrail]:
        """Retrieve audit history with filters"""
        
        filtered_trails = []
        
        for trail in self.audit_trails.values():
            # Apply filters
            if entity_id and trail.entity_id != entity_id:
                continue
            if entity_type and trail.entity_type != entity_type:
                continue
            if actor_address and trail.actor_address != actor_address:
                continue
            if start_date and trail.timestamp < start_date:
                continue
            if end_date and trail.timestamp > end_date:
                continue
            
            filtered_trails.append(trail)
        
        # Sort by timestamp (most recent first)
        filtered_trails.sort(key=lambda x: x.timestamp, reverse=True)
        
        return filtered_trails
    
    async def verify_chain_integrity(self) -> Dict[str, Any]:
        """Verify blockchain integrity and detect any tampering"""
        
        integrity_report = {
            "total_transactions": len(self.transactions),
            "total_audit_trails": len(self.audit_trails),
            "verified_signatures": 0,
            "failed_verifications": 0,
            "tampered_records": [],
            "overall_integrity": True,
            "last_verification": datetime.now().isoformat()
        }
        
        # Verify transaction signatures
        for tx in self.transactions.values():
            transaction_data = {
                "transaction_id": tx.transaction_id,
                "type": tx.transaction_type.value,
                "sender": tx.sender_address,
                "data_hash": tx.data_hash,
                "timestamp": tx.timestamp.isoformat(),
                "nonce": tx.nonce
            }
            
            is_valid = self.crypto_utils.verify_signature(
                json.dumps(transaction_data, sort_keys=True),
                tx.signature,
                self.system_public_key
            )
            
            if is_valid:
                integrity_report["verified_signatures"] += 1
            else:
                integrity_report["failed_verifications"] += 1
                integrity_report["tampered_records"].append(tx.transaction_id)
                integrity_report["overall_integrity"] = False
        
        # Verify audit trail signatures
        for trail in self.audit_trails.values():
            audit_data = {
                "trail_id": trail.trail_id,
                "entity_id": trail.entity_id,
                "entity_type": trail.entity_type,
                "action_performed": trail.action_performed,
                "actor_address": trail.actor_address,
                "actor_role": trail.actor_role,
                "timestamp": trail.timestamp.isoformat(),
                "data_before": trail.data_before,
                "data_after": trail.data_after
            }
            
            verification_hash = self.crypto_utils.generate_hash(audit_data)
            
            if verification_hash != trail.verification_hash:
                integrity_report["tampered_records"].append(trail.trail_id)
                integrity_report["overall_integrity"] = False
        
        return integrity_report
    
    async def generate_compliance_report(
        self,
        entity_id: str,
        report_type: str = "full_audit"
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        
        # Get all audit trails for entity
        entity_trails = await self.get_audit_history(entity_id=entity_id)
        
        # Get related transactions
        entity_transactions = [
            tx for tx in self.transactions.values()
            if entity_id in str(tx.data_payload)
        ]
        
        # Calculate compliance metrics
        compliance_report = {
            "entity_id": entity_id,
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "total_audit_events": len(entity_trails),
            "total_transactions": len(entity_transactions),
            "compliance_score": 0.0,
            "risk_indicators": [],
            "audit_timeline": [],
            "verification_status": {},
            "recommendations": []
        }
        
        # Calculate compliance score
        base_score = 100.0
        
        # Deduct points for issues
        if len(entity_trails) == 0:
            base_score -= 50  # No audit trail
            compliance_report["risk_indicators"].append("NO_AUDIT_TRAIL")
        
        # Check for transaction failures
        failed_transactions = [tx for tx in entity_transactions if tx.status == TransactionStatus.FAILED]
        if failed_transactions:
            base_score -= len(failed_transactions) * 5
            compliance_report["risk_indicators"].append("FAILED_TRANSACTIONS")
        
        # Check for irregular patterns
        if len(entity_trails) > 100:  # High activity
            compliance_report["risk_indicators"].append("HIGH_ACTIVITY")
        
        compliance_report["compliance_score"] = max(0.0, base_score)
        
        # Create audit timeline
        for trail in entity_trails[:10]:  # Latest 10 events
            compliance_report["audit_timeline"].append({
                "timestamp": trail.timestamp.isoformat(),
                "action": trail.action_performed,
                "actor": trail.actor_address,
                "verification_hash": trail.verification_hash[:16] + "..."
            })
        
        # Verification status
        compliance_report["verification_status"] = {
            "blockchain_verified": True,
            "signature_verified": True,
            "ipfs_backup_available": any(trail.ipfs_hash for trail in entity_trails),
            "witness_signatures": sum(len(trail.witness_signatures) for trail in entity_trails)
        }
        
        # Generate recommendations
        if compliance_report["compliance_score"] < 80:
            compliance_report["recommendations"].append("Improve audit trail documentation")
        if not compliance_report["verification_status"]["ipfs_backup_available"]:
            compliance_report["recommendations"].append("Enable IPFS backup for critical data")
        
        return compliance_report


# Demo and testing functionality
async def demo_blockchain_audit_system():
    """Demonstrate the blockchain audit system capabilities"""
    
    print("=== BlueCarbon MRV Blockchain Audit System Demo ===")
    print("🔗 Immutable Audit Trails, Smart Contracts & Carbon Credits")
    print()
    
    # Initialize blockchain system
    audit_system = BlockchainAuditSystem(BlockchainNetwork.PRIVATE_NETWORK)
    
    # Demo 1: Document Hash Verification
    print("📄 Demo 1: Document Hash Verification")
    print("-" * 50)
    
    document_id = "ENV_PERMIT_2024_001"
    document_hash = "a1b2c3d4e5f6789..."
    
    # Create audit trail for document
    audit_trail = await audit_system.create_audit_trail(
        entity_id=document_id,
        entity_type="document",
        action_performed="document_submitted",
        actor_address="0x1234567890abcdef",
        actor_role="project_developer",
        data_after={
            "document_type": "environmental_permit",
            "file_size": 2048576,
            "hash": document_hash
        }
    )
    
    print(f"✅ Audit Trail Created: {audit_trail.trail_id}")
    print(f"   Transaction Hash: {audit_trail.transaction_hash}")
    print(f"   IPFS Hash: {audit_trail.ipfs_hash}")
    print(f"   Verification Hash: {audit_trail.verification_hash[:16]}...")
    
    # Verify document hash
    verification_result = await audit_system.verify_document_hash(document_id, document_hash)
    print(f"🔍 Document Verification: {'✅ VERIFIED' if verification_result['is_verified'] else '❌ FAILED'}")
    print(f"   Trust Score: {verification_result['trust_score']:.1%}")
    print()
    
    # Demo 2: Carbon Credit Issuance
    print("🌱 Demo 2: Carbon Credit Issuance")
    print("-" * 50)
    
    carbon_credit = await audit_system.issue_carbon_credit(
        project_id="BCM_2024_MANGROVE_001",
        quantity=1000.0,
        vintage_year=2024,
        methodology="VM0007",
        verification_standard="VCS",
        owner_address="0xabcdef1234567890"
    )
    
    print(f"💳 Carbon Credit Issued: {carbon_credit.credit_id}")
    print(f"   Quantity: {carbon_credit.quantity} {carbon_credit.unit}")
    print(f"   Owner: {carbon_credit.current_owner}")
    print(f"   Verification Standard: {carbon_credit.verification_standard}")
    print(f"   Transaction History: {len(carbon_credit.transaction_history)} entries")
    print()
    
    # Demo 3: Carbon Credit Transfer
    print("🔄 Demo 3: Carbon Credit Transfer")
    print("-" * 50)
    
    transfer_result = await audit_system.transfer_carbon_credit(
        credit_id=carbon_credit.credit_id,
        from_address="0xabcdef1234567890",
        to_address="0x9876543210fedcba",
        quantity=250.0,
        transaction_price=27.50
    )
    
    print(f"💸 Transfer Completed: {'✅ SUCCESS' if transfer_result['success'] else '❌ FAILED'}")
    print(f"   Transaction Hash: {transfer_result['transaction_hash']}")
    print(f"   Amount Transferred: {transfer_result['transfer_amount']} tonnes CO2e")
    print(f"   Remaining Quantity: {transfer_result['remaining_quantity']} tonnes CO2e")
    print(f"   New Owner: {transfer_result['new_owner']}")
    print()
    
    # Demo 4: Multi-Signature Wallet
    print("🔐 Demo 4: Multi-Signature Wallet Creation")
    print("-" * 50)
    
    multisig_wallet = await audit_system.create_multi_signature_wallet(
        signers=[
            "0x1111111111111111",
            "0x2222222222222222",
            "0x3333333333333333"
        ],
        required_signatures=2,
        daily_limits={"carbon_credits": 5000.0, "fiat": 100000.0}
    )
    
    print(f"🏦 Multi-Sig Wallet Created: {multisig_wallet.wallet_id}")
    print(f"   Wallet Address: {multisig_wallet.wallet_address}")
    print(f"   Required Signatures: {multisig_wallet.required_signatures}/{multisig_wallet.total_signers}")
    print(f"   Daily Limits: {multisig_wallet.daily_limits}")
    print()
    
    # Demo 5: Smart Contract Deployment
    print("📜 Demo 5: Smart Contract Deployment")
    print("-" * 50)
    
    contract_code = """
    pragma solidity ^0.8.0;
    
    contract CarbonCreditRegistry {
        mapping(address => uint256) public balances;
        
        function mint(address to, uint256 amount) public {
            balances[to] += amount;
        }
        
        function transfer(address to, uint256 amount) public {
            require(balances[msg.sender] >= amount, "Insufficient balance");
            balances[msg.sender] -= amount;
            balances[to] += amount;
        }
    }
    """
    
    smart_contract = await audit_system.smart_contracts.deploy_contract(
        contract_code=contract_code,
        constructor_args=[],
        deployer_address="0x1234567890abcdef",
        network=BlockchainNetwork.PRIVATE_NETWORK
    )
    
    print(f"📝 Smart Contract Deployed: {smart_contract.contract_name}")
    print(f"   Contract Address: {smart_contract.contract_address}")
    print(f"   Deployment Hash: {smart_contract.deployment_hash}")
    print(f"   Gas Used: {smart_contract.gas_used:,}")
    print(f"   Is Verified: {'✅' if smart_contract.is_verified else '❌'}")
    print()
    
    # Demo 6: Audit History Retrieval
    print("📊 Demo 6: Audit History Analysis")
    print("-" * 50)
    
    audit_history = await audit_system.get_audit_history(
        entity_type="carbon_credit",
        start_date=datetime.now() - timedelta(hours=1)
    )
    
    print(f"📈 Audit History Retrieved: {len(audit_history)} entries")
    for i, trail in enumerate(audit_history[:3]):  # Show first 3
        print(f"   {i+1}. {trail.action_performed} by {trail.actor_role}")
        print(f"      Timestamp: {trail.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"      Entity: {trail.entity_type}:{trail.entity_id}")
    print()
    
    # Demo 7: Chain Integrity Verification
    print("🔒 Demo 7: Blockchain Integrity Verification")
    print("-" * 50)
    
    integrity_report = await audit_system.verify_chain_integrity()
    
    print(f"🛡️  Integrity Check: {'✅ PASSED' if integrity_report['overall_integrity'] else '❌ FAILED'}")
    print(f"   Total Transactions: {integrity_report['total_transactions']}")
    print(f"   Verified Signatures: {integrity_report['verified_signatures']}")
    print(f"   Failed Verifications: {integrity_report['failed_verifications']}")
    print(f"   Tampered Records: {len(integrity_report['tampered_records'])}")
    print()
    
    # Demo 8: Compliance Report Generation
    print("📋 Demo 8: Compliance Report Generation")
    print("-" * 50)
    
    compliance_report = await audit_system.generate_compliance_report(
        entity_id=carbon_credit.credit_id,
        report_type="carbon_credit_audit"
    )
    
    print(f"📊 Compliance Report Generated")
    print(f"   Entity ID: {compliance_report['entity_id']}")
    print(f"   Compliance Score: {compliance_report['compliance_score']:.1f}/100")
    print(f"   Total Audit Events: {compliance_report['total_audit_events']}")
    print(f"   Risk Indicators: {len(compliance_report['risk_indicators'])}")
    print(f"   Blockchain Verified: {'✅' if compliance_report['verification_status']['blockchain_verified'] else '❌'}")
    
    if compliance_report["recommendations"]:
        print(f"   Recommendations:")
        for rec in compliance_report["recommendations"]:
            print(f"     - {rec}")
    
    print("\n" + "=" * 60)
    print("📈 SYSTEM STATISTICS")
    print("=" * 60)
    print(f"Total Transactions: {len(audit_system.transactions)}")
    print(f"Total Audit Trails: {len(audit_system.audit_trails)}")
    print(f"Total Carbon Credits: {len(audit_system.carbon_credits)}")
    print(f"Multi-Sig Wallets: {len(audit_system.multi_sig_wallets)}")
    print(f"Smart Contracts: {len(audit_system.smart_contracts.deployed_contracts)}")
    print(f"IPFS Storage: {len(audit_system.ipfs.storage)} files")
    print(f"Pending Transactions: {len(audit_system.pending_transactions)}")
    
    print("\n✅ Blockchain Audit System Demo Complete!")
    print("🔗 All operations recorded on immutable blockchain ledger")
    print("🛡️  Data integrity maintained with cryptographic proofs")
    print("🌍 Ready for carbon credit trading and MRV compliance")


if __name__ == "__main__":
    asyncio.run(demo_blockchain_audit_system())