"""
Document AI Verification System with OCR
Advanced document processing system for BlueCarbon MRV platform.

Features:
- OCR text extraction from various document formats
- AI-powered document authenticity verification
- Fraud detection and anomaly analysis
- Document classification and metadata extraction
- Blockchain-ready hash generation for audit trails
- Real-time verification scoring and confidence levels
"""

import asyncio
import hashlib
import json
import re
import base64
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import cv2


class DocumentType(Enum):
    """Document types supported by the verification system"""
    ENVIRONMENTAL_PERMIT = "environmental_permit"
    LAND_OWNERSHIP = "land_ownership"
    PROJECT_PROPOSAL = "project_proposal"
    FINANCIAL_STATEMENT = "financial_statement"
    SURVEY_REPORT = "survey_report"
    COMPLIANCE_CERTIFICATE = "compliance_certificate"
    MONITORING_REPORT = "monitoring_report"
    THIRD_PARTY_VALIDATION = "third_party_validation"
    GOVERNMENT_APPROVAL = "government_approval"
    SATELLITE_IMAGERY = "satellite_imagery"
    FIELD_PHOTOS = "field_photos"
    TECHNICAL_DRAWINGS = "technical_drawings"


class VerificationStatus(Enum):
    """Document verification status"""
    PENDING = "pending"
    PROCESSING = "processing"
    VERIFIED = "verified"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"
    FRAUD_DETECTED = "fraud_detected"


class FraudIndicator(Enum):
    """Types of fraud indicators"""
    DOCUMENT_MANIPULATION = "document_manipulation"
    FAKE_SIGNATURE = "fake_signature"
    ALTERED_TEXT = "altered_text"
    INCONSISTENT_METADATA = "inconsistent_metadata"
    DUPLICATE_CONTENT = "duplicate_content"
    SUSPICIOUS_TIMING = "suspicious_timing"
    INVALID_AUTHORITY = "invalid_authority"
    MISMATCHED_COORDINATES = "mismatched_coordinates"


@dataclass
class DocumentMetadata:
    """Document metadata extraction results"""
    file_name: str
    file_size: int
    file_type: str
    creation_date: Optional[datetime]
    modification_date: Optional[datetime]
    author: Optional[str]
    title: Optional[str]
    pages: int
    language: str
    encoding: str


@dataclass
class OCRResult:
    """OCR processing results"""
    extracted_text: str
    confidence_score: float
    language_detected: str
    word_count: int
    character_count: int
    text_regions: List[Dict[str, Any]]
    coordinates: List[Tuple[int, int, int, int]]


@dataclass
class FraudAnalysis:
    """Fraud detection analysis results"""
    fraud_indicators: List[FraudIndicator]
    fraud_probability: float
    risk_score: float
    suspicious_patterns: List[str]
    timestamp_anomalies: List[Dict[str, Any]]
    content_inconsistencies: List[str]


@dataclass
class DocumentClassification:
    """Document classification results"""
    predicted_type: DocumentType
    confidence: float
    alternative_types: List[Tuple[DocumentType, float]]
    key_features: List[str]
    extracted_entities: Dict[str, List[str]]


@dataclass
class VerificationResult:
    """Complete document verification results"""
    document_id: str
    document_type: DocumentType
    status: VerificationStatus
    confidence_score: float
    authenticity_score: float
    metadata: DocumentMetadata
    ocr_result: OCRResult
    classification: DocumentClassification
    fraud_analysis: FraudAnalysis
    blockchain_hash: str
    verification_timestamp: datetime
    processing_time_ms: int
    reviewer_notes: Optional[str] = None


