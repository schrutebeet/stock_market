from pathlib import Path
from email.message import EmailMessage
import ssl
import smtplib


from dependencies.authenticator import mail_key

class EmailGenerator:
    """Email class capable of sending emails to various recipients.
    """
    def __init__(self):
        self.user = mail_key.user
        self.password = mail_key.password
        self.recipients = mail_key.recipients

    @staticmethod
    def read_file(file_path):
        """Static method to read the content of a file."""
        with open(file_path, 'r') as file:
            return file.read()
        
    @staticmethod
    def replace_placeholders(text, replacements):
        """Static method to replace placeholders in the text."""
        for placeholder, value in replacements.items():
            text = text.replace(f'{{{placeholder}}}', str(value))
        return text
    
    def send_email(self, subject: str, body: str) -> None:
        em = EmailMessage()
        em['From'] = self.user
        em['To'] = self.recipients
        em['Subject'] = subject
        em.set_content(body, subtype = 'html')
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(self.user, self.password)
            smtp.sendmail(self.user, self.recipients, em.as_string())


    def send_successful_start(self, placeholders: dict = {}) -> None:
        subject = 'Application Run Successful'
        body_path = Path(__file__).parent / "successful_start.txt"
        body = self.read_file(body_path)
        body = self.replace_placeholders(body, placeholders)
        self.send_email(subject, body)


EmailGenerator().send_successful_start({'n_stocks': 3000})
