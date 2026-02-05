# This program is a base checker for general events
# It will check the event's google form spreadsheet with the GM list to find if the entry is a GM. 
# If not, it will send an email to remind them to sign up to be a GM.
from googleapiclient.discovery import build
from utils import sheets
from utils import gmail
from utils import google_authentication
from utils import logonScanner

# form standard
    # C, D, E = First name, last name, ucla email
    # form must be editable after submission 
    # each email should be able to submit only 1 form --> no duplicate entries 


# workflow
# human done
# 1. person creates google form and links it to a spreadsheet range
# 2. person inputs the spreadsheet ID and the sheetID into the function

# program done in while loop
# 3. the program dynamically creates the ranges it'd need
# 4. program creates a new tab called EntryStatuses if it doesn't already exist
# 5. program checks if they're a member
# 7. program checks if the names match
# 8. program sends emails as necessary
# 9. in the new tab, it will put the status of the entry into the first column A and append the respective entry to the right unmodified
# 10. loop again

# create new sheet with entry status
# put entry status as column and copy the rest of the entry to the right of it


# ID and range of spreadsheet
GM_SPREADSHEET_ID = "1ZQjmV6OVpHfB9hiJP9sLValh9cGUA2aOg3fpn6ELHj8"
GM_SHEET_ID = "1892524808"
GM_SHEET_NAME = "Members Jan 2026"

# Notes:
# Columns: default spreadsheet starts from A = index 0
# Rows: default spreadsheet starts from 1 = index 0 (row 1 in the spreadsheet UI is the title row, first entry is row 2 which is index 1 for this program)


def findlastcolnum(service, SPREADSHEET_ID, SHEET_NAME):
    """
    Determine the last column by reading only the header row (row 1).
    This avoids scanning the entire sheet and ensures valid ranges for any sheet name.
    """
    RANGE_NAME = f"{SHEET_NAME}!1:1"  # Header row only
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()
    values = result.get('values', [])
    if not values:
        # No header row found
        return 0
    header = values[0]
    return len(header)

def column_to_letter(col_num):
    """
    Function to convert a column number to a column letter
    """
    letter = ''
    while col_num > 0:
        col_num, remainder = divmod(col_num - 1, 26)
        letter = chr(65 + remainder) + letter
    return letter


