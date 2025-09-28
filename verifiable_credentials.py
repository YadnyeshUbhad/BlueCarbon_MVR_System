"""
Verifiable Credentials (VC) Identity Module for BlueCarbon MRV System
Implements W3C Verifiable Credentials standard for secure identity verification
"""

import json
import hashlib
from datetime import datetime, timedelta
import random
import uuid


class VerifiableCredentialsManager:
    def __init__(self):
        self.issued_credentials = {}
        self.verified_identities = {}
        self.did_registry = {}  # Decentralized Identity Registry
        
    def generate_did(self, entity_type, entity_id):
        """Generate a Decentralized Identity (DID) for an entity"""
        did_method = "did:bluecarbon"
        unique_id = hashlib.sha256(f"{entity_type}:{entity_id}:{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        did = f"{did_method}:{entity_type}:{unique_id}"
        
        # Create DID Document
        did_document = {
            "@context": "https://www.w3.org/ns/did/v1",
            "id": did,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "verificationMethod": [
                {
                    "id": f"{did}#key-1",
                    "type": "Ed25519VerificationKey2018",
                    "controller": did,
                    "publicKeyBase58": self._generate_mock_public_key()
                }
            ],
            "authentication": [f"{did}#key-1"],
            "service": [
                {
                    "id": f"{did}#bluecarbon-service",
                    "type": "BlueCarbonMRVService",
                    "serviceEndpoint": "https://bluecarbon-mrv.gov.in"
                }
            ]
        }
        
        self.did_registry[did] = did_document
        return did
    
    def issue_identity_credential(self, entity_data, issuer_did="did:bluecarbon:authority:nccr"):
        """Issue a Verifiable Credential for identity verification"""
        
        credential_id = f"urn:uuid:{uuid.uuid4()}"
        subject_did = self.generate_did(entity_data['type'], entity_data['id'])
        
        credential = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://bluecarbon-mrv.gov.in/credentials/v1"
            ],
            "id": credential_id,
            "type": ["VerifiableCredential", "BlueCarbonIdentityCredential"],
            "issuer": {
                "id": issuer_did,
                "name": "National Centre for Coastal Research"
            },
            "issuanceDate": datetime.now().isoformat(),
            "expirationDate": (datetime.now() + timedelta(days=365)).isoformat(),
            "credentialSubject": {
                "id": subject_did,
                "type": entity_data['type'],
                "name": entity_data['name'],
                "organization": entity_data.get('organization', ''),
                "registrationNumber": entity_data.get('registration_number', ''),
                "verificationLevel": self._determine_verification_level(entity_data),
                "permissions": self._generate_permissions(entity_data['type']),
                "issuedBy": "NCCR BlueCarbon MRV System",
                "verificationMethod": f"{subject_did}#key-1"
            },
            "proof": {
                "type": "Ed25519Signature2018",
                "created": datetime.now().isoformat(),
                "verificationMethod": f"{issuer_did}#key-1",
                "proofPurpose": "assertionMethod",
                "jws": self._generate_mock_signature(credential_id, subject_did)
            }
        }
        
        # Store the credential
        self.issued_credentials[credential_id] = credential
        self.verified_identities[subject_did] = {
            'credential_id': credential_id,
            'verification_status': 'verified',
            'issued_date': datetime.now(),
            'entity_data': entity_data
        }
        
        return credential
    
    def verify_credential(self, credential_id_or_did):
        """Verify a Verifiable Credential or DID"""
        
        # Try to find by credential ID first
        if credential_id_or_did in self.issued_credentials:
            credential = self.issued_credentials[credential_id_or_did]
            
            # Check expiration
            expiration_date = datetime.fromisoformat(credential['expirationDate'].replace('Z', '+00:00'))
            if expiration_date < datetime.now():
                return {
                    'valid': False,
                    'reason': 'Credential has expired',
                    'expired_on': expiration_date.isoformat()
                }
            
            # Verify signature (mock verification)
            signature_valid = self._verify_mock_signature(
                credential['proof']['jws'],
                credential_id_or_did,
                credential['credentialSubject']['id']
            )
            
            return {
                'valid': signature_valid,
                'credential': credential,
                'verification_time': datetime.now().isoformat(),
                'issuer_trusted': True,  # Mock - in production, check trusted issuer list
                'subject_did': credential['credentialSubject']['id'],
                'permissions': credential['credentialSubject']['permissions']
            }
        
        # Try to find by DID
        elif credential_id_or_did in self.verified_identities:
            identity_data = self.verified_identities[credential_id_or_did]
            credential = self.issued_credentials[identity_data['credential_id']]
            
            return {
                'valid': True,
                'identity_verified': True,
                'did': credential_id_or_did,
                'credential': credential,
                'verification_status': identity_data['verification_status'],
                'entity_type': identity_data['entity_data']['type'],
                'permissions': credential['credentialSubject']['permissions']
            }
        
        else:
            return {
                'valid': False,
                'reason': 'Credential or DID not found in registry'
            }
    
    def revoke_credential(self, credential_id, reason=""):
        """Revoke a Verifiable Credential"""
        if credential_id in self.issued_credentials:
            credential = self.issued_credentials[credential_id]
            subject_did = credential['credentialSubject']['id']
            
            # Mark as revoked
            credential['credentialStatus'] = {
                'id': f"https://bluecarbon-mrv.gov.in/status/{credential_id}",
                'type': "RevocationList2020Status",
                "revocationListIndex": random.randint(1000, 9999),
                "revocationListCredential": "https://bluecarbon-mrv.gov.in/credentials/status/1",
                "revoked": True,
                "revocationReason": reason,
                "revocationDate": datetime.now().isoformat()
            }
            
            # Update verified identities
            if subject_did in self.verified_identities:
                self.verified_identities[subject_did]['verification_status'] = 'revoked'
                self.verified_identities[subject_did]['revocation_date'] = datetime.now()
                self.verified_identities[subject_did]['revocation_reason'] = reason
            
            return True
        return False
    
    def get_identity_profile(self, did):
        """Get comprehensive identity profile for a DID"""
        if did not in self.verified_identities:
            return None
            
        identity_data = self.verified_identities[did]
        credential = self.issued_credentials[identity_data['credential_id']]
        did_document = self.did_registry.get(did, {})
        
        # Calculate trust score based on various factors
        trust_score = self._calculate_trust_score(identity_data, credential)
        
        profile = {
            'did': did,
            'identity_data': identity_data['entity_data'],
            'credential_summary': {
                'id': identity_data['credential_id'],
                'issued_date': identity_data['issued_date'].isoformat(),
                'verification_level': credential['credentialSubject']['verificationLevel'],
                'status': identity_data['verification_status'],
                'expiration_date': credential['expirationDate'],
                'issuer': credential['issuer']['name']
            },
            'did_document': did_document,
            'trust_score': trust_score,
            'permissions': credential['credentialSubject']['permissions'],
            'verification_history': self._get_verification_history(did)
        }
        
        return profile
    
    def _determine_verification_level(self, entity_data):
        """Determine verification level based on entity data"""
        if entity_data['type'] == 'admin':
            return 'AUTHORITY'
        elif entity_data['type'] == 'ngo' and entity_data.get('registration_number'):
            return 'VERIFIED_ORGANIZATION'
        elif entity_data['type'] == 'industry' and entity_data.get('registration_number'):
            return 'VERIFIED_BUSINESS'
        elif entity_data['type'] == 'panchayat':
            return 'GOVERNMENT_ENTITY'
        else:
            return 'BASIC'
    
    def _generate_permissions(self, entity_type):
        """Generate permissions based on entity type"""
        base_permissions = ['read:public_data', 'read:own_data']
        
        if entity_type == 'admin':
            return base_permissions + [
                'read:all_data', 'write:all_data', 'verify:projects', 
                'issue:credits', 'manage:users', 'access:satellite_data',
                'access:drone_data', 'manage:blockchain'
            ]
        elif entity_type == 'ngo':
            return base_permissions + [
                'write:projects', 'read:project_data', 'submit:monitoring_data',
                'access:camera_tools', 'request:verification'
            ]
        elif entity_type == 'industry':
            return base_permissions + [
                'buy:carbon_credits', 'retire:carbon_credits', 'read:marketplace',
                'generate:reports'
            ]
        elif entity_type == 'panchayat':
            return base_permissions + [
                'write:community_projects', 'verify:local_data', 'read:regional_data'
            ]
        else:
            return base_permissions
    
    def _generate_mock_public_key(self):
        """Generate a mock public key for demonstration"""
        return hashlib.sha256(f"mock_public_key_{random.randint(1000, 9999)}".encode()).hexdigest()[:32]
    
    def _generate_mock_signature(self, credential_id, subject_did):
        """Generate a mock JWS signature for demonstration"""
        payload = f"{credential_id}:{subject_did}:{datetime.now().isoformat()}"
        signature = hashlib.sha256(payload.encode()).hexdigest()
        # Mock JWS format
        return f"eyJhbGciOiJFZDI1NTE5U2lnbmF0dXJlMjAxOCJ9.{signature[:32]}.{signature[32:]}"
    
    def _verify_mock_signature(self, jws, credential_id, subject_did):
        """Verify a mock JWS signature for demonstration"""
        # In a real implementation, this would verify the actual cryptographic signature
        return len(jws) > 50 and jws.startswith("eyJ")  # Basic mock verification
    
    def _calculate_trust_score(self, identity_data, credential):
        """Calculate trust score based on various factors"""
        score = 50  # Base score
        
        # Add points for verification level
        verification_level = credential['credentialSubject']['verificationLevel']
        if verification_level == 'AUTHORITY':
            score += 40
        elif verification_level == 'VERIFIED_ORGANIZATION':
            score += 30
        elif verification_level == 'VERIFIED_BUSINESS':
            score += 25
        elif verification_level == 'GOVERNMENT_ENTITY':
            score += 35
        else:
            score += 10
        
        # Add points for registration details
        if identity_data['entity_data'].get('registration_number'):
            score += 10
        
        # Deduct points if revoked
        if identity_data['verification_status'] == 'revoked':
            score = 0
        
        return min(score, 100)
    
    def _get_verification_history(self, did):
        """Get verification history for a DID"""
        # Mock verification history
        return [
            {
                'action': 'credential_issued',
                'timestamp': datetime.now().isoformat(),
                'actor': 'NCCR System',
                'details': 'Initial identity credential issued'
            },
            {
                'action': 'identity_verified',
                'timestamp': datetime.now().isoformat(),
                'actor': 'NCCR Admin',
                'details': 'Identity documents verified'
            }
        ]
    
    def get_system_statistics(self):
        """Get system-wide VC statistics"""
        total_credentials = len(self.issued_credentials)
        active_credentials = len([c for c in self.issued_credentials.values() 
                                if 'credentialStatus' not in c or not c.get('credentialStatus', {}).get('revoked', False)])
        revoked_credentials = total_credentials - active_credentials
        
        # Count by entity type
        entity_types = {}
        for identity in self.verified_identities.values():
            entity_type = identity['entity_data']['type']
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        
        return {
            'total_credentials_issued': total_credentials,
            'active_credentials': active_credentials,
            'revoked_credentials': revoked_credentials,
            'total_dids_registered': len(self.did_registry),
            'credentials_by_type': entity_types,
            'average_trust_score': self._calculate_average_trust_score(),
            'system_health': 'operational' if active_credentials > 0 else 'no_active_credentials'
        }
    
    def _calculate_average_trust_score(self):
        """Calculate average trust score across all identities"""
        if not self.verified_identities:
            return 0
        
        total_score = 0
        count = 0
        
        for did, identity_data in self.verified_identities.items():
            if identity_data['verification_status'] == 'verified':
                credential = self.issued_credentials[identity_data['credential_id']]
                trust_score = self._calculate_trust_score(identity_data, credential)
                total_score += trust_score
                count += 1
        
        return total_score / max(count, 1)


# Global VC manager instance
vc_manager = VerifiableCredentialsManager()