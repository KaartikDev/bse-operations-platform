from googleapiclient.discovery import build
from utils import sheets
from utils import gmail
from utils import google_authentication

# ID and range of spreadsheet
GM_SPREADSHEET_ID = "1Xngw94j6M21rG-YEQLHbPTnTDtBW9sMhTSky2CXTYdY"
gm_spreadsheet_range = f"Members Jan 2026!A2:{sheets.GM_LAST_COLUMN_LETTER}{sheets.GM_NUMBER_OF_COLUMNS}" # make ranges more dynamic later
GM_SHEET_ID = "286014913"
MENTEE_SPREADSHEET_ID = "1myZZASczHp7fzHchePcb4cVuQHYxOow6YOXAPHcXPHY"
mentee_spreadsheet_range = f"Form Responses 1!A2:{sheets.MENTEE_LAST_COLUMN_LETTER}{sheets.MENTEE_NUMBER_OF_COLUMNS}" # make ranges more dynamic later
MENTEE_SHEET_ID = "829339717"

# Notes: 
# Columns: default spreadsheet starts from A = index 0
# Rows: default spreadsheet starts from 1 = index 0 (row 1 in the spreadsheet UI is the title row, first entry is row 2 which is index 1 for this program)

def run_mentee_checker():
    creds = google_authentication.authenticate()
    service = sheets.create_service(creds)
    sheet = sheets.create_sheet(service)
    gmail_service = build("gmail", "v1", credentials=creds)
    
    ### ---Get and Process Entries--- ###
    mentee_ls = sheets.get_entries(sheet, MENTEE_SPREADSHEET_ID, mentee_spreadsheet_range, "Mentee")
    mentee_entries = sheets.normalize_table(mentee_ls[0], 2)
    GMrawls = sheets.get_entries(sheet, GM_SPREADSHEET_ID, gm_spreadsheet_range, "GM")
    GM_entries = sheets.normalize_table(GMrawls[0], 1)

    all_update_requests = [] # We collect EVERY change here for one batch call

    ### ---Iterate and process through every applicant (Row 2 in Sheets is index 0 in our list)--- ###
    # start=2 because Row 1 is headers, Row 2 is the first applicant
    for index, mentee_entry in enumerate(mentee_entries, start=2):
        UID = mentee_entry[sheets.MENTEE_BSE_ID_COLUMN_INDEX]
        
        # Read the current "Memory" from the spreadsheet
        current_memory = mentee_entry[sheets.MENTEE_NOTIFICATION_STATE_COLUMN_INDEX].strip()

        # Default state
        target_state = "NOT_A_GM" 
        
        for gm in GM_entries:
            if UID == gm[sheets.GM_BSE_ID_COLUMN_INDEX]:
                m_first = sheets.get_first_name(mentee_entry).strip().lower()
                gm_first = sheets.get_first_name(gm).strip().lower()
                m_last = sheets.get_last_name(mentee_entry).strip().lower()
                gm_last = sheets.get_last_name(gm).strip().lower()
                if m_first != gm_first or m_last != gm_last:
                    target_state = "NAME_MISMATCH"
                elif gm[sheets.GM_ALREADY_MENTEE_COLUMN_INDEX].strip().lower() == "yes":
                    target_state = "ALREADY_MENTEE"
                else:
                    target_state = "VERIFIED"
                break

        ### ----Compare Truth vs. Memory--- ###
        if target_state != current_memory:
            # IF WE ARE IN THIS BLOCK, IT MEANS:
                # A) This is the first time the script has ever seen this person
                # OR B) The person edited their form, so their status changed.
            print(f"Updating Row {index}: {current_memory} -> {target_state}")

            #### ---Gmail Notification Implementation--- ####
            # 1. Send the email (this only happens once per change!)
            recipient_email = sheets.get_email(mentee_entry)
            # gmail.send_mentorship_notification(gmail_service, recipient_email, target_state, mentee_entry)            ###########

            # B. Prepare Spreadsheet Updates
            is_verified = "Yes" if target_state == "VERIFIED" else "No"
            was_past_mentee = "Yes" if target_state == "ALREADY_MENTEE" else "No"

            # Update Verification Column
            all_update_requests.append({
                "range": f"Form Responses 1!{sheets.MENTEE_VERIFICATION_COLUMN_LETTER}{index}",
                "values": [[is_verified]]
            })
            # Update Past Mentee Column
            all_update_requests.append({
                "range": f"Form Responses 1!{sheets.MENTEE_WAS_PAST_MENTEE_COLUMN_LETTER}{index}",
                "values": [[was_past_mentee]]
            })
            # Update Memory (Notification State) Column
            all_update_requests.append({
                "range": f"Form Responses 1!{sheets.MENTEE_NOTIFICATION_STATE_COLUMN_LETTER}{index}",
                "values": [[target_state]]
            })
    # 5. Execute all updates in ONE batch call at the end
    if all_update_requests:
        batch_body = {
            "valueInputOption": "RAW",
            "data": all_update_requests
        }
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=MENTEE_SPREADSHEET_ID,
            body=batch_body
        ).execute()
        print(f"Successfully synced {len(all_update_requests)//3} rows.")
    else:
        print("No changes detected. No emails sent.")


if __name__ == "__main__":
    run_mentee_checker()