def runChecker(SPREADSHEET_ID: str, SHEET_ID: str, SHEET_NAME: str, TYPE: str):
    """
    SHEET_NAME: the name of the sheet tab of the resspective Sheet ID (found at the bottom of the spreadsheet UI)
    TYPE: the type of spreadsheet. Ex. if it's a spreadsheet of mentees, type = mentee. This is not an important parameter. It can be anything
    """
    ### ---Service Creation--- ###
    creds = google_authentication.authenticate()
    service = sheets.create_service(creds)
    sheets_api = sheets.create_sheet(service)
    gmail_service = build("gmail", "v1", credentials=creds)

    ### ---Dynamic Creation/Verification of EntryStatuses Tab--- ###
    # fetch current sheets metadata
    temp = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID,
        fields='sheets(properties(sheetId,title))'
    ).execute()
    metadata_sheets = temp.get('sheets', [])
    target_title = "EntryStatuses"
    target_id = None  # sheet id of the EntryStatuses tab
    # check if the sheet exists
    for sh in metadata_sheets:
        if sh['properties']['title'] == target_title:
            target_id = sh['properties']['sheetId']
            break
    # create only if missing
    if target_id is None:
        request_body = {
            'requests': [{'addSheet': {'properties': {'title': target_title}}}]
        }
        response = service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=request_body
        ).execute()
        target_id = response['replies'][0]['addSheet']['properties']['sheetId']
    print(f"Ready to use Sheet ID: {target_id}")

    ### ---Dynamic Creation of Ranges--- ###
    GM_last_column_number = findlastcolnum(service, GM_SPREADSHEET_ID, GM_SHEET_NAME)
    GM_last_column_letter = column_to_letter(GM_last_column_number)
    spreadsheet_last_column_number = findlastcolnum(service, SPREADSHEET_ID, SHEET_NAME)
    spreadsheet_last_column_letter = column_to_letter(spreadsheet_last_column_number)
    print(f'Number of columns: {spreadsheet_last_column_number}')
    print(f'Last column letter: {spreadsheet_last_column_letter}')

    # Use open-ended row ranges: A2:{last_col_letter} reads all rows starting at row 2 through the last column
    gm_spreadsheet_range = f"{GM_SHEET_NAME}!A2:{GM_last_column_letter}"  # dynamic GM sheet
    spreadsheet_range = f"{SHEET_NAME}!A2:{spreadsheet_last_column_letter}"  # dynamic form sheet

    ### ---Get and Process Entries--- ###
    # Read source entries
    entryls = sheets.get_entries(sheets_api, SPREADSHEET_ID, spreadsheet_range, TYPE)
    normalizedEntries = sheets.normalize_table(entryls[0], 2)

    # Read GM entries
    GMrawls = sheets.get_entries(sheets_api, GM_SPREADSHEET_ID, gm_spreadsheet_range, "GM")
    GM_entries = sheets.normalize_table(GMrawls[0], 1)

    # # Build GM lookup keyed by logon (local-part of email)
    # def extract_login(email: str) -> str:
    #     if not email:
    #         return ""
    #     try:
    #         return email.split('@', 1)[0].strip().lower()
    #     except Exception:
    #         return ""

    # gm_by_login = {}
    # for gm in GM_entries:
    #     gm_email = sheets.get_email(gm)  # column E
    #     login = extract_login(gm_email)
    #     if login:
    #         gm_by_login[login] = gm

    # Read prior statuses (memory) from EntryStatuses column A
    prev_result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="EntryStatuses!A2:A"
    ).execute()
    prev_values = prev_result.get('values', [])
    prev_statuses = [row[0] if row else "" for row in prev_values]

    all_update_requests = []  # Collect updates for EntryStatuses

    # Iterate and process through every applicant; row 2 is index 0 in our list
    for index, entry in enumerate(normalizedEntries, start=2):
        entry_email = sheets.get_email(entry)  # column E
        print(entry_email)

        # Default state
        target_state = "NOT_A_GM"

        for member in GM_entries:
            member_email = sheets.get_email(member)
            # print(member_email)
            if logonScanner.checkLogon(member_email, entry_email) == True:
                first_name = sheets.get_first_name(entry).strip().lower()  # column C
                gm_first = sheets.get_first_name(member).strip().lower()           # column C
                last_name = sheets.get_last_name(entry).strip().lower()    # column D
                gm_last = sheets.get_last_name(member).strip().lower()             # column D
                print(first_name)
                print(gm_first)
                if first_name != gm_first or last_name != gm_last:
                    target_state = "NAME_MISMATCH"
                    print("name mismatch")
                else:
                    target_state = "VERIFIED"
                    print("verified")
        print("next")

        # Compare against previous status stored in EntryStatuses column A
        prev_state = prev_statuses[index - 2] if (index - 2) < len(prev_statuses) else ""
        if target_state != prev_state:
            print(f"Updating Row {index}: {prev_state} -> {target_state}")
            # Send notification once per change (optional)
            gmail.send_event_email(gmail_service, entry_email, target_state, entry, TYPE)           ###########

        # Prepare EntryStatuses updates: A=status, B..=full row
        all_update_requests.append({
            "range": f"EntryStatuses!A{index}",
            "values": [[target_state]]
        })
        all_update_requests.append({
            "range": f"EntryStatuses!B{index}",
            "values": [entry]
        })

    # Execute all updates to EntryStatuses in one batch
    if all_update_requests:
        batch_body = {
            "valueInputOption": "RAW",
            "data": all_update_requests
        }
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=batch_body
        ).execute()
        print(f"Successfully synced {len(all_update_requests)//2} rows.")
    else:
        print("No changes detected. No emails sent.")


if __name__ == "__main__":
    # runChecker("1myZZASczHp7fzHchePcb4cVuQHYxOow6YOXAPHcXPHY", "829339717", "Form Responses 1", "Mentee")
    runChecker("1bJcGFdZnSSlRCgARXxkFcMMMAl4t5T0tCStawPVFFrQ", "689981456", "Copy of Form Responses 1", "Jane Street x BSE Guts++")
