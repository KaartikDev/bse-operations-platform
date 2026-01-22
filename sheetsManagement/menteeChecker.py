import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from utils import sheets
from utils import gmail

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/gmail.send"] # will need to move this later to a separate gmail/sheets specific file

# ID and range of spreadsheet
GM_SPREADSHEET_ID = "1Xngw94j6M21rG-YEQLHbPTnTDtBW9sMhTSky2CXTYdY"
gm_spreadsheet_range = f"Members Jan 2026!A2:{sheets.GM_LAST_COLUMN_LETTER}{sheets.GM_NUMBER_OF_COLUMNS}" # make ranges more dynamic later
GM_SHEET_ID = "286014913"
MENTEE_SPREADSHEET_ID = "1myZZASczHp7fzHchePcb4cVuQHYxOow6YOXAPHcXPHY"
mentee_spreadsheet_range = f"Form Responses 1!A2:{sheets.MENTEE_LAST_COLUMN_LETTER}{sheets.MENTEE__NUMBER_OF_COLUMNS}" # make ranges more dynamic later
MENTEE_SHEET_ID = "829339717"

# Notes: 
# Columns: default spreadsheet starts from A = index 0
# Rows: default spreadsheet starts from 1 = index 0 (row 1 in the spreadsheet UI is the title row, first entry is row 2 which is index 1 for this program)

# forms should be 1 form per email and editable and copies of responses should be sent to the user


