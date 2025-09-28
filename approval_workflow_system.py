"""
Multi-layer Approval Workflow System for BlueCarbon MRV Platform
AI auto-verification followed by manual admin/auditor approvals with blockchain logging
"""

import datetime
import json
import hashlib
import uuid
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from collections import defaultdict

class ApprovalStage(Enum):
    SUBMISSION = "submission"
    AI_VERIFICATION = "ai_verification"
    TECHNICAL_REVIEW = "technical_review"
    ADMIN_APPROVAL = "admin_approval"
    AUDITOR_VERIFICATION = "auditor_verification"
    FINAL_APPROVAL = "final_approval"
    BLOCKCHAIN_LOGGING = "blockchain_logging"
    COMPLETED = "completed"

class ApprovalStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVISION = "requires_revision"
    ESCALATED = "escalated"
    COMPLETED = "completed"

class ApprovalDecision(Enum):
    AUTO_APPROVE = "auto_approve"
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_REVISION = "request_revision"
    ESCALATE = "escalate"
    DEFER = "defer"

class ApprovalRole(Enum):
    AI_SYSTEM = "ai_system"
    TECHNICAL_REVIEWER = "technical_reviewer"
    ADMIN = "admin"
    SENIOR_ADMIN = "senior_admin"
    AUDITOR = "auditor"
    BLOCKCHAIN_LOGGER = "blockchain_logger"

@dataclass
class ApprovalAction:
    action_id: str
    stage: ApprovalStage
    approver_id: str
    approver_role: ApprovalRole
    decision: ApprovalDecision
    confidence_score: Optional[float]
    comments: str
    timestamp: datetime.datetime
    supporting_data: Dict[str, Any]
    blockchain_hash: Optional[str] = None

@dataclass
class ApprovalWorkflow:
    workflow_id: str
    project_id: str
    project_type: str
    current_stage: ApprovalStage
    overall_status: ApprovalStatus
    submission_data: Dict[str, Any]
    actions_history: List[ApprovalAction]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    estimated_completion: Optional[datetime.datetime]
    priority_level: int  # 1-5, 5 being highest
    sla_deadline: datetime.datetime
    
