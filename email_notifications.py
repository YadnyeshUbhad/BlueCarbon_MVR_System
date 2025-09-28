"""
Email Notification System for BlueCarbon MRV Platform
Using Resend API for reliable email delivery
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class EmailNotificationSystem:
    """Email notification system with Resend API integration and SMTP fallback"""
    
    def __init__(self):
        # Resend API configuration
        self.resend_api_key = os.getenv('RESEND_API_KEY')
        self.resend_api_url = 'https://api.resend.com/emails'
        
        # SMTP configuration (fallback)
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        
        # Email settings
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@bluecarbon.mrv')
        self.from_name = 'BlueCarbon MRV Platform'
        self.admin_email = os.getenv('ADMIN_EMAIL', 'admin@bluecarbon.mrv')
        self.use_resend = bool(self.resend_api_key)
        
    def send_email_via_resend(self, to_email: str, subject: str, html_content: str, 
                             text_content: str = None) -> bool:
        """Send email using Resend API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.resend_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'from': f'{self.from_name} <{self.from_email}>',
                'to': [to_email],
                'subject': subject,
                'html': html_content
            }
            
            if text_content:
                data['text'] = text_content
            
            response = requests.post(self.resend_api_url, headers=headers, json=data)
            
            if response.status_code == 200:
                logger.info(f"Email sent successfully via Resend to {to_email}")
                return True
            else:
                logger.error(f"Resend API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email via Resend: {e}")
            return False
    
    def send_email_via_smtp(self, to_email: str, subject: str, html_content: str, 
                           text_content: str = None) -> bool:
        """Send email using SMTP (fallback)"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f'{self.from_name} <{self.from_email}>'
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully via SMTP to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email via SMTP: {e}")
            return False
    
    def send_email(self, to_email: str, subject: str, html_content: str, 
                   text_content: str = None) -> bool:
        """Send email using preferred method (Resend first, SMTP as fallback)"""
        if self.use_resend:
            success = self.send_email_via_resend(to_email, subject, html_content, text_content)
            if success:
                return True
            # Fall back to SMTP if Resend fails
            logger.info("Falling back to SMTP due to Resend failure")
        
        if self.smtp_username and self.smtp_password:
            return self.send_email_via_smtp(to_email, subject, html_content, text_content)
        
        logger.error("No email configuration available - neither Resend nor SMTP")
        return False
    
    def create_html_template(self, title: str, content: str, action_button: Dict[str, str] = None) -> str:
        """Create a professional HTML email template"""
        action_button_html = ""
        if action_button:
            action_button_html = f"""
            <div style="text-align: center; margin: 30px 0;">
                <a href="{action_button['url']}" 
                   style="background: #0077B6; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 8px; display: inline-block;">
                    {action_button['text']}
                </a>
            </div>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #0077B6 0%, #00B4D8 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">🌊 BlueCarbon MRV</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0;">Marine Restoration & Verification Platform</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 40px 30px;">
                    <h2 style="color: #0077B6; margin-top: 0;">{title}</h2>
                    <div style="font-size: 16px; color: #555;">
                        {content}
                    </div>
                    {action_button_html}
                </div>
                
                <!-- Footer -->
                <div style="background: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #eee;">
                    <p style="margin: 0; font-size: 12px; color: #666;">
                        © 2024 BlueCarbon MRV Platform. All rights reserved.<br>
                        This is an automated message. Please do not reply to this email.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    # NGO-related notifications
    def send_ngo_registration_confirmation(self, email: str, name: str, org_name: str) -> bool:
        """Send NGO registration confirmation email"""
        subject = "🌱 Registration Received - BlueCarbon MRV"
        content = f"""
        <p>Dear {name},</p>
        <p>Thank you for registering <strong>{org_name}</strong> with the BlueCarbon MRV Platform!</p>
        <p><strong>What happens next?</strong></p>
        <ul>
            <li>Our team will review your application within <strong>2-3 business days</strong></li>
            <li>You'll receive an email notification once your account is approved</li>
            <li>After approval, you can access the full NGO portal and start submitting projects</li>
        </ul>
        <p><strong>Required documents for approval:</strong></p>
        <ul>
            <li>NGO Registration Certificate</li>
            <li>Tax Exemption Certificate</li>
            <li>Bank Account Proof</li>
            <li>Contact person ID proof</li>
        </ul>
        <p>If you have any questions, please contact our support team.</p>
        <p>Best regards,<br>BlueCarbon MRV Team</p>
        """
        
        html_content = self.create_html_template(
            "Registration Confirmation",
            content,
            {"text": "Track Application Status", "url": "https://platform.bluecarbon.mrv/ngo/login"}
        )
        
        return self.send_email(email, subject, html_content)
    
    def send_ngo_approval_notification(self, email: str, name: str, org_name: str) -> bool:
        """Send NGO approval notification"""
        subject = "🎉 Account Approved - Welcome to BlueCarbon MRV!"
        content = f"""
        <p>Dear {name},</p>
        <p>Great news! Your NGO registration for <strong>{org_name}</strong> has been approved! 🎉</p>
        <p><strong>You can now:</strong></p>
        <ul>
            <li>Access your complete NGO portal</li>
            <li>Submit blue carbon restoration projects</li>
            <li>Track project verification status</li>
            <li>Manage carbon credits and revenue</li>
            <li>Monitor projects via satellite and drone data</li>
        </ul>
        <p><strong>Getting Started:</strong></p>
        <ol>
            <li>Log in to your NGO portal</li>
            <li>Complete your organization profile</li>
            <li>Submit your first project</li>
        </ol>
        <p>Welcome to the future of marine restoration!</p>
        <p>Best regards,<br>BlueCarbon MRV Team</p>
        """
        
        html_content = self.create_html_template(
            "Account Approved!",
            content,
            {"text": "Access NGO Portal", "url": "https://platform.bluecarbon.mrv/ngo/login"}
        )
        
        return self.send_email(email, subject, html_content)
    
    def send_ngo_rejection_notification(self, email: str, name: str, reason: str) -> bool:
        """Send NGO rejection notification"""
        subject = "❌ Application Status Update - BlueCarbon MRV"
        content = f"""
        <p>Dear {name},</p>
        <p>Thank you for your interest in the BlueCarbon MRV Platform.</p>
        <p>After reviewing your application, we need additional information before we can proceed with approval:</p>
        <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin: 20px 0;">
            <strong>Reason for revision request:</strong><br>
            {reason}
        </div>
        <p><strong>Next Steps:</strong></p>
        <ul>
            <li>Please address the issues mentioned above</li>
            <li>Submit the required documentation or information</li>
            <li>Contact our support team if you need assistance</li>
        </ul>
        <p>We're here to help you succeed in your marine restoration efforts!</p>
        <p>Best regards,<br>BlueCarbon MRV Team</p>
        """
        
        html_content = self.create_html_template(
            "Application Needs Attention",
            content,
            {"text": "Contact Support", "url": "mailto:support@bluecarbon.mrv"}
        )
        
        return self.send_email(email, subject, html_content)
    
    # Project-related notifications
    def send_project_approval_notification(self, email: str, ngo_name: str, project_name: str, 
                                         credits_approved: int, token_id: str) -> bool:
        """Send project approval notification"""
        subject = f"🎉 Project Approved: {project_name}"
        content = f"""
        <p>Dear {ngo_name} Team,</p>
        <p>Excellent news! Your project <strong>"{project_name}"</strong> has been approved! 🎉</p>
        
        <div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #155724;">Project Details:</h3>
            <ul style="margin: 10px 0;">
                <li><strong>Project:</strong> {project_name}</li>
                <li><strong>Credits Approved:</strong> {credits_approved} tCO₂e</li>
                <li><strong>Token ID:</strong> {token_id}</li>
                <li><strong>Approval Date:</strong> {datetime.now().strftime('%B %d, %Y')}</li>
            </ul>
        </div>
        
        <p><strong>What's Next?</strong></p>
        <ul>
            <li>Your carbon credits are now available in the marketplace</li>
            <li>You can track sales and revenue in your NGO portal</li>
            <li>Monitor project progress with our satellite and drone tools</li>
            <li>Set up withdrawal preferences for revenue collection</li>
        </ul>
        
        <p>Congratulations on this important milestone in marine conservation!</p>
        <p>Best regards,<br>BlueCarbon MRV Team</p>
        """
        
        html_content = self.create_html_template(
            "Project Approved!",
            content,
            {"text": "View Project Details", "url": "https://platform.bluecarbon.mrv/ngo/projects"}
        )
        
        return self.send_email(email, subject, html_content)
    
    # Industry-related notifications
    def send_industry_registration_confirmation(self, email: str, contact_person: str, company_name: str) -> bool:
        """Send industry registration confirmation"""
        subject = "🏭 Registration Received - BlueCarbon MRV"
        content = f"""
        <p>Dear {contact_person},</p>
        <p>Thank you for registering <strong>{company_name}</strong> with the BlueCarbon MRV Platform!</p>
        <p><strong>Application Review Process:</strong></p>
        <ul>
            <li>Our compliance team will review your application within <strong>3-5 business days</strong></li>
            <li>We'll verify your company details and environmental commitments</li>
            <li>You'll receive approval notification via email</li>
            <li>After approval, you can access the carbon credits marketplace</li>
        </ul>
        <p><strong>What You'll Get Access To:</strong></p>
        <ul>
            <li>Verified carbon credits marketplace</li>
            <li>Real-time project monitoring</li>
            <li>Carbon footprint tracking tools</li>
            <li>Compliance reporting features</li>
            <li>Direct connection with NGO projects</li>
        </ul>
        <p>Thank you for your commitment to environmental sustainability!</p>
        <p>Best regards,<br>BlueCarbon MRV Team</p>
        """
        
        html_content = self.create_html_template(
            "Registration Confirmation",
            content,
            {"text": "Track Application", "url": "https://platform.bluecarbon.mrv/industry/login"}
        )
        
        return self.send_email(email, subject, html_content)
    
    def send_credits_purchase_notification(self, ngo_email: str, industry_email: str, admin_email: str,
                                         ngo_name: str, industry_name: str, project_name: str, 
                                         credits: int, total_amount: float, transaction_id: str) -> bool:
        """Send notifications for credit purchase to all stakeholders"""
        success_count = 0
        
        # NGO Notification
        ngo_subject = f"💰 Credits Sold: {credits} tCO₂e from {project_name}"
        ngo_content = f"""
        <p>Dear {ngo_name} Team,</p>
        <p>Great news! <strong>{industry_name}</strong> has purchased carbon credits from your project! 💰</p>
        
        <div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #155724;">Transaction Details:</h3>
            <ul style="margin: 10px 0;">
                <li><strong>Buyer:</strong> {industry_name}</li>
                <li><strong>Project:</strong> {project_name}</li>
                <li><strong>Credits Sold:</strong> {credits} tCO₂e</li>
                <li><strong>Total Amount:</strong> ₹{total_amount:,.2f}</li>
                <li><strong>Transaction ID:</strong> {transaction_id}</li>
            </ul>
        </div>
        
        <p><strong>Revenue Management:</strong></p>
        <ul>
            <li>Funds will be processed within 2-3 business days</li>
            <li>You can request withdrawal from your NGO portal</li>
            <li>Track all transactions in your revenue dashboard</li>
        </ul>
        
        <p>Thank you for your continued commitment to marine restoration!</p>
        <p>Best regards,<br>BlueCarbon MRV Team</p>
        """
        
        ngo_html = self.create_html_template(
            "Credits Sold Successfully!",
            ngo_content,
            {"text": "View Revenue Dashboard", "url": "https://platform.bluecarbon.mrv/ngo/revenue"}
        )
        
        if self.send_email(ngo_email, ngo_subject, ngo_html):
            success_count += 1
        
        # Industry Notification
        industry_subject = f"✅ Purchase Confirmed: {credits} Carbon Credits"
        industry_content = f"""
        <p>Dear {industry_name} Team,</p>
        <p>Your carbon credits purchase has been confirmed! ✅</p>
        
        <div style="background: #cce5ff; border: 1px solid #99ccff; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #0066cc;">Purchase Summary:</h3>
            <ul style="margin: 10px 0;">
                <li><strong>Project:</strong> {project_name}</li>
                <li><strong>NGO Partner:</strong> {ngo_name}</li>
                <li><strong>Credits Purchased:</strong> {credits} tCO₂e</li>
                <li><strong>Total Paid:</strong> ₹{total_amount:,.2f}</li>
                <li><strong>Transaction ID:</strong> {transaction_id}</li>
            </ul>
        </div>
        
        <p><strong>Your Impact:</strong></p>
        <ul>
            <li>You've directly supported marine restoration efforts</li>
            <li>Credits are now available in your portfolio</li>
            <li>Use these credits for your sustainability reporting</li>
            <li>Consider retiring credits to offset your emissions</li>
        </ul>
        
        <p>Thank you for choosing verified blue carbon credits!</p>
        <p>Best regards,<br>BlueCarbon MRV Team</p>
        """
        
        industry_html = self.create_html_template(
            "Purchase Confirmed!",
            industry_content,
            {"text": "View Your Credits", "url": "https://platform.bluecarbon.mrv/industry/credits"}
        )
        
        if self.send_email(industry_email, industry_subject, industry_html):
            success_count += 1
        
        # Admin Notification
        admin_subject = f"🔄 Transaction Completed: {transaction_id}"
        admin_content = f"""
        <p>Dear Admin,</p>
        <p>A new carbon credits transaction has been completed on the platform.</p>
        
        <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Transaction Details:</h3>
            <ul style="margin: 10px 0;">
                <li><strong>Transaction ID:</strong> {transaction_id}</li>
                <li><strong>Buyer:</strong> {industry_name}</li>
                <li><strong>Seller (NGO):</strong> {ngo_name}</li>
                <li><strong>Project:</strong> {project_name}</li>
                <li><strong>Credits:</strong> {credits} tCO₂e</li>
                <li><strong>Amount:</strong> ₹{total_amount:,.2f}</li>
                <li><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</li>
            </ul>
        </div>
        
        <p><strong>Platform Revenue:</strong> ₹{total_amount * 0.05:,.2f} (5% commission)</p>
        
        <p>Best regards,<br>BlueCarbon MRV System</p>
        """
        
        admin_html = self.create_html_template(
            "Transaction Notification",
            admin_content,
            {"text": "View Admin Dashboard", "url": "https://platform.bluecarbon.mrv/admin/transactions"}
        )
        
        if self.send_email(admin_email, admin_subject, admin_html):
            success_count += 1
        
        return success_count >= 2  # Success if at least 2 out of 3 emails sent
    
    def send_withdrawal_request_notification(self, ngo_email: str, admin_email: str, 
                                           ngo_name: str, amount: float, request_id: str) -> bool:
        """Send withdrawal request notifications"""
        success_count = 0
        
        # NGO Confirmation
        ngo_subject = f"💳 Withdrawal Request Submitted: ₹{amount:,.2f}"
        ngo_content = f"""
        <p>Dear {ngo_name} Team,</p>
        <p>Your withdrawal request has been successfully submitted! 💳</p>
        
        <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #856404;">Request Details:</h3>
            <ul style="margin: 10px 0;">
                <li><strong>Amount:</strong> ₹{amount:,.2f}</li>
                <li><strong>Request ID:</strong> {request_id}</li>
                <li><strong>Status:</strong> Pending Review</li>
                <li><strong>Expected Processing:</strong> 2-3 business days</li>
            </ul>
        </div>
        
        <p><strong>What happens next?</strong></p>
        <ul>
            <li>Our finance team will review your request</li>
            <li>You'll receive confirmation once approved</li>
            <li>Funds will be transferred to your registered account</li>
        </ul>
        
        <p>You can track the status in your NGO portal.</p>
        <p>Best regards,<br>BlueCarbon MRV Team</p>
        """
        
        ngo_html = self.create_html_template(
            "Withdrawal Request Submitted",
            ngo_content,
            {"text": "Track Request", "url": "https://platform.bluecarbon.mrv/ngo/revenue"}
        )
        
        if self.send_email(ngo_email, ngo_subject, ngo_html):
            success_count += 1
        
        # Admin Notification
        admin_subject = f"💳 New Withdrawal Request: {ngo_name} - ₹{amount:,.2f}"
        admin_content = f"""
        <p>Dear Admin,</p>
        <p>A new withdrawal request requires your approval.</p>
        
        <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #856404;">Request Details:</h3>
            <ul style="margin: 10px 0;">
                <li><strong>NGO:</strong> {ngo_name}</li>
                <li><strong>Amount:</strong> ₹{amount:,.2f}</li>
                <li><strong>Request ID:</strong> {request_id}</li>
                <li><strong>Submitted:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</li>
                <li><strong>Status:</strong> Awaiting Admin Approval</li>
            </ul>
        </div>
        
        <p><strong>Action Required:</strong> Please review and approve/reject this withdrawal request in the admin panel.</p>
        
        <p>Best regards,<br>BlueCarbon MRV System</p>
        """
        
        admin_html = self.create_html_template(
            "Withdrawal Request - Action Required",
            admin_content,
            {"text": "Review Request", "url": "https://platform.bluecarbon.mrv/admin/withdrawals"}
        )
        
        if self.send_email(admin_email, admin_subject, admin_html):
            success_count += 1
        
        return success_count >= 1
    
    def send_fraud_detection_alert(self, admin_email: str, ngo_email: str, auditor_email: str,
                                 alert_type: str, details: Dict[str, Any]) -> bool:
        """Send fraud detection alerts to relevant stakeholders"""
        success_count = 0
        
        # Determine severity and icon
        severity_icons = {
            'critical': '🚨',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
        
        severity = details.get('severity', 'warning')
        icon = severity_icons.get(severity, '⚠️')
        
        subject = f"{icon} Fraud Alert: {alert_type}"
        
        content = f"""
        <div style="background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #721c24;">🚨 Fraud Detection Alert</h3>
            <ul style="margin: 10px 0;">
                <li><strong>Alert Type:</strong> {alert_type}</li>
                <li><strong>Severity:</strong> {severity.title()}</li>
                <li><strong>Time:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</li>
                <li><strong>Description:</strong> {details.get('description', 'Suspicious activity detected')}</li>
                <li><strong>Entity:</strong> {details.get('entity', 'Unknown')}</li>
                <li><strong>Score:</strong> {details.get('risk_score', 0)}/100</li>
            </ul>
        </div>
        
        <p><strong>Immediate Action Required:</strong></p>
        <ul>
            <li>Review the flagged activity immediately</li>
            <li>Investigate all related transactions</li>
            <li>Consider temporary suspension if necessary</li>
            <li>Document findings in the admin panel</li>
        </ul>
        
        <p>This alert was generated by our AI-powered fraud detection system.</p>
        <p>Best regards,<br>BlueCarbon MRV Security Team</p>
        """
        
        html_content = self.create_html_template(
            f"Fraud Alert: {alert_type}",
            content,
            {"text": "Investigate Now", "url": "https://platform.bluecarbon.mrv/admin/fraud-alerts"}
        )
        
        # Send to admin (always)
        if self.send_email(admin_email, subject, html_content):
            success_count += 1
        
        # Send to NGO if they're involved
        if ngo_email and details.get('involves_ngo', False):
            if self.send_email(ngo_email, subject, html_content):
                success_count += 1
        
        # Send to auditor for critical alerts
        if auditor_email and severity == 'critical':
            if self.send_email(auditor_email, subject, html_content):
                success_count += 1
        
        return success_count >= 1

# Global email notification system instance
email_system = EmailNotificationSystem()

def send_test_emails():
    """Test function to verify email system"""
    print("Testing email notification system...")
    
    # Test NGO registration
    success = email_system.send_ngo_registration_confirmation(
        "test@example.com", 
        "John Doe", 
        "Green Ocean Foundation"
    )
    print(f"NGO registration email: {'✅' if success else '❌'}")
    
    # Test credit purchase notification
    success = email_system.send_credits_purchase_notification(
        "ngo@example.com",
        "industry@example.com", 
        "admin@example.com",
        "Green Ocean Foundation",
        "EcoTech Industries",
        "Sundarbans Mangrove Restoration",
        100,
        25000.0,
        "TXN123456"
    )
    print(f"Credit purchase notifications: {'✅' if success else '❌'}")
    
    print("Email system test complete!")

if __name__ == "__main__":
    send_test_emails()