def run():
    """
    Checks mentee assignments in a Google Sheet.
    In this program's nomenclature, "entry" == "row".
    """
    #### ---Authenticate and construct service--- ####
    creds = authenticate()

    ### ---Create Service and Sheet Objects--- ### 
    service = sheets.create_service(creds)
    sheet = sheets.create_sheet(service)
    
    ### ---Get and Process Mentee Entries--- ###
    # 1. get entire list of mentee applicants
    mentee_ls = sheets.get_entries(sheet, MENTEE_SPREADSHEET_ID, mentee_spreadsheet_range, "Mentee")
    # 2. normalize the table to ensure all rows have the same number of columns
    print("Normalizing entries...\n")
    mentee_entries = sheets.normalize_table(mentee_ls[0], 2)
    # print("\n")
    # print(mentee_entries)
    # print("\n")
    # 3. for each applicant, check if they are verified via the verification column and if not, add it to a list to be verified
    # Use enumerate to get the 1-based index of each row
    rows_to_verify = []
    for index, entry in enumerate(mentee_entries, start=1): # starts counting at 1 instead of 0
        # maybe can turn verification into batch update too later
        if sheets.check_is_verified(entry) == True:
            print(f"Row {index} is already verified.")
        else:
            rows_to_verify.append(index)
    
    print("\nRows to verify:", rows_to_verify)

    # 4. for those who need to be verified, verify them against the GM spreadsheet
    # Check if they're 
    # 1) a GM 
    # 2) their name matches the GM names 
    # 3) they're not already/were a mentee 
    # the current logic for checking if they were a past mentee only checks at the time of submission. 
    # if the row is already verified, the code won't check it but skip over it since it'll see it's already been verified as a GM
    # this is a possible bug, but may not be a big issue since the verification is only done once when the application is first submitted
    rows_to_reject = []
    rows_was_already_mentee = []
    GMrawls = sheets.get_entries(sheet, GM_SPREADSHEET_ID, gm_spreadsheet_range, "GM")
    GM_entries = sheets.normalize_table(GMrawls[0], 1)
    for row in rows_to_verify:
        UID = mentee_entries[row-1][sheets.MENTEE_BSE_ID_COLUMN_INDEX]  # Adjust for 0-based index since enumerate counts entry 1 as 1 and not 0. 
        print(f"\nVerifying row {row} with UID {UID}...")
        # search GM entries for matching UID and firss + last names
        for GM_entry in GM_entries:
            GM_UID = GM_entry[sheets.GM_BSE_ID_COLUMN_INDEX]
            # print(GM_UID)
            if UID == GM_UID:
                print(f"Match found for UID {UID}. Verifying applicant name with GM name...")
                mentee_first_name = sheets.get_first_name(mentee_entries[row-1]).strip().lower()
                gm_first_name = sheets.get_first_name(GM_entry).strip().lower()
                mentee_last_name = sheets.get_last_name(mentee_entries[row-1]).strip().lower()
                gm_last_name = sheets.get_last_name(GM_entry).strip().lower()
                if mentee_first_name != gm_first_name or mentee_last_name != gm_last_name:
                    print(f"Name mismatch for UID {UID}. Mentee name: {mentee_first_name} {mentee_last_name}, GM name: {gm_first_name} {gm_last_name}. Marking row {row} for deletion.")
                    rows_to_reject.append(row)
                    break
                elif mentee_first_name == gm_first_name and mentee_last_name == gm_last_name:
                    print(f"Name match for UID {UID}. Marking row {row} as verified.")
                    sheets.verify_applicant(MENTEE_SPREADSHEET_ID, row, service)
                    print(f"Row {row} verified successfully.")
                if GM_entry[sheets.GM_ALREADY_MENTEE_COLUMN_INDEX].strip().lower() == "yes":
                    print(f"UID {UID} has already been a mentee before. Marking row {row} for deletion.")
                    rows_was_already_mentee.append(row)
                    break

                print("Finished checking entry.")
                break
        else:
            print(f"No match found for UID {UID}. Marking row {row} for deletion.")
            rows_to_reject.append(row)
    
    print("\nRows to reject (not verified):", rows_to_reject)
    print(len(rows_to_reject))
    rows_to_reject.sort(reverse=True)
    print(rows_to_reject)
    print("Rows who were already mentees:", rows_was_already_mentee)

    # 5. mark those who could not be verified as "No" in the "is gm" column
    update_requests = []
    for row in rows_to_reject:
        # Convert 1-based index relative to the first entry to be relative to the title row for A1 notation to match the sheets UI
        cell_range = f"Form Responses 1!{sheets.MENTEE_VERIFICATION_COLUMN_LETTER}{row + 1}" 
        update_requests.append({
            "range": cell_range,
            "values": [["No"]] # Values must be a list of lists [ [cell_value] ]
        })
    # Construct the full request body
    batch_update_values_request = {
        "valueInputOption": "RAW", # RAW inserts string as-is; USER_ENTERED parses like UI
        "data": update_requests
    }
    # Execute the batch update
    if update_requests:
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=MENTEE_SPREADSHEET_ID,
            body=batch_update_values_request
        ).execute()
        print(f"Successfully updated status for {len(update_requests)} rows.")

    # 6. Mark those who were already mentees as "Yes" or "No" in the "Was Passt Mentee" column
    update_requests_already_mentee = []
    for row in rows_was_already_mentee:
        # Convert 1-based index relative to the first entry to be relative to the title row for A1 notation to match the sheets UI
        cell_range = f"Form Responses 1!{sheets.MENTEE_WAS_PAST_MENTEE_COLUMN_LETTER}{row + 1}" 
        update_requests_already_mentee.append({
            "range": cell_range,
            "values": [["Yes"]] # Values must be a list of lists [ [cell_value] ]
        })
    # Construct the full request body
    batch_update_values_request_already_mentee = {
        "valueInputOption": "RAW", # RAW inserts string as-is; USER_ENTERED parses like UI
        "data": update_requests_already_mentee
    }
    # Execute the batch update
    if update_requests_already_mentee:
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=MENTEE_SPREADSHEET_ID,
            body=batch_update_values_request_already_mentee
        ).execute()
        print(f"Successfully updated 'Was Past Mentee' status for {len(update_requests_already_mentee)} rows.") 
    
    #### ---Gmail Notification Implementation--- ####
    ### ---Build Gmail service--- ###
    gmail_service = build("gmail", "v1", credentials=creds)
    ### ---Send Emails to Rejected Applicants--- ###
    for row in rows_to_reject:
        recipient_email = sheets.get_email(mentee_entries[row-1])  # Adjust for 0-based index of mentee_entries
    #     first_name = sheets.get_first_name(mentee_entries[row-1])  # Adjust for 0-based index of mentee_entries
    #     last_name = sheets.get_last_name(mentee_entries[row-1])  # Adjust for 0-based index of mentee_entries
    #     subject = f"[{first_name.upper()} {last_name.upper()}][APPLICATION ERROR][AUTOMATED EMAIL]"
    #     body = (
    #         f"""
    #         Dear {first_name} {last_name},

    #         Thank you for your interest in becoming a mentee. 
    #         This is an automated message regarding your application to participate in the BSE Mentorship Program.
    #         After our system reviewed your application, we could not verify your status as a General Member of BSE. 
    #         This could be due to various reasons:
            
    #         1. You have not submitted the General Member form yet. You must be a General Member to participate.
    #         2. The UID you provided in either your General Member form or Mentee Application form don't match.
    #         3. The first and last names you provided in the General Member form don't match those in your Mentee Application form.
            
    #         In order to be eligible for the Mentorship Program, all of the above must be resolved.
    #         Your application has not been deleted, but will not be considered until the issue is resolved.
    #         You have the ability to edit your responses in the Mentee Application form and General Member form. 
    #         Pleases check to ensure all of the information is correct and consistent.

    #         If you believe this message was sent in error, you may reply to this email to ask for a manual review of your information.


    #         Best regards,
    #         The BSE Team
    #         """
    #     )
        
    #     gmail.send_mentee_is_not_GM(gmail_service, recipient_email, subject, body)
        print(f"Sending email to {recipient_email}...")

    for row in rows_was_already_mentee:
        recipient_email = sheets.get_email(mentee_entries[row-1])  # Adjust for 0-based index of mentee_entries
        print(f"Sending email to {recipient_email} about already being a mentee...")
        # first_name = sheets.get_first_name(mentee_entries[row-1])  # Adjust for 0-based index of mentee_entries
        # last_name = sheets.get_last_name(mentee_entries[row-1])  # Adjust for 0-based index of mentee_entries
        # subject = f"[{first_name.upper()} {last_name.upper()}][APPLICATION REJECTED][AUTOMATED EMAIL]"
        # body = (
        #     f"""
        #     Dear {first_name} {last_name},

        #     Thank you for your interest in becoming a mentee. 
        #     This is an automated message regarding your application to participate in the BSE Mentorship Program.
        #     After our system reviewed your application, noticed that you have already been a mentee before.
        #     Due to limited mentor availability, we are only able to accept applicants who have not previously participated as mentees. 
        #     As a result, we are unable to accept your application for the Mentorship Program at this time. 

        #     If you believe this message was sent in error, you may reply to this email to ask for a manual review of your information.

        #     Best regards,
        #     The BSE Team
        #     """
        # )
        # gmail.send_mentee_is_not_GM(gmail_service, recipient_email, subject, body)
        




def authenticate():
    """ Authenticates and returns the credentials object """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

    
if __name__ == "__main__":
    run()