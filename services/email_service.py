import smtplib
from email.mime.text import MIMEText
from models import db, SmtpServer
from services.logger import loggie

def send_mail(to: str, message: str, caption: str):
    """Sends an email via the configured SMTP server."""
    try:
        smtp_server = SmtpServer.query.filter_by(disabled=False).first()
        if not smtp_server:
            loggie.error("No active SMTP server configured")
            return {"code": 40, "message": "No active SMTP server configured", "status_code": 500}

        # Create email message
        msg = MIMEText(message)
        msg["Subject"] = caption
        msg["From"] = smtp_server.from_email
        msg["To"] = to

        # Establish SMTP connection
        try:
            if smtp_server.security == "SSL":
                server = smtplib.SMTP_SSL(smtp_server.host, smtp_server.port)
            else:
                server = smtplib.SMTP(smtp_server.host, smtp_server.port)
                if smtp_server.security == "STARTTLS":
                    server.starttls()

            # Authenticate if username/password exist
            if smtp_server.username and smtp_server.password:
                server.login(smtp_server.username, smtp_server.password)

            # Send email
            server.sendmail(smtp_server.from_email, to, msg.as_string())
            server.quit()

            loggie.info(f"Email sent successfully to {to}")
            return {"code": 0, "message": "Email sent successfully", "status_code": 200}

        except smtplib.SMTPException as smtp_err:
            loggie.error(f"SMTP error: {str(smtp_err)}")
            return {"code": 50, "message": f"SMTP error: {str(smtp_err)}", "status_code": 500}

    except Exception as e:
        loggie.error(f"Unexpected error sending email: {str(e)}")
        return {"code": 70, "message": f"An unexpected error occurred: {str(e)}", "status_code": 500}