import base64
from email.message import EmailMessage

from googleapiclient.discovery import build
from menteeChecker import authenticate

def main():
    creds = authenticate()
    gmail_service = build("gmail", "v1", credentials=creds)
    send_mentee_is_not_GM(gmail_service, "bryanqi@g.ucla.edu", "Test", "This is a test email sent via Gmail API.")

def send_mentee_is_not_GM(service, recipient, subject, body_text):
    """
    Create and send an email message via Gmail API to notify the applicant that their mentee application was rejected since they're not a GM.
    Will default use the google cloud project's app email.
    """
    # 1. Construct the email
    message = EmailMessage()
    message.set_content(body_text)
    message["To"] = recipient
    message["Subject"] = subject
    message["From"] = "me" # "me" is a special keyword for the authenticated user

    # 2. Encode for Gmail API
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {"raw": encoded_message}

    # 3. Execute the request
    try:
        sent_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        print(f'Message Id: {sent_message["id"]}')
    except Exception as error:
        print(f'An error occurred: {error}')


if __name__ == "__main__":
    main()