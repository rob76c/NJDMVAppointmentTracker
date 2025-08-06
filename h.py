import smtplib
import ssl
from email.message import EmailMessage
import os
from dotenv import load_dotenv

def send_email(subject, content):

    load_dotenv()

    # Configuration
    smtp_server = "smtp.sendgrid.net"
    port = 587  # For TLS: 587, For SSL: 465
    username = os.getenv("key")  # SendGrid username is usually 'apikey'
    password = os.getenv("password")  # Replace with your SendGrid API Key
    sender_email = os.getenv("sender_email")  # Verified sender in SendGrid
    receiver_email = os.getenv("receiver_email") # The recipient's email address 

    # Create email message
    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.set_content(content)

    # Try to send the email
    try:
        if port == 465:
            # SSL connection
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(username, password)
                server.send_message(msg)
        else:
            # TLS connection
            with smtplib.SMTP(smtp_server, port) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(username, password)
                server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