class OCRProcessor:
    """Advanced OCR processing with multiple engines"""
    
    def __init__(self):
        self.tesseract_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,;:!?-()[]{}/@#$%^&*+=_~`"\'<>|\\/'
        
    async def preprocess_image(self, image_data: bytes) -> np.ndarray:
        """Preprocess image for optimal OCR results"""
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Preprocessing pipeline
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Noise removal
        denoised = cv2.medianBlur(gray, 5)
        
        # Contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = np.ones((1,1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    async def extract_text_tesseract(self, image_data: bytes) -> OCRResult:
        """Extract text using Tesseract OCR"""
        try:
            # Preprocess image
            processed_image = await self.preprocess_image(image_data)
            
            # OCR with detailed data
            ocr_data = pytesseract.image_to_data(
                processed_image, 
                config=self.tesseract_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Extract text and confidence
            extracted_text = pytesseract.image_to_string(
                processed_image, 
                config=self.tesseract_config
            ).strip()
            
            # Calculate confidence
            confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Detect language
            try:
                detected_lang = pytesseract.image_to_osd(processed_image)
                lang_match = re.search(r'Script: (\w+)', detected_lang)
                language = lang_match.group(1) if lang_match else "Latin"
            except:
                language = "Unknown"
            
            # Extract text regions and coordinates
            text_regions = []
            coordinates = []
            
            for i in range(len(ocr_data['text'])):
                if int(ocr_data['conf'][i]) > 30:  # Filter low confidence
                    text_regions.append({
                        'text': ocr_data['text'][i],
                        'confidence': ocr_data['conf'][i],
                        'level': ocr_data['level'][i]
                    })
                    
                    coordinates.append((
                        ocr_data['left'][i],
                        ocr_data['top'][i],
                        ocr_data['left'][i] + ocr_data['width'][i],
                        ocr_data['top'][i] + ocr_data['height'][i]
                    ))
            
            return OCRResult(
                extracted_text=extracted_text,
                confidence_score=avg_confidence / 100.0,
                language_detected=language,
                word_count=len(extracted_text.split()),
                character_count=len(extracted_text),
                text_regions=text_regions,
                coordinates=coordinates
            )
            
        except Exception as e:
            # Return minimal result on error
            return OCRResult(
                extracted_text="",
                confidence_score=0.0,
                language_detected="Unknown",
                word_count=0,
                character_count=0,
                text_regions=[],
                coordinates=[]
            )


class DocumentClassifier:
    """AI-powered document classification"""
    
    def __init__(self):
        self.document_patterns = {
            DocumentType.ENVIRONMENTAL_PERMIT: [
                r'environmental\s+permit', r'environmental\s+clearance',
                r'environmental\s+assessment', r'EPA\s+approval', r'ministry\s+of\s+environment'
            ],
            DocumentType.LAND_OWNERSHIP: [
                r'title\s+deed', r'land\s+ownership', r'property\s+title',
                r'cadastral\s+map', r'survey\s+number', r'land\s+records'
            ],
            DocumentType.PROJECT_PROPOSAL: [
                r'project\s+proposal', r'project\s+document', r'project\s+plan',
                r'technical\s+proposal', r'implementation\s+plan'
            ],
            DocumentType.FINANCIAL_STATEMENT: [
                r'financial\s+statement', r'balance\s+sheet', r'income\s+statement',
                r'audit\s+report', r'financial\s+report', r'budget\s+allocation'
            ],
            DocumentType.SURVEY_REPORT: [
                r'survey\s+report', r'baseline\s+study', r'environmental\s+survey',
                r'biodiversity\s+assessment', r'ecological\s+survey'
            ],
            DocumentType.COMPLIANCE_CERTIFICATE: [
                r'compliance\s+certificate', r'certification\s+body',
                r'ISO\s+\d+', r'verified\s+carbon\s+standard', r'gold\s+standard'
            ]
        }
        
        self.entity_patterns = {
            'dates': r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b\d{2,4}[-/]\d{1,2}[-/]\d{1,2}\b',
            'coordinates': r'\b\d+°\d+\'[\d.]*"[NS]\s+\d+°\d+\'[\d.]*"[EW]\b',
            'amounts': r'\$[\d,]+\.?\d*|\b\d+\s*(?:USD|INR|EUR|crores?|lakhs?)\b',
            'organizations': r'\b(?:Ministry|Department|Authority|Corporation|Ltd|Inc|Pvt)\b[^.]*',
            'permit_numbers': r'\b[A-Z]{2,}\/?[\d-]+\b',
            'area_measurements': r'\b\d+\.?\d*\s*(?:hectares?|acres?|sq\.?\s*(?:km|m|ft))\b'
        }
    
    async def classify_document(self, ocr_result: OCRResult) -> DocumentClassification:
        """Classify document based on extracted text"""
        text = ocr_result.extracted_text.lower()
        
        # Score each document type
        type_scores = {}
        for doc_type, patterns in self.document_patterns.items():
            score = 0
            matched_patterns = []
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    score += len(matches) * (1.0 / len(patterns))
                    matched_patterns.append(pattern)
            
            type_scores[doc_type] = score
        
        # Find best match
        if type_scores:
            best_type = max(type_scores.items(), key=lambda x: x[1])
            predicted_type = best_type[0]
            confidence = min(best_type[1], 1.0)
            
            # Sort alternatives
            alternatives = [(t, s) for t, s in type_scores.items() if t != predicted_type and s > 0]
            alternatives.sort(key=lambda x: x[1], reverse=True)
            alternatives = alternatives[:3]  # Top 3 alternatives
        else:
            predicted_type = DocumentType.PROJECT_PROPOSAL  # Default
            confidence = 0.1
            alternatives = []
        
        # Extract entities
        extracted_entities = {}
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, ocr_result.extracted_text, re.IGNORECASE)
            if matches:
                extracted_entities[entity_type] = list(set(matches))  # Remove duplicates
        
        # Key features based on text analysis
        key_features = self._extract_key_features(ocr_result.extracted_text)
        
        return DocumentClassification(
            predicted_type=predicted_type,
            confidence=confidence,
            alternative_types=alternatives,
            key_features=key_features,
            extracted_entities=extracted_entities
        )
    
    def _extract_key_features(self, text: str) -> List[str]:
        """Extract key features from document text"""
        features = []
        text_lower = text.lower()
        
        # Check for common document features
        if any(word in text_lower for word in ['signature', 'signed', 'authorized']):
            features.append('Contains signatures')
        
        if any(word in text_lower for word in ['seal', 'stamp', 'official']):
            features.append('Official markings')
        
        if re.search(r'\b\d{4}\b', text):  # Year patterns
            features.append('Contains dates')
        
        if re.search(r'\$|\d+\s*(?:USD|INR|EUR)', text):
            features.append('Financial information')
        
        if any(word in text_lower for word in ['gps', 'coordinates', 'latitude', 'longitude']):
            features.append('Geographic data')
        
        if len(text) > 1000:
            features.append('Detailed document')
        elif len(text) < 200:
            features.append('Brief document')
        
        return features


class FraudDetector:
    """Advanced fraud detection system"""
    
    def __init__(self):
        self.suspicious_patterns = [
            r'(?i)(duplicate|copy|reproduction)\s+of',
            r'(?i)this\s+is\s+a\s+copy',
            r'(?i)specimen|sample|template',
            r'(?i)for\s+demonstration\s+only'
        ]
        
        self.known_fraudulent_signatures = set()  # Would be populated from database
        self.document_hashes = {}  # Document fingerprints for duplicate detection
    
    async def analyze_fraud_indicators(
        self, 
        ocr_result: OCRResult, 
        metadata: DocumentMetadata,
        classification: DocumentClassification
    ) -> FraudAnalysis:
        """Comprehensive fraud analysis"""
        fraud_indicators = []
        suspicious_patterns = []
        timestamp_anomalies = []
        content_inconsistencies = []
        
        # Text-based fraud detection
        text = ocr_result.extracted_text.lower()
        
        # Check for suspicious text patterns
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text):
                fraud_indicators.append(FraudIndicator.DOCUMENT_MANIPULATION)
                suspicious_patterns.append(f"Suspicious text pattern: {pattern}")
        
        # Metadata inconsistencies
        if metadata.creation_date and metadata.modification_date:
            time_diff = metadata.modification_date - metadata.creation_date
            if time_diff < timedelta(minutes=1):
                timestamp_anomalies.append({
                    'type': 'rapid_modification',
                    'description': 'Document modified too quickly after creation',
                    'time_diff_seconds': time_diff.total_seconds()
                })
                fraud_indicators.append(FraudIndicator.INCONSISTENT_METADATA)
        
        # Content consistency checks
        await self._check_content_consistency(
            ocr_result, classification, content_inconsistencies, fraud_indicators
        )
        
        # OCR confidence analysis
        if ocr_result.confidence_score < 0.5:
            suspicious_patterns.append("Low OCR confidence suggests poor document quality")
        
        # Calculate fraud probability
        base_probability = len(fraud_indicators) * 0.15
        confidence_penalty = (1.0 - ocr_result.confidence_score) * 0.2
        content_penalty = len(content_inconsistencies) * 0.1
        
        fraud_probability = min(base_probability + confidence_penalty + content_penalty, 0.95)
        
        # Risk score calculation
        risk_score = self._calculate_risk_score(
            fraud_indicators, fraud_probability, classification.confidence
        )
        
        return FraudAnalysis(
            fraud_indicators=fraud_indicators,
            fraud_probability=fraud_probability,
            risk_score=risk_score,
            suspicious_patterns=suspicious_patterns,
            timestamp_anomalies=timestamp_anomalies,
            content_inconsistencies=content_inconsistencies
        )
    
    async def _check_content_consistency(
        self, 
        ocr_result: OCRResult, 
        classification: DocumentClassification,
        inconsistencies: List[str],
        fraud_indicators: List[FraudIndicator]
    ):
        """Check for content inconsistencies"""
        text = ocr_result.extracted_text
        
        # Date consistency checks
        dates = re.findall(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b', text)
        if len(dates) > 1:
            # Check for impossible date combinations
            try:
                parsed_dates = []
                for date_str in dates:
                    # Simple date parsing (would need more robust implementation)
                    parts = re.split(r'[-/]', date_str)
                    if len(parts) == 3:
                        if int(parts[2]) < 1900 or int(parts[2]) > 2030:
                            inconsistencies.append(f"Unrealistic date: {date_str}")
                            fraud_indicators.append(FraudIndicator.ALTERED_TEXT)
            except:
                pass
        
        # Geographic coordinate consistency
        coords = classification.extracted_entities.get('coordinates', [])
        if len(coords) > 1:
            # Check for impossible coordinate combinations
            for coord in coords:
                if not self._validate_coordinates(coord):
                    inconsistencies.append(f"Invalid coordinates: {coord}")
                    fraud_indicators.append(FraudIndicator.MISMATCHED_COORDINATES)
    
    def _validate_coordinates(self, coord_str: str) -> bool:
        """Validate geographic coordinates"""
        try:
            # Basic coordinate validation (simplified)
            coord_match = re.match(r'(\d+)°(\d+)\'[\d.]*"([NS])\s+(\d+)°(\d+)\'[\d.]*"([EW])', coord_str)
            if coord_match:
                lat_deg, lat_min, lat_dir, lon_deg, lon_min, lon_dir = coord_match.groups()
                latitude = int(lat_deg) + int(lat_min) / 60
                longitude = int(lon_deg) + int(lon_min) / 60
                
                if lat_dir == 'S':
                    latitude = -latitude
                if lon_dir == 'W':
                    longitude = -longitude
                
                return -90 <= latitude <= 90 and -180 <= longitude <= 180
            return False
        except:
            return False
    
    def _calculate_risk_score(
        self, 
        fraud_indicators: List[FraudIndicator], 
        fraud_probability: float, 
        classification_confidence: float
    ) -> float:
        """Calculate comprehensive risk score"""
        base_risk = fraud_probability * 100
        
        # Adjust based on fraud indicators
        high_risk_indicators = [
            FraudIndicator.DOCUMENT_MANIPULATION,
            FraudIndicator.FAKE_SIGNATURE,
            FraudIndicator.DUPLICATE_CONTENT
        ]
        
        high_risk_count = sum(1 for indicator in fraud_indicators if indicator in high_risk_indicators)
        risk_adjustment = high_risk_count * 15
        
        # Adjust based on classification confidence
        confidence_adjustment = (1.0 - classification_confidence) * 10
        
        final_risk = min(base_risk + risk_adjustment + confidence_adjustment, 100)
        return final_risk


class DocumentAIVerifier:
    """Main document verification system"""
    
    def __init__(self):
        self.ocr_processor = OCRProcessor()
        self.classifier = DocumentClassifier()
        self.fraud_detector = FraudDetector()
        self.verification_history = {}
    
    async def verify_document(
        self, 
        document_data: bytes, 
        document_id: str,
        expected_type: Optional[DocumentType] = None
    ) -> VerificationResult:
        """Complete document verification pipeline"""
        start_time = datetime.now()
        
        try:
            # Extract metadata (simplified - would use actual file processing)
            metadata = DocumentMetadata(
                file_name=f"document_{document_id}",
                file_size=len(document_data),
                file_type="image/jpeg",  # Would detect actual type
                creation_date=datetime.now() - timedelta(days=1),
                modification_date=datetime.now() - timedelta(hours=2),
                author="Unknown",
                title="Unknown",
                pages=1,
                language="en",
                encoding="utf-8"
            )
            
            # OCR processing
            ocr_result = await self.ocr_processor.extract_text_tesseract(document_data)
            
            # Document classification
            classification = await self.classifier.classify_document(ocr_result)
            
            # Fraud analysis
            fraud_analysis = await self.fraud_detector.analyze_fraud_indicators(
                ocr_result, metadata, classification
            )
            
            # Determine verification status
            status = self._determine_verification_status(
                classification, fraud_analysis, expected_type
            )
            
            # Calculate confidence and authenticity scores
            confidence_score = self._calculate_confidence_score(
                ocr_result, classification, fraud_analysis
            )
            
            authenticity_score = 1.0 - fraud_analysis.fraud_probability
            
            # Generate blockchain hash
            blockchain_hash = self._generate_blockchain_hash(
                document_data, document_id, classification, fraud_analysis
            )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            result = VerificationResult(
                document_id=document_id,
                document_type=classification.predicted_type,
                status=status,
                confidence_score=confidence_score,
                authenticity_score=authenticity_score,
                metadata=metadata,
                ocr_result=ocr_result,
                classification=classification,
                fraud_analysis=fraud_analysis,
                blockchain_hash=blockchain_hash,
                verification_timestamp=datetime.now(),
                processing_time_ms=int(processing_time)
            )
            
            # Store in verification history
            self.verification_history[document_id] = result
            
            return result
            
        except Exception as e:
            # Return error result
            return VerificationResult(
                document_id=document_id,
                document_type=DocumentType.PROJECT_PROPOSAL,
                status=VerificationStatus.REJECTED,
                confidence_score=0.0,
                authenticity_score=0.0,
                metadata=DocumentMetadata(
                    file_name=f"error_document_{document_id}",
                    file_size=0, file_type="unknown", creation_date=None,
                    modification_date=None, author=None, title=None,
                    pages=0, language="unknown", encoding="unknown"
                ),
                ocr_result=OCRResult("", 0.0, "unknown", 0, 0, [], []),
                classification=DocumentClassification(
                    DocumentType.PROJECT_PROPOSAL, 0.0, [], [], {}
                ),
                fraud_analysis=FraudAnalysis([], 1.0, 100.0, [f"Error: {str(e)}"], [], []),
                blockchain_hash="",
                verification_timestamp=datetime.now(),
                processing_time_ms=0
            )
    
    def _determine_verification_status(
        self, 
        classification: DocumentClassification,
        fraud_analysis: FraudAnalysis,
        expected_type: Optional[DocumentType]
    ) -> VerificationStatus:
        """Determine final verification status"""
        
        # Check for fraud indicators
        if fraud_analysis.fraud_probability > 0.7:
            return VerificationStatus.FRAUD_DETECTED
        
        if fraud_analysis.risk_score > 80:
            return VerificationStatus.NEEDS_REVIEW
        
        # Check classification confidence
        if classification.confidence < 0.3:
            return VerificationStatus.NEEDS_REVIEW
        
        # Check type match if expected type provided
        if expected_type and classification.predicted_type != expected_type:
            if classification.confidence < 0.7:
                return VerificationStatus.NEEDS_REVIEW
        
        # Check for high-risk fraud indicators
        high_risk_indicators = [
            FraudIndicator.DOCUMENT_MANIPULATION,
            FraudIndicator.FAKE_SIGNATURE,
            FraudIndicator.DUPLICATE_CONTENT
        ]
        
        if any(indicator in fraud_analysis.fraud_indicators for indicator in high_risk_indicators):
            return VerificationStatus.NEEDS_REVIEW
        
        # All checks passed
        if classification.confidence > 0.8 and fraud_analysis.fraud_probability < 0.2:
            return VerificationStatus.VERIFIED
        else:
            return VerificationStatus.NEEDS_REVIEW
    
    def _calculate_confidence_score(
        self,
        ocr_result: OCRResult,
        classification: DocumentClassification,
        fraud_analysis: FraudAnalysis
    ) -> float:
        """Calculate overall confidence score"""
        
        # Weighted combination of various confidence metrics
        ocr_weight = 0.3
        classification_weight = 0.4
        fraud_weight = 0.3
        
        ocr_confidence = ocr_result.confidence_score
        classification_confidence = classification.confidence
        fraud_confidence = 1.0 - fraud_analysis.fraud_probability
        
        overall_confidence = (
            ocr_confidence * ocr_weight +
            classification_confidence * classification_weight +
            fraud_confidence * fraud_weight
        )
        
        return min(overall_confidence, 0.99)  # Cap at 99%
    
    def _generate_blockchain_hash(
        self,
        document_data: bytes,
        document_id: str,
        classification: DocumentClassification,
        fraud_analysis: FraudAnalysis
    ) -> str:
        """Generate hash for blockchain storage"""
        
        # Create hash input from key verification data
        hash_input = {
            'document_id': document_id,
            'document_type': classification.predicted_type.value,
            'confidence': classification.confidence,
            'fraud_probability': fraud_analysis.fraud_probability,
            'risk_score': fraud_analysis.risk_score,
            'timestamp': datetime.now().isoformat(),
            'data_hash': hashlib.sha256(document_data).hexdigest()
        }
        
        # Create SHA-256 hash
        hash_string = json.dumps(hash_input, sort_keys=True)
        blockchain_hash = hashlib.sha256(hash_string.encode()).hexdigest()
        
        return blockchain_hash
    
    async def get_verification_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get verification statistics summary"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_verifications = [
            result for result in self.verification_history.values()
            if result.verification_timestamp >= cutoff_date
        ]
        
        if not recent_verifications:
            return {
                'total_documents': 0,
                'verified_count': 0,
                'rejected_count': 0,
                'fraud_detected': 0,
                'needs_review': 0,
                'average_confidence': 0.0,
                'average_processing_time': 0.0,
                'document_types': {},
                'fraud_indicators': {}
            }
        
        # Calculate statistics
        status_counts = {}
        for status in VerificationStatus:
            status_counts[status.value] = sum(
                1 for result in recent_verifications if result.status == status
            )
        
        type_counts = {}
        for doc_type in DocumentType:
            type_counts[doc_type.value] = sum(
                1 for result in recent_verifications if result.document_type == doc_type
            )
        
        fraud_indicator_counts = {}
        for result in recent_verifications:
            for indicator in result.fraud_analysis.fraud_indicators:
                fraud_indicator_counts[indicator.value] = fraud_indicator_counts.get(indicator.value, 0) + 1
        
        avg_confidence = sum(r.confidence_score for r in recent_verifications) / len(recent_verifications)
        avg_processing_time = sum(r.processing_time_ms for r in recent_verifications) / len(recent_verifications)
        
        return {
            'total_documents': len(recent_verifications),
            'verified_count': status_counts[VerificationStatus.VERIFIED.value],
            'rejected_count': status_counts[VerificationStatus.REJECTED.value],
            'fraud_detected': status_counts[VerificationStatus.FRAUD_DETECTED.value],
            'needs_review': status_counts[VerificationStatus.NEEDS_REVIEW.value],
            'average_confidence': round(avg_confidence, 3),
            'average_processing_time': round(avg_processing_time, 2),
            'document_types': type_counts,
            'fraud_indicators': fraud_indicator_counts
        }


