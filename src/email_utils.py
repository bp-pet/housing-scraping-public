import json
import logging
import smtplib
from email.message import EmailMessage

email_limit = 100

class EmailSender:

    def __init__(self) -> None:
        self.emails_sent: int = 0

    def send_email(self, text_to_send: str) -> None:
        if self.emails_sent >= email_limit:
            # failsafe to not end up with a billion emails if something breaks
            raise Exception("Email limit reached, please restart program to continue")
        logging.info(f"Sending email {text_to_send}")
        with open("config/params.json", "r") as f:
            params = json.load(f)
        for target in params["TARGET_ADDRESSES"]:
            msg = EmailMessage()
            msg['Subject'] = 'Automated Python Email'
            msg['From'] = params["EMAIL_ADDRESS"]
            msg['To'] = target
            msg.set_content(text_to_send)

            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(params["EMAIL_ADDRESS"], params["EMAIL_PASSWORD"])
                    smtp.send_message(msg)
                print(f"Email sent successfully to {target}!")
                self.emails_sent += 1
            except Exception as e:
                print(f"Failed to send email: {e}")

if __name__ == "__main__":
    EmailSender().send_email('testing email')