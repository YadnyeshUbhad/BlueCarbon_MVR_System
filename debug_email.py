#!/usr/bin/env python3
"""
Enhanced Email Debug Script
Test different sender configurations to ensure delivery
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def test_email_with_different_senders():
    """Test email with different sender configurations"""
    
    smtp_host = 'smtp-relay.brevo.com'
    smtp_port = 587
    username = '97c0ad001@smtp-brevo.com'
    password = 'TQ9EVHvPY5IMhsLF'
    
    # Test different sender configurations
    sender_configs = [
        {
            'from_email': username,
            'from_name': 'BlueCarbon MRV',
            'reply_to': username
        },
        {
            'from_email': username,  
            'from_name': 'BlueCarbon Platform',
            'reply_to': 'noreply@bluecarbon.com'
        }
    ]
    
    recipient = 'ubhadsatishm@gmail.com'
    
    for i, config in enumerate(sender_configs, 1):
        print(f"\n🧪 Testing Configuration {i}:")
        print(f"From: {config['from_name']} <{config['from_email']}>")
        print(f"Reply-To: {config['reply_to']}")
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{config['from_name']} <{config['from_email']}>"
            msg['To'] = recipient
            msg['Reply-To'] = config['reply_to']
            msg['Subject'] = f"🌊 BlueCarbon MRV Test #{i} - {datetime.now().strftime('%H:%M:%S')}"
            
            # Plain text version
            text_content = f"""
Hello!

This is test email #{i} from BlueCarbon MRV Platform.

Configuration Details:
- Sender: {config['from_name']} <{config['from_email']}>
- Reply-To: {config['reply_to']}
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Test ID: TEST-{i}-{datetime.now().strftime('%H%M%S')}

If you receive this email, the configuration is working!

Best regards,
BlueCarbon MRV Team
            """
            
            # HTML version
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>BlueCarbon MRV Test Email</title>
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #0077B6; margin: 0;">🌊 BlueCarbon MRV</h1>
                        <p style="color: #666; margin: 5px 0;">Test Email #{i}</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #333;">✅ Email Delivery Test</h3>
                        <p><strong>Configuration:</strong> {config['from_name']} &lt;{config['from_email']}&gt;</p>
                        <p><strong>Reply-To:</strong> {config['reply_to']}</p>
                        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p><strong>Test ID:</strong> TEST-{i}-{datetime.now().strftime('%H%M%S')}</p>
                    </div>
                    
                    <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 0; color: #1565c0;">
                            <strong>📧 Success!</strong> If you're reading this, our email configuration is working correctly.
                        </p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <p style="color: #666; font-size: 12px; margin: 0;">
                            BlueCarbon MRV Platform - Marine Restoration & Verification<br>
                            This is an automated test email.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Attach both versions
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(username, password)
                result = server.send_message(msg)
                
            print(f"✅ Test #{i} sent successfully!")
            print(f"📨 Check your inbox: {recipient}")
            
        except Exception as e:
            print(f"❌ Test #{i} failed: {str(e)}")
    
    return True

def test_simple_direct_email():
    """Test with the most basic configuration possible"""
    print("\n🔧 Testing Simple Direct Email...")
    
    smtp_host = 'smtp-relay.brevo.com'
    smtp_port = 587
    username = '97c0ad001@smtp-brevo.com'
    password = 'TQ9EVHvPY5IMhsLF'
    
    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(username, password)
        
        # Simple message
        from_addr = username
        to_addr = 'ubhadsatishm@gmail.com'
        subject = f"Simple Test {datetime.now().strftime('%H:%M:%S')}"
        body = f"""Hello from BlueCarbon MRV!

This is a simple test email sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.

If you receive this, our email setup is working!

Best regards,
BlueCarbon Team"""

        msg = f"""From: {from_addr}
To: {to_addr}
Subject: {subject}

{body}"""

        server.sendmail(from_addr, [to_addr], msg)
        server.quit()
        
        print("✅ Simple email sent successfully!")
        print(f"📧 Check: {to_addr}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple email failed: {str(e)}")
        return False

def main():
    print("="*60)
    print("🔍 BlueCarbon MRV - Email Delivery Debug")
    print("="*60)
    
    # Test 1: Simple direct email
    test_simple_direct_email()
    
    # Test 2: Different sender configurations
    test_email_with_different_senders()
    
    print(f"\n📋 Next Steps:")
    print(f"1. Check your inbox: ubhadsatishm@gmail.com")
    print(f"2. Check SPAM/Junk folder")
    print(f"3. Check Brevo dashboard for delivery status")
    print(f"4. If no emails arrive, we may need to verify sender domain")
    
    print("\n⏰ Note: Email delivery can take 1-5 minutes")
    print("="*60)

if __name__ == "__main__":
    main()