class AIVerificationEngine:
    """AI-powered auto-verification system"""
    
    def __init__(self):
        self.confidence_threshold = 85.0
        self.auto_approve_threshold = 95.0
        self.auto_reject_threshold = 30.0
        
        # Verification weights for different criteria
        self.verification_criteria = {
            'document_authenticity': 25.0,
            'location_verification': 20.0,
            'environmental_impact': 20.0,
            'compliance_check': 15.0,
            'financial_validation': 10.0,
            'organizational_credibility': 10.0
        }
    
    async def verify_project_submission(self, project_data: Dict[str, Any]) -> Tuple[ApprovalDecision, float, Dict[str, Any]]:
        """Perform comprehensive AI verification of project submission"""
        
        verification_results = {}
        total_score = 0.0
        
        try:
            # Document authenticity check
            doc_score = await self._verify_documents(project_data.get('documents', []))
            verification_results['document_authenticity'] = {
                'score': doc_score,
                'passed': doc_score > 70,
                'details': 'AI document verification completed'
            }
            total_score += doc_score * (self.verification_criteria['document_authenticity'] / 100)
            
            # Location verification
            location_score = await self._verify_location(project_data.get('coordinates', {}))
            verification_results['location_verification'] = {
                'score': location_score,
                'passed': location_score > 70,
                'details': 'Satellite imagery cross-referenced'
            }
            total_score += location_score * (self.verification_criteria['location_verification'] / 100)
            
            # Environmental impact assessment
            env_score = await self._assess_environmental_impact(project_data)
            verification_results['environmental_impact'] = {
                'score': env_score,
                'passed': env_score > 60,
                'details': 'Environmental impact calculated'
            }
            total_score += env_score * (self.verification_criteria['environmental_impact'] / 100)
            
            # Compliance check
            compliance_score = await self._check_compliance(project_data)
            verification_results['compliance_check'] = {
                'score': compliance_score,
                'passed': compliance_score > 75,
                'details': 'Regulatory compliance verified'
            }
            total_score += compliance_score * (self.verification_criteria['compliance_check'] / 100)
            
            # Financial validation
            financial_score = await self._validate_financials(project_data)
            verification_results['financial_validation'] = {
                'score': financial_score,
                'passed': financial_score > 70,
                'details': 'Financial projections analyzed'
            }
            total_score += financial_score * (self.verification_criteria['financial_validation'] / 100)
            
            # Organizational credibility
            org_score = await self._check_organization_credibility(project_data)
            verification_results['organizational_credibility'] = {
                'score': org_score,
                'passed': org_score > 65,
                'details': 'Organization trust score evaluated'
            }
            total_score += org_score * (self.verification_criteria['organizational_credibility'] / 100)
            
            # Determine decision based on total score
            if total_score >= self.auto_approve_threshold:
                decision = ApprovalDecision.AUTO_APPROVE
            elif total_score <= self.auto_reject_threshold:
                decision = ApprovalDecision.REJECT
            elif total_score >= self.confidence_threshold:
                decision = ApprovalDecision.APPROVE
            else:
                decision = ApprovalDecision.REQUEST_REVISION
            
            supporting_data = {
                'verification_results': verification_results,
                'total_score': total_score,
                'ai_model_version': '2.1.0',
                'processing_time_ms': 2300
            }
            
            return decision, total_score, supporting_data
            
        except Exception as e:
            # AI verification failed, escalate to human review
            return ApprovalDecision.ESCALATE, 0.0, {'error': str(e), 'requires_manual_review': True}
    
    async def _verify_documents(self, documents: List[Dict]) -> float:
        """Simulate document verification"""
        if not documents:
            return 50.0
        
        # Simulate AI document analysis
        authenticity_scores = []
        for doc in documents:
            # Mock document verification score
            base_score = 85.0
            if doc.get('type') == 'environmental_clearance':
                base_score += 10.0
            if doc.get('digital_signature'):
                base_score += 5.0
            authenticity_scores.append(min(100.0, base_score))
        
        return sum(authenticity_scores) / len(authenticity_scores)
    
    async def _verify_location(self, coordinates: Dict) -> float:
        """Simulate location verification"""
        if not coordinates:
            return 40.0
        
        # Mock satellite verification
        lat = coordinates.get('latitude', 0)
        lon = coordinates.get('longitude', 0)
        
        if lat == 0 and lon == 0:
            return 10.0  # Invalid coordinates
        
        # Simulate location authenticity score
        return 88.5  # Mock high confidence
    
    async def _assess_environmental_impact(self, project_data: Dict) -> float:
        """Simulate environmental impact assessment"""
        project_type = project_data.get('project_type', '')
        area = project_data.get('area', 0)
        
        base_score = 75.0
        if 'restoration' in project_type.lower():
            base_score += 15.0
        if 'conservation' in project_type.lower():
            base_score += 10.0
        if area > 50:  # Large projects get higher score
            base_score += 5.0
        
        return min(100.0, base_score)
    
    async def _check_compliance(self, project_data: Dict) -> float:
        """Simulate compliance checking"""
        required_docs = ['environmental_clearance', 'land_ownership', 'noc_pollution']
        submitted_docs = [doc.get('type') for doc in project_data.get('documents', [])]
        
        compliance_ratio = len(set(required_docs) & set(submitted_docs)) / len(required_docs)
        return compliance_ratio * 100
    
    async def _validate_financials(self, project_data: Dict) -> float:
        """Simulate financial validation"""
        budget = project_data.get('budget', 0)
        duration = project_data.get('duration_months', 12)
        
        if budget <= 0:
            return 20.0
        
        monthly_budget = budget / duration
        if monthly_budget < 10000:
            return 60.0
        elif monthly_budget < 50000:
            return 80.0
        else:
            return 90.0
    
    async def _check_organization_credibility(self, project_data: Dict) -> float:
        """Simulate organization credibility check"""
        org_id = project_data.get('organization_id', '')
        # This would integrate with the trust score system
        # For simulation, return a reasonable score
        return 82.0

