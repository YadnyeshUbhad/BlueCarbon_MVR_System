#!/usr/bin/env python3
"""
Final Email Test with Maximum Deliverability
Uses all proper headers and best practices for email delivery
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
import socket
from datetime import datetime

def send_final_test_email():
    """Send test email with all proper headers for maximum deliverability"""
    
    # SMTP Configuration
    smtp_host = 'smtp-relay.brevo.com'
    smtp_port = 587
    username = '97c0ad001@smtp-brevo.com'
    password = 'TQ9EVHvPY5IMhsLF'
    
    # Email addresses
    from_email = username
    from_name = "BlueCarbon MRV Platform"
    to_email = "ubhadsatishm@gmail.com"
    
    print("🚀 Sending Final Test Email with Maximum Deliverability...")
    print(f"From: {from_name} <{from_email}>")
    print(f"To: {to_email}")
    
    try:
        # Create message with proper headers
        msg = MIMEMultipart('alternative')
        
        # Essential headers
        msg['From'] = f'{from_name} <{from_email}>'
        msg['To'] = to_email
        msg['Subject'] = f'🔵 BlueCarbon MRV - FINAL TEST EMAIL ({datetime.now().strftime("%H:%M")})'
        msg['Date'] = formatdate(localtime=True)
        msg['Message-ID'] = make_msgid(domain=smtp_host)
        
        # Additional headers for better deliverability
        msg['X-Mailer'] = 'BlueCarbon MRV System v1.0'
        msg['X-Priority'] = '3'
        msg['X-MSMail-Priority'] = 'Normal'
        msg['Importance'] = 'Normal'
        msg['Reply-To'] = from_email
        msg['Return-Path'] = from_email
        
        # Content
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Plain text version
        text_content = f"""
🔵 BlueCarbon MRV - Final Email Test

Hello Satish!

This is the FINAL test email from BlueCarbon MRV Platform.

Test Details:
- Time: {current_time}
- Sender: {from_name} <{from_email}>
- SMTP: Brevo (smtp-relay.brevo.com)
- Method: Enhanced headers for maximum deliverability

🔍 What to check:
1. Primary inbox
2. Spam/Junk folder
3. Gmail's "Updates" or "Promotions" tab

If you receive this email, our configuration is 100% working!

Technical Details:
- Message ID: {make_msgid(domain=smtp_host)}
- Server: {smtp_host}:{smtp_port}
- Encryption: TLS

Best regards,
BlueCarbon MRV Development Team
        """

        # HTML version with better structure
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>BlueCarbon MRV - Final Test</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0077B6, #00B4D8); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: white; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .success-box {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .info-box {{ background: #f8f9fa; border-left: 4px solid #0077B6; padding: 20px; margin: 20px 0; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body style="background-color: #f4f4f4; padding: 20px;">
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">🔵 BlueCarbon MRV</h1>
                    <p style="margin: 10px 0 0 0;">Final Email Delivery Test</p>
                </div>
                
                <div class="content">
                    <h2 style="color: #0077B6; margin-top: 0;">Hello Satish! 👋</h2>
                    
                    <div class="success-box">
                        <h3 style="margin-top: 0;">✅ SUCCESS!</h3>
                        <p style="margin-bottom: 0;">If you're reading this, our email system is working perfectly!</p>
                    </div>
                    
                    <p>This is the <strong>FINAL test email</strong> from the BlueCarbon MRV Platform with enhanced deliverability settings.</p>
                    
                    <div class="info-box">
                        <h4 style="margin-top: 0; color: #0077B6;">📊 Test Information:</h4>
                        <ul>
                            <li><strong>Time:</strong> {current_time}</li>
                            <li><strong>Sender:</strong> {from_name} &lt;{from_email}&gt;</li>
                            <li><strong>SMTP Server:</strong> Brevo (smtp-relay.brevo.com)</li>
                            <li><strong>Encryption:</strong> TLS</li>
                            <li><strong>Headers:</strong> Enhanced for deliverability</li>
                        </ul>
                    </div>
                    
                    <h4>🔍 Where to look for this email:</h4>
                    <ol>
                        <li><strong>Primary Inbox</strong> (most likely)</li>
                        <li><strong>Spam/Junk folder</strong> (check here if not in inbox)</li>
                        <li><strong>Gmail tabs:</strong> Updates or Promotions</li>
                        <li><strong>All Mail</strong> folder</li>
                    </ol>
                    
                    <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin-top: 30px;">
                        <p style="margin: 0; color: #1565c0;">
                            <strong>🎉 Great news!</strong> If you receive this email, the BlueCarbon MRV Platform's email system is 100% operational and ready for production use!
                        </p>
                    </div>
                </div>
                
                <div class="footer">
                    <p>BlueCarbon MRV Platform - Marine Restoration & Verification System</p>
                    <p>This is an automated test email • {current_time}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Attach both versions
        text_part = MIMEText(text_content.strip(), 'plain', 'utf-8')
        html_part = MIMEText(html_content.strip(), 'html', 'utf-8')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Send email with enhanced connection
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(username, password)
        
        # Send the email
        send_result = server.send_message(msg)
        server.quit()
        
        print("✅ Final test email sent successfully!")
        print(f"📨 Email should arrive at: {to_email}")
        print(f"⏰ Check in 1-5 minutes")
        print(f"🔍 Don't forget to check your spam folder!")
        
        return True
        
    except Exception as e:
        print(f"❌ Final test failed: {str(e)}")
        return False

def main():
    print("="*70)
    print("🔵 BlueCarbon MRV - FINAL EMAIL DELIVERY TEST")
    print("="*70)
    
    success = send_final_test_email()
    
    print("\n" + "="*70)
    if success:
        print("📧 EMAIL SENT SUCCESSFULLY!")
        print()
        print("📋 NEXT STEPS:")
        print("1. Check your primary inbox: ubhadsatishm@gmail.com")
        print("2. ⚠️  IMPORTANT: Check SPAM/JUNK folder")
        print("3. In Gmail, also check 'Updates' and 'Promotions' tabs")
        print("4. Search for 'BlueCarbon' in your email")
        print("5. Email may take 1-5 minutes to arrive")
        print()
        print("💡 If still no email after 10 minutes:")
        print("   - Check Brevo dashboard for delivery status")
        print("   - Verify sender email in Brevo console")
        print("   - Try using a different recipient email for testing")
        
    else:
        print("❌ EMAIL SENDING FAILED!")
        print("Please check SMTP credentials and try again.")
    
    print("="*70)

if __name__ == "__main__":
    main()