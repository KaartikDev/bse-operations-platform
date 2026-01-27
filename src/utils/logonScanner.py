import re

def checkLogon(reference_email:str, email_to_check:str)->bool:
    """
    Checks the logon of the email_to_check with the reference email to see if they are the same person
    """
    # Regex to capture the part before the @
    pattern = r'^([^@]+)@'
    match1 = re.search(pattern, reference_email)
    match2 = re.search(pattern, email_to_check)
    
    if match1 and match2:
        # Extract the captured group (index 1)
        user1 = match1.group(1)
        user2 = match2.group(1)
        
        if user1 == user2:
            return True
        else:
            return False