class ApprovalWorkflowEngine:
    """Main workflow orchestration engine"""
    
    def __init__(self):
        self.ai_engine = AIVerificationEngine()
        self.workflows: Dict[str, ApprovalWorkflow] = {}
        self.stage_handlers = {
            ApprovalStage.AI_VERIFICATION: self._handle_ai_verification,
            ApprovalStage.TECHNICAL_REVIEW: self._handle_technical_review,
            ApprovalStage.ADMIN_APPROVAL: self._handle_admin_approval,
            ApprovalStage.AUDITOR_VERIFICATION: self._handle_auditor_verification,
            ApprovalStage.BLOCKCHAIN_LOGGING: self._handle_blockchain_logging
        }
        
        # SLA timelines (in hours)
        self.stage_sla = {
            ApprovalStage.AI_VERIFICATION: 1,
            ApprovalStage.TECHNICAL_REVIEW: 24,
            ApprovalStage.ADMIN_APPROVAL: 48,
            ApprovalStage.AUDITOR_VERIFICATION: 72,
            ApprovalStage.BLOCKCHAIN_LOGGING: 2,
        }
    
    def create_workflow(self, project_id: str, project_data: Dict[str, Any], priority: int = 3) -> str:
        """Create a new approval workflow"""
        workflow_id = str(uuid.uuid4())
        
        # Calculate SLA deadline based on priority
        total_sla_hours = sum(self.stage_sla.values())
        priority_multiplier = {1: 2.0, 2: 1.5, 3: 1.0, 4: 0.75, 5: 0.5}
        adjusted_hours = total_sla_hours * priority_multiplier.get(priority, 1.0)
        
        workflow = ApprovalWorkflow(
            workflow_id=workflow_id,
            project_id=project_id,
            project_type=project_data.get('project_type', 'unknown'),
            current_stage=ApprovalStage.SUBMISSION,
            overall_status=ApprovalStatus.PENDING,
            submission_data=project_data,
            actions_history=[],
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            estimated_completion=datetime.datetime.now() + datetime.timedelta(hours=adjusted_hours),
            priority_level=priority,
            sla_deadline=datetime.datetime.now() + datetime.timedelta(hours=adjusted_hours)
        )
        
        self.workflows[workflow_id] = workflow
        
        # Start AI verification immediately
        self._advance_workflow(workflow_id, ApprovalStage.AI_VERIFICATION)
        
        return workflow_id
    
    async def process_workflow_step(self, workflow_id: str) -> bool:
        """Process the current step of a workflow"""
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        
        if workflow.current_stage in self.stage_handlers:
            return await self.stage_handlers[workflow.current_stage](workflow)
        
        return False
    
    async def _handle_ai_verification(self, workflow: ApprovalWorkflow) -> bool:
        """Handle AI verification stage"""
        try:
            workflow.overall_status = ApprovalStatus.IN_PROGRESS
            
            # Perform AI verification
            decision, confidence, supporting_data = await self.ai_engine.verify_project_submission(
                workflow.submission_data
            )
            
            # Create approval action
            action = ApprovalAction(
                action_id=str(uuid.uuid4()),
                stage=ApprovalStage.AI_VERIFICATION,
                approver_id="ai_system",
                approver_role=ApprovalRole.AI_SYSTEM,
                decision=decision,
                confidence_score=confidence,
                comments=f"AI verification completed with {confidence:.1f}% confidence",
                timestamp=datetime.datetime.now(),
                supporting_data=supporting_data
            )
            
            workflow.actions_history.append(action)
            workflow.updated_at = datetime.datetime.now()
            
            # Determine next stage based on AI decision
            if decision == ApprovalDecision.AUTO_APPROVE and confidence >= 95.0:
                # Skip human review for high-confidence auto-approvals
                self._advance_workflow(workflow.workflow_id, ApprovalStage.BLOCKCHAIN_LOGGING)
                workflow.overall_status = ApprovalStatus.APPROVED
            elif decision == ApprovalDecision.REJECT:
                workflow.overall_status = ApprovalStatus.REJECTED
                workflow.current_stage = ApprovalStage.COMPLETED
            elif decision == ApprovalDecision.ESCALATE:
                self._advance_workflow(workflow.workflow_id, ApprovalStage.ADMIN_APPROVAL)
            else:
                self._advance_workflow(workflow.workflow_id, ApprovalStage.TECHNICAL_REVIEW)
            
            return True
            
        except Exception as e:
            # AI verification failed, escalate to human review
            self._escalate_workflow(workflow.workflow_id, f"AI verification failed: {str(e)}")
            return False
    
    async def _handle_technical_review(self, workflow: ApprovalWorkflow) -> bool:
        """Handle technical review stage (requires human input)"""
        # This stage waits for human technical reviewer input
        # In a real system, this would be handled by the frontend
        workflow.overall_status = ApprovalStatus.PENDING
        return True
    
    async def _handle_admin_approval(self, workflow: ApprovalWorkflow) -> bool:
        """Handle admin approval stage (requires human input)"""
        # This stage waits for admin input
        workflow.overall_status = ApprovalStatus.PENDING
        return True
    
    async def _handle_auditor_verification(self, workflow: ApprovalWorkflow) -> bool:
        """Handle auditor verification stage (requires human input)"""
        # This stage waits for auditor input
        workflow.overall_status = ApprovalStatus.PENDING
        return True
    
    async def _handle_blockchain_logging(self, workflow: ApprovalWorkflow) -> bool:
        """Handle blockchain logging stage"""
        try:
            # Create blockchain entry
            blockchain_data = {
                'workflow_id': workflow.workflow_id,
                'project_id': workflow.project_id,
                'approval_hash': self._generate_approval_hash(workflow),
                'timestamp': datetime.datetime.now().isoformat(),
                'final_decision': 'approved',
                'approvers': [action.approver_id for action in workflow.actions_history]
            }
            
            # Simulate blockchain logging
            blockchain_hash = hashlib.sha256(
                json.dumps(blockchain_data, sort_keys=True).encode()
            ).hexdigest()
            
            action = ApprovalAction(
                action_id=str(uuid.uuid4()),
                stage=ApprovalStage.BLOCKCHAIN_LOGGING,
                approver_id="blockchain_system",
                approver_role=ApprovalRole.BLOCKCHAIN_LOGGER,
                decision=ApprovalDecision.APPROVE,
                confidence_score=100.0,
                comments="Approval logged to blockchain for immutable audit trail",
                timestamp=datetime.datetime.now(),
                supporting_data=blockchain_data,
                blockchain_hash=blockchain_hash
            )
            
            workflow.actions_history.append(action)
            workflow.current_stage = ApprovalStage.COMPLETED
            workflow.overall_status = ApprovalStatus.COMPLETED
            workflow.updated_at = datetime.datetime.now()
            
            return True
            
        except Exception as e:
            self._escalate_workflow(workflow.workflow_id, f"Blockchain logging failed: {str(e)}")
            return False
    
    def manual_approval(self, workflow_id: str, approver_id: str, approver_role: ApprovalRole, 
                       decision: ApprovalDecision, comments: str, 
                       supporting_data: Optional[Dict] = None) -> bool:
        """Process manual approval/rejection by human reviewers"""
        
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        
        # Create approval action
        action = ApprovalAction(
            action_id=str(uuid.uuid4()),
            stage=workflow.current_stage,
            approver_id=approver_id,
            approver_role=approver_role,
            decision=decision,
            confidence_score=None,
            comments=comments,
            timestamp=datetime.datetime.now(),
            supporting_data=supporting_data or {}
        )
        
        workflow.actions_history.append(action)
        workflow.updated_at = datetime.datetime.now()
        
        # Advance workflow based on decision
        if decision == ApprovalDecision.APPROVE:
            next_stage = self._get_next_stage(workflow.current_stage)
            if next_stage:
                self._advance_workflow(workflow_id, next_stage)
            else:
                workflow.overall_status = ApprovalStatus.COMPLETED
        elif decision == ApprovalDecision.REJECT:
            workflow.overall_status = ApprovalStatus.REJECTED
            workflow.current_stage = ApprovalStage.COMPLETED
        elif decision == ApprovalDecision.REQUEST_REVISION:
            workflow.overall_status = ApprovalStatus.REQUIRES_REVISION
        elif decision == ApprovalDecision.ESCALATE:
            self._escalate_workflow(workflow_id, comments)
        
        return True
    
    def _advance_workflow(self, workflow_id: str, next_stage: ApprovalStage):
        """Advance workflow to next stage"""
        if workflow_id in self.workflows:
            self.workflows[workflow_id].current_stage = next_stage
            self.workflows[workflow_id].updated_at = datetime.datetime.now()
    
    def _escalate_workflow(self, workflow_id: str, reason: str):
        """Escalate workflow for senior review"""
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            workflow.overall_status = ApprovalStatus.ESCALATED
            workflow.current_stage = ApprovalStage.ADMIN_APPROVAL
            workflow.priority_level = min(5, workflow.priority_level + 1)
    
    def _get_next_stage(self, current_stage: ApprovalStage) -> Optional[ApprovalStage]:
        """Get the next stage in the approval workflow"""
        stage_order = [
            ApprovalStage.SUBMISSION,
            ApprovalStage.AI_VERIFICATION,
            ApprovalStage.TECHNICAL_REVIEW,
            ApprovalStage.ADMIN_APPROVAL,
            ApprovalStage.AUDITOR_VERIFICATION,
            ApprovalStage.BLOCKCHAIN_LOGGING,
            ApprovalStage.COMPLETED
        ]
        
        try:
            current_index = stage_order.index(current_stage)
            if current_index < len(stage_order) - 1:
                return stage_order[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    def _generate_approval_hash(self, workflow: ApprovalWorkflow) -> str:
        """Generate hash for blockchain logging"""
        hash_data = {
            'workflow_id': workflow.workflow_id,
            'project_id': workflow.project_id,
            'actions': [
                {
                    'stage': action.stage.value,
                    'approver': action.approver_id,
                    'decision': action.decision.value,
                    'timestamp': action.timestamp.isoformat()
                }
                for action in workflow.actions_history
            ]
        }
        
        return hashlib.sha256(
            json.dumps(hash_data, sort_keys=True).encode()
        ).hexdigest()
    
    def get_workflow(self, workflow_id: str) -> Optional[ApprovalWorkflow]:
        """Get workflow by ID"""
        return self.workflows.get(workflow_id)
    
    def get_pending_workflows(self, stage: Optional[ApprovalStage] = None) -> List[ApprovalWorkflow]:
        """Get all pending workflows, optionally filtered by stage"""
        workflows = [w for w in self.workflows.values() 
                    if w.overall_status in [ApprovalStatus.PENDING, ApprovalStatus.IN_PROGRESS]]
        
        if stage:
            workflows = [w for w in workflows if w.current_stage == stage]
        
        return sorted(workflows, key=lambda x: (x.priority_level, x.created_at), reverse=True)
    
    def get_workflow_analytics(self) -> Dict[str, Any]:
        """Get analytics about workflow performance"""
        if not self.workflows:
            return {'error': 'No workflows to analyze'}
        
        workflows = list(self.workflows.values())
        
        # Status distribution
        status_counts = defaultdict(int)
        for w in workflows:
            status_counts[w.overall_status.value] += 1
        
        # Stage distribution
        stage_counts = defaultdict(int)
        for w in workflows:
            stage_counts[w.current_stage.value] += 1
        
        # Average processing time
        completed_workflows = [w for w in workflows if w.overall_status == ApprovalStatus.COMPLETED]
        if completed_workflows:
            avg_processing_time = sum([
                (w.updated_at - w.created_at).total_seconds() / 3600
                for w in completed_workflows
            ]) / len(completed_workflows)
        else:
            avg_processing_time = 0
        
        # SLA compliance
        sla_breaches = sum(1 for w in workflows if datetime.datetime.now() > w.sla_deadline 
                          and w.overall_status != ApprovalStatus.COMPLETED)
        
        return {
            'total_workflows': len(workflows),
            'status_distribution': dict(status_counts),
            'stage_distribution': dict(stage_counts),
            'average_processing_time_hours': round(avg_processing_time, 2),
            'sla_breach_count': sla_breaches,
            'ai_auto_approval_rate': self._calculate_ai_auto_approval_rate(),
            'completion_rate': len(completed_workflows) / len(workflows) * 100 if workflows else 0
        }
    
    def _calculate_ai_auto_approval_rate(self) -> float:
        """Calculate rate of AI auto-approvals"""
        ai_decisions = []
        for workflow in self.workflows.values():
            for action in workflow.actions_history:
                if action.approver_role == ApprovalRole.AI_SYSTEM:
                    ai_decisions.append(action.decision)
        
        if not ai_decisions:
            return 0.0
        
        auto_approvals = sum(1 for d in ai_decisions if d == ApprovalDecision.AUTO_APPROVE)
        return (auto_approvals / len(ai_decisions)) * 100

# Usage example and testing
async def demo_approval_workflow():
    """Demonstrate the approval workflow system"""
    engine = ApprovalWorkflowEngine()
    
    # Sample project data
    project_data = {
        'project_id': 'MRV-2024-001',
        'project_type': 'mangrove_restoration',
        'organization_id': 'ngo_001',
        'area': 150,
        'duration_months': 24,
        'budget': 500000,
        'coordinates': {
            'latitude': 21.9497,
            'longitude': 88.2314
        },
        'documents': [
            {'type': 'environmental_clearance', 'digital_signature': True},
            {'type': 'land_ownership', 'digital_signature': False},
            {'type': 'project_proposal', 'digital_signature': True}
        ]
    }
    
    print("=== Multi-layer Approval Workflow Demo ===\n")
    
    # Create workflow
    workflow_id = engine.create_workflow('MRV-2024-001', project_data, priority=4)
    print(f"Created workflow: {workflow_id}")
    
    # Process AI verification
    await engine.process_workflow_step(workflow_id)
    
    workflow = engine.get_workflow(workflow_id)
    print(f"Current stage: {workflow.current_stage.value}")
    print(f"Overall status: {workflow.overall_status.value}")
    
    if workflow.actions_history:
        last_action = workflow.actions_history[-1]
        print(f"Last action: {last_action.decision.value} by {last_action.approver_role.value}")
        if last_action.confidence_score:
            print(f"AI Confidence: {last_action.confidence_score:.1f}%")
    
    # Simulate manual approval if needed
    if workflow.overall_status == ApprovalStatus.PENDING:
        print("\nSimulating manual approval...")
        engine.manual_approval(
            workflow_id,
            "admin_001",
            ApprovalRole.ADMIN,
            ApprovalDecision.APPROVE,
            "Manual review completed. Project approved for implementation."
        )
        
        # Process next steps
        await engine.process_workflow_step(workflow_id)
    
    # Get analytics
    analytics = engine.get_workflow_analytics()
    print(f"\n=== Workflow Analytics ===")
    print(f"Total workflows: {analytics['total_workflows']}")
    print(f"AI auto-approval rate: {analytics['ai_auto_approval_rate']:.1f}%")
    print(f"Average processing time: {analytics['average_processing_time_hours']} hours")
    
    return engine

if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_approval_workflow())