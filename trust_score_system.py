"""
Trust Score System for BlueCarbon MRV Platform
AI-powered reputation and trust scoring for NGOs, Industries, and all platform entities
"""

import datetime
import json
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class EntityType(Enum):
    NGO = "ngo"
    INDUSTRY = "industry"
    AUDITOR = "auditor"
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"

class TrustEvent(Enum):
    # Positive events
    PROJECT_APPROVED = "project_approved"
    AUDIT_PASSED = "audit_passed"
    DOCUMENT_VERIFIED = "document_verified"
    COMPLIANCE_MET = "compliance_met"
    MILESTONE_ACHIEVED = "milestone_achieved"
    POSITIVE_FEEDBACK = "positive_feedback"
    TRANSPARENT_REPORTING = "transparent_reporting"
    
    # Negative events
    PROJECT_REJECTED = "project_rejected"
    AUDIT_FAILED = "audit_failed"
    DOCUMENT_FRAUD = "document_fraud"
    COMPLIANCE_VIOLATION = "compliance_violation"
    MILESTONE_MISSED = "milestone_missed"
    NEGATIVE_FEEDBACK = "negative_feedback"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    
    # Neutral events
    DOCUMENT_UPLOADED = "document_uploaded"
    PROFILE_UPDATED = "profile_updated"
    LOGIN_ACTIVITY = "login_activity"

@dataclass
class TrustScoreEvent:
    entity_id: str
    entity_type: EntityType
    event_type: TrustEvent
    impact_score: float
    description: str
    timestamp: datetime.datetime
    metadata: Dict
    verified: bool = True

@dataclass
class TrustScoreProfile:
    entity_id: str
    entity_type: EntityType
    current_score: float
    score_history: List[Tuple[datetime.datetime, float]]
    total_events: int
    positive_events: int
    negative_events: int
    risk_level: str
    verification_status: str
    compliance_rate: float
    last_updated: datetime.datetime
    score_trend: str  # "improving", "declining", "stable"
    
