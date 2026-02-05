import base64
from email.message import EmailMessage
import inspect
from utils import sheets

def send_email(service, recipient, subject, body_html):
    """
    Create and send an email message via Gmail API.
    Will default use the google cloud project's app email.
    """
    # 1. Construct the email
    message = EmailMessage()
    message.set_content(body_html, subtype='html')
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

def send_mentorship_notification(service, recipient, state, mentee_data):
    first_name = sheets.get_first_name(mentee_data).upper()
    last_name = sheets.get_last_name(mentee_data).upper()

    subject = ""
    body = ""

    if state == "NAME_MISMATCH" or state == "NOT_A_GM":
        subject = f"[{first_name} {last_name}][APPLICATION ERROR][AUTOMATED EMAIL]"
        body = (
            f"""
            <p>Dear {first_name} {last_name},</p>
            <p>Thank you for your interest in becoming a mentee. This is an automated message regarding your application to participate in the BSE Mentorship Program.</p>
            <p>After our system reviewed your application, we could not verify your status as a General Member of BSE. This could be due to various reasons:</p>
            
            <ul>
                <li>You have not submitted the General Member form yet. You must be a General Member to participate.</li>
                <li>The email you provided in either your General Member form or Mentee Application form don't match.</li>
                <li>The first and last names you provided in the General Member form don't match those in your Mentee Application form.</li>
            </ul>
            
            <p>In order to be eligible for the Mentorship Program, all of the above must be resolved. Your application has not been deleted, but will not be considered until the issue is resolved. You have the ability to edit your responses in the Mentee Application form and General Member form. Pleases check to ensure all of the information is correct and consistent.</p>

            <p>If you believe this message was sent in error, you may reply to this email to ask for a manual review of your information.</p>

            <p>Best regards,<br>The BSE Team</p>
            """
        )
    elif state == "ALREADY_MENTEE":
        subject = f"[{first_name.upper()} {last_name.upper()}][APPLICATION REJECTED][AUTOMATED EMAIL]"
        body = (
            f"""
            <p>Dear {first_name} {last_name},</p>
            <p>Thank you for your interest in becoming a mentee. This is an automated message regarding your application to participate in the BSE Mentorship Program.</p>
            <p>After our system reviewed your application, we noticed that you have already been a mentee before. Due to limited mentor availability, we are only able to accept applicants who have not previously participated as mentees. As a result, we are unable to accept your application for the Mentorship Program at this time.</p> 

            <p>If you believe this message was sent in error, you may reply to this email to ask for a manual review of your information.</p>

            <p>Best regards,<br>The BSE Team</p>
            """
        )    
    # Call existing gmail sending logic here
    send_email(service, recipient, inspect.cleandoc(subject), inspect.cleandoc(body))

def send_event_email(service, recipient, state, mentee_data, event_name):
    first_name = sheets.get_first_name(mentee_data).upper()
    last_name = sheets.get_last_name(mentee_data).upper()

    subject = ""
    body = ""

    if state == "NAME_MISMATCH" or state == "NOT_A_GM":
        subject = f"[{first_name} {last_name}][APPLICATION ERROR][AUTOMATED EMAIL]"
        body = (
            f"""
            <p>Dear {first_name} {last_name},</p>
            <p>Thank you for your interest in {event_name}. This is an automated message regarding your application.</p>
            <p>After our system reviewed your application, we could not verify your status as a General Member of BSE. This could be due to various reasons:</p>
            
            <ul>
                <li>You have not submitted the General Member form yet. You must be a General Member to participate.</li>
                <li>The email you provided in either your General Member form or event signup form don't match.</li>
                <li>The first and last names you provided in the General Member form don't match those in your Mentee Application form.</li>
            </ul>

            <p>In order to be eligible to participate in this event, all of the above must be resolved. Your application has not been deleted, but will not be considered until the issue is resolved. You have the ability to edit your responses. Pleases check to ensure all of the information is correct and consistent.</p>

            <p>If you believe this message was sent in error, you may reply to this email to ask for a manual review of your information.</p>

            <p>Best regards,<br>The BSE Team</p>
            """
        )
    # Call existing gmail sending logic here
    send_email(service, recipient, inspect.cleandoc(subject), inspect.cleandoc(body))