# Demo usage
async def demo_document_verification():
    """Demonstrate the document verification system"""
    
    print("=== BlueCarbon MRV Document AI Verification System ===")
    print("🔍 Advanced OCR, AI Classification, and Fraud Detection")
    print()
    
    verifier = DocumentAIVerifier()
    
    # Simulate document verification scenarios
    scenarios = [
        {
            'id': 'ENV_PERMIT_001',
            'type': DocumentType.ENVIRONMENTAL_PERMIT,
            'description': 'Environmental Permit - Clean Document'
        },
        {
            'id': 'LAND_TITLE_002',
            'type': DocumentType.LAND_OWNERSHIP,
            'description': 'Land Title - Suspicious Metadata'
        },
        {
            'id': 'FINANCIAL_003',
            'type': DocumentType.FINANCIAL_STATEMENT,
            'description': 'Financial Statement - OCR Issues'
        }
    ]
    
    print("📄 Processing Sample Documents:")
    print("=" * 50)
    
    for scenario in scenarios:
        print(f"\n🔄 Processing: {scenario['description']}")
        
        # Simulate document data (would be actual file bytes)
        sample_text = f"Sample {scenario['type'].value} document with official content"
        document_data = sample_text.encode()
        
        # Verify document
        result = await verifier.verify_document(
            document_data=document_data,
            document_id=scenario['id'],
            expected_type=scenario['type']
        )
        
        print(f"   Document ID: {result.document_id}")
        print(f"   Status: {result.status.value.upper()}")
        print(f"   Confidence: {result.confidence_score:.1%}")
        print(f"   Authenticity: {result.authenticity_score:.1%}")
        print(f"   Type: {result.document_type.value}")
        print(f"   Fraud Risk: {result.fraud_analysis.risk_score:.1f}%")
        print(f"   Processing Time: {result.processing_time_ms}ms")
        
        if result.fraud_analysis.fraud_indicators:
            print(f"   ⚠️  Fraud Indicators: {[i.value for i in result.fraud_analysis.fraud_indicators]}")
        
        if result.fraud_analysis.suspicious_patterns:
            print(f"   🚩 Suspicious Patterns: {len(result.fraud_analysis.suspicious_patterns)} detected")
        
        print(f"   🔗 Blockchain Hash: {result.blockchain_hash[:16]}...")
    
    # Generate summary statistics
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY (Last 7 Days)")
    print("=" * 50)
    
    summary = await verifier.get_verification_summary(days=7)
    
    print(f"Total Documents Processed: {summary['total_documents']}")
    print(f"Verified: {summary['verified_count']}")
    print(f"Needs Review: {summary['needs_review']}")
    print(f"Fraud Detected: {summary['fraud_detected']}")
    print(f"Rejected: {summary['rejected_count']}")
    print(f"Average Confidence: {summary['average_confidence']:.1%}")
    print(f"Average Processing Time: {summary['average_processing_time']:.1f}ms")
    
    if summary['fraud_indicators']:
        print(f"\n🚨 Most Common Fraud Indicators:")
        for indicator, count in sorted(summary['fraud_indicators'].items(), key=lambda x: x[1], reverse=True):
            print(f"   - {indicator.replace('_', ' ').title()}: {count} cases")
    
    print("\n✅ Document AI Verification System Demo Complete!")


if __name__ == "__main__":
    import io
    asyncio.run(demo_document_verification())