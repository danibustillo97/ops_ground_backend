import os
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..schemas.email_shema import EmailRequest
from ..db import get_db

load_dotenv()

class Settings:
    SMTP_SERVER = "smtp.office365.com"
    SMTP_PORT = 587
    SMTP_USER = "noreply@arajet.com"
    SMTP_PASSWORD = 'j2efoij39202wd!'
    FROM_EMAIL = "noreply@arajet.com"

settings = Settings()

def send_email(case_id: str, to_email: str, subject: str, body: str, db: Session = Depends(get_db)):
    msg = MIMEMultipart()
    msg['From'] = settings.FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.FROM_EMAIL, to_email, msg.as_string())
        server.quit()
        print(f"Email sent to {to_email}")

        create_email_query = text("""
            INSERT INTO bender.Tbl_Ground_ops_emails (id, baggage_case_id, to_email, from_email, subject, body)
            VALUES (:id, :baggage_case_id, :to_email, :from_email, :subject, :body)
        """)

        db.execute(create_email_query, {
            "id": case_id,
            "baggage_case_id": case_id,
            "to_email": to_email,
            "from_email": settings.FROM_EMAIL,
            "subject": subject,
            "body": body
        })
        db.commit()

    except Exception as e:
        print(f"Failed to send email: {e}")
        raise e

router = APIRouter()

@router.post("/send-email/")
def send_email_endpoint(email_request: EmailRequest, db: Session = Depends(get_db)):
    try:
        send_email(email_request.case_id, email_request.to_email, email_request.subject, email_request.body, db)
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