class TrustScoreCalculator:
    """Advanced trust score calculation engine with AI-powered reputation analysis"""
    
    # Base scoring weights for different event types
    EVENT_WEIGHTS = {
        TrustEvent.PROJECT_APPROVED: 15.0,
        TrustEvent.AUDIT_PASSED: 20.0,
        TrustEvent.DOCUMENT_VERIFIED: 8.0,
        TrustEvent.COMPLIANCE_MET: 12.0,
        TrustEvent.MILESTONE_ACHIEVED: 10.0,
        TrustEvent.POSITIVE_FEEDBACK: 5.0,
        TrustEvent.TRANSPARENT_REPORTING: 7.0,
        
        TrustEvent.PROJECT_REJECTED: -25.0,
        TrustEvent.AUDIT_FAILED: -30.0,
        TrustEvent.DOCUMENT_FRAUD: -50.0,
        TrustEvent.COMPLIANCE_VIOLATION: -35.0,
        TrustEvent.MILESTONE_MISSED: -15.0,
        TrustEvent.NEGATIVE_FEEDBACK: -8.0,
        TrustEvent.SUSPICIOUS_ACTIVITY: -20.0,
        
        TrustEvent.DOCUMENT_UPLOADED: 1.0,
        TrustEvent.PROFILE_UPDATED: 0.5,
        TrustEvent.LOGIN_ACTIVITY: 0.1,
    }
    
    # Entity type multipliers
    ENTITY_MULTIPLIERS = {
        EntityType.NGO: 1.0,
        EntityType.INDUSTRY: 1.2,  # Higher accountability expected
        EntityType.AUDITOR: 1.5,  # Critical role in verification
        EntityType.BUYER: 0.8,
        EntityType.SELLER: 0.9,
        EntityType.ADMIN: 2.0,  # Highest standards
    }
    
    def __init__(self):
        self.min_score = 0.0
        self.max_score = 100.0
        self.initial_score = 50.0
        
    def calculate_base_score(self, events: List[TrustScoreEvent]) -> float:
        """Calculate base trust score from historical events"""
        if not events:
            return self.initial_score
            
        total_impact = 0.0
        for event in events:
            # Apply time decay - recent events have more weight
            days_ago = (datetime.datetime.now() - event.timestamp).days
            time_weight = math.exp(-days_ago / 180)  # 6-month half-life
            
            # Apply entity type multiplier
            entity_multiplier = self.ENTITY_MULTIPLIERS.get(event.entity_type, 1.0)
            
            # Calculate event impact
            base_weight = self.EVENT_WEIGHTS.get(event.event_type, 0.0)
            event_impact = base_weight * time_weight * entity_multiplier * event.impact_score
            
            total_impact += event_impact
        
        # Apply sigmoid normalization to keep score in reasonable range
        normalized_score = self.initial_score + (total_impact / (1 + abs(total_impact) / 50))
        
        return max(self.min_score, min(self.max_score, normalized_score))
    
    def calculate_compliance_bonus(self, compliance_rate: float) -> float:
        """Calculate bonus/penalty based on compliance rate"""
        if compliance_rate >= 0.95:
            return 10.0  # Excellent compliance
        elif compliance_rate >= 0.85:
            return 5.0   # Good compliance
        elif compliance_rate >= 0.70:
            return 0.0   # Acceptable compliance
        elif compliance_rate >= 0.50:
            return -5.0  # Poor compliance
        else:
            return -15.0 # Critical compliance issues
    
    def calculate_activity_factor(self, events: List[TrustScoreEvent]) -> float:
        """Calculate activity-based score adjustment"""
        if not events:
            return -5.0  # Penalty for inactivity
            
        # Recent activity (last 30 days)
        recent_events = [e for e in events if (datetime.datetime.now() - e.timestamp).days <= 30]
        
        if len(recent_events) >= 10:
            return 5.0   # Very active
        elif len(recent_events) >= 5:
            return 2.0   # Active
        elif len(recent_events) >= 1:
            return 0.0   # Some activity
        else:
            return -3.0  # Inactive
    
    def calculate_verification_bonus(self, verification_status: str) -> float:
        """Calculate bonus based on verification status"""
        verification_bonuses = {
            'verified': 10.0,
            'partially_verified': 5.0,
            'pending': 0.0,
            'unverified': -10.0,
            'rejected': -20.0
        }
        return verification_bonuses.get(verification_status, 0.0)
    
    def determine_risk_level(self, score: float) -> str:
        """Determine risk level based on trust score"""
        if score >= 85:
            return "very_low"
        elif score >= 70:
            return "low"
        elif score >= 50:
            return "medium"
        elif score >= 30:
            return "high"
        else:
            return "very_high"
    
    def determine_score_trend(self, score_history: List[Tuple[datetime.datetime, float]]) -> str:
        """Analyze score trend over time"""
        if len(score_history) < 2:
            return "stable"
            
        # Get recent scores (last 30 days)
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=30)
        recent_scores = [(date, score) for date, score in score_history if date >= cutoff_date]
        
        if len(recent_scores) < 2:
            return "stable"
            
        # Calculate trend
        first_score = recent_scores[0][1]
        last_score = recent_scores[-1][1]
        change = last_score - first_score
        
        if change > 5:
            return "improving"
        elif change < -5:
            return "declining"
        else:
            return "stable"
    
    def calculate_trust_score(self, entity_id: str, entity_type: EntityType, 
                            events: List[TrustScoreEvent], 
                            compliance_rate: float = 1.0,
                            verification_status: str = "unverified") -> TrustScoreProfile:
        """Calculate comprehensive trust score for an entity"""
        
        # Calculate base score from events
        base_score = self.calculate_base_score(events)
        
        # Apply various adjustments
        compliance_bonus = self.calculate_compliance_bonus(compliance_rate)
        activity_factor = self.calculate_activity_factor(events)
        verification_bonus = self.calculate_verification_bonus(verification_status)
        
        # Final score calculation
        final_score = base_score + compliance_bonus + activity_factor + verification_bonus
        final_score = max(self.min_score, min(self.max_score, final_score))
        
        # Calculate statistics
        positive_events = len([e for e in events if self.EVENT_WEIGHTS.get(e.event_type, 0) > 0])
        negative_events = len([e for e in events if self.EVENT_WEIGHTS.get(e.event_type, 0) < 0])
        
        # Build score history
        score_history = [(datetime.datetime.now(), final_score)]
        if events:
            # Simulate historical scores (in real implementation, this would be stored)
            for i in range(min(10, len(events))):
                historical_date = events[-(i+1)].timestamp
                historical_score = final_score - (i * 2)  # Simplified simulation
                score_history.append((historical_date, max(0, historical_score)))
        
        # Determine trend
        trend = self.determine_score_trend(score_history)
        
        return TrustScoreProfile(
            entity_id=entity_id,
            entity_type=entity_type,
            current_score=round(final_score, 1),
            score_history=score_history,
            total_events=len(events),
            positive_events=positive_events,
            negative_events=negative_events,
            risk_level=self.determine_risk_level(final_score),
            verification_status=verification_status,
            compliance_rate=compliance_rate,
            last_updated=datetime.datetime.now(),
            score_trend=trend
        )

class TrustScoreManager:
    """Trust score management system"""
    
    def __init__(self):
        self.calculator = TrustScoreCalculator()
        self.events_db = {}  # In production, this would be a proper database
        self.profiles_db = {}
    
    def add_trust_event(self, event: TrustScoreEvent):
        """Add a new trust score event"""
        if event.entity_id not in self.events_db:
            self.events_db[event.entity_id] = []
        
        self.events_db[event.entity_id].append(event)
        
        # Recalculate trust score
        self.update_trust_score(event.entity_id, event.entity_type)
    
    def update_trust_score(self, entity_id: str, entity_type: EntityType, 
                          compliance_rate: float = 1.0, verification_status: str = "unverified"):
        """Update trust score for an entity"""
        events = self.events_db.get(entity_id, [])
        
        profile = self.calculator.calculate_trust_score(
            entity_id, entity_type, events, compliance_rate, verification_status
        )
        
        self.profiles_db[entity_id] = profile
        return profile
    
    def get_trust_profile(self, entity_id: str) -> Optional[TrustScoreProfile]:
        """Get trust profile for an entity"""
        return self.profiles_db.get(entity_id)
    
    def get_risk_entities(self, risk_level: str = "high") -> List[TrustScoreProfile]:
        """Get all entities with specified risk level or higher"""
        risk_levels = ["very_high", "high", "medium", "low", "very_low"]
        risk_threshold = risk_levels.index(risk_level)
        
        risky_entities = []
        for profile in self.profiles_db.values():
            if risk_levels.index(profile.risk_level) <= risk_threshold:
                risky_entities.append(profile)
        
        return sorted(risky_entities, key=lambda x: x.current_score)
    
    def get_top_trusted_entities(self, entity_type: EntityType = None, limit: int = 10) -> List[TrustScoreProfile]:
        """Get top trusted entities"""
        profiles = list(self.profiles_db.values())
        
        if entity_type:
            profiles = [p for p in profiles if p.entity_type == entity_type]
        
        return sorted(profiles, key=lambda x: x.current_score, reverse=True)[:limit]
    
    def generate_trust_report(self, entity_id: str) -> Dict:
        """Generate comprehensive trust report"""
        profile = self.get_trust_profile(entity_id)
        if not profile:
            return {"error": "Entity not found"}
        
        events = self.events_db.get(entity_id, [])
        
        # Analyze event patterns
        event_analysis = {}
        for event in events:
            event_type = event.event_type.value
            if event_type not in event_analysis:
                event_analysis[event_type] = {"count": 0, "total_impact": 0.0}
            
            event_analysis[event_type]["count"] += 1
            event_analysis[event_type]["total_impact"] += event.impact_score
        
        # Risk indicators
        risk_indicators = []
        if profile.current_score < 30:
            risk_indicators.append("Very low trust score")
        if profile.negative_events > profile.positive_events:
            risk_indicators.append("More negative than positive events")
        if profile.score_trend == "declining":
            risk_indicators.append("Declining trust score trend")
        if profile.compliance_rate < 0.7:
            risk_indicators.append("Poor compliance rate")
        
        return {
            "profile": asdict(profile),
            "event_analysis": event_analysis,
            "risk_indicators": risk_indicators,
            "recommendations": self._generate_recommendations(profile, events),
            "generated_at": datetime.datetime.now().isoformat()
        }
    
    def _generate_recommendations(self, profile: TrustScoreProfile, events: List[TrustScoreEvent]) -> List[str]:
        """Generate AI-powered recommendations for improving trust score"""
        recommendations = []
        
        if profile.current_score < 50:
            recommendations.append("Focus on completing projects successfully and meeting compliance requirements")
        
        if profile.negative_events > 5:
            recommendations.append("Address recent issues and implement quality control measures")
        
        if profile.verification_status == "unverified":
            recommendations.append("Complete account verification process to boost trust score")
        
        if profile.compliance_rate < 0.8:
            recommendations.append("Improve compliance with platform requirements and deadlines")
        
        if len(events) < 10:
            recommendations.append("Increase platform activity and engagement to build trust history")
        
        if profile.score_trend == "declining":
            recommendations.append("Review recent activities and address any performance issues")
        
        return recommendations

# Usage example and testing
def simulate_trust_score_system():
    """Simulate the trust score system with sample data"""
    manager = TrustScoreManager()
    
    # Simulate events for an NGO
    ngo_events = [
        TrustScoreEvent("ngo_001", EntityType.NGO, TrustEvent.PROJECT_APPROVED, 1.0, 
                       "Coastal restoration project approved", datetime.datetime.now() - datetime.timedelta(days=30), {}),
        TrustScoreEvent("ngo_001", EntityType.NGO, TrustEvent.DOCUMENT_VERIFIED, 1.0, 
                       "Environmental clearance verified", datetime.datetime.now() - datetime.timedelta(days=25), {}),
        TrustScoreEvent("ngo_001", EntityType.NGO, TrustEvent.MILESTONE_ACHIEVED, 1.0, 
                       "50% project completion milestone", datetime.datetime.now() - datetime.timedelta(days=15), {}),
        TrustScoreEvent("ngo_001", EntityType.NGO, TrustEvent.AUDIT_PASSED, 1.0, 
                       "Third-party audit successful", datetime.datetime.now() - datetime.timedelta(days=5), {}),
    ]
    
    # Add events
    for event in ngo_events:
        manager.add_trust_event(event)
    
    # Update with additional information
    profile = manager.update_trust_score("ngo_001", EntityType.NGO, 
                                       compliance_rate=0.95, verification_status="verified")
    
    print("Trust Score Profile:")
    print(f"Entity: {profile.entity_id}")
    print(f"Current Score: {profile.current_score}")
    print(f"Risk Level: {profile.risk_level}")
    print(f"Score Trend: {profile.score_trend}")
    print(f"Compliance Rate: {profile.compliance_rate}")
    
    # Generate report
    report = manager.generate_trust_report("ngo_001")
    print("\nTrust Report Generated:")
    print(f"Recommendations: {report['recommendations']}")
    
    return manager

if __name__ == "__main__":
    simulate_trust_score_system()