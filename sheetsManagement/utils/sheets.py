from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Mapping Spreadsheet Columns
MENTEE__NUMBER_OF_COLUMNS = 13   # Total number of columns in the mentee spreadsheet
MENTEE_LAST_COLUMN_LETTER = "M" # Last column letter in Mentee sheet
MENTEE_EMAIL_COLUMN_INDEX = 1   # "B" column in Mentee sheet
MENTEE_FIRST_NAME_COLUMN_INDEX = 2 # "C" column in Mentee sheet
MENTEE_LAST_NAME_COLUMN_INDEX = 3 # "D" column in Mentee sheet
MENTEE_BSE_ID_COLUMN_INDEX = 5  # "F" column in Mentee sheet
MENTEE_VERIFICATION_COLUMN_LETTER = "L"
MENTEE_VERIFICATION_COLUMN_INDEX = 11 # "L" column in Mentee sheet
MENTEE_WAS_PAST_MENTEE_COLUMN_LETTER = "M"
MENTEE_WAS_PAST_MENTEE_COLUMN_INDEX = 12 # "M" column in Mentee sheet

ALUMNI_NUMBER_OF_COLUMNS = 6    # Total number of columns in the alumni spreadsheet

GM_NUMBER_OF_COLUMNS = 18       # Total number of columns in the GM spreadsheet
GM_LAST_COLUMN_LETTER = "R"   # Last column letter in GM sheet
GM_BSE_ID_COLUMN_INDEX = 16     # "Q" column in GM sheet
GM_ALREADY_MENTEE_COLUMN_INDEX = 17 # "R" column in GM sheet

def create_service(CREDS):
    """ Creates and returns the service object """
    print("Building service...")
    try:
        service = build("sheets", "v4", credentials=CREDS)
        print("Service built successfully.")
        return service
    except HttpError as err:
        print(err)

def create_sheet(SERVICE):
    """ Creates and returns the Sheets object """
    sheet = SERVICE.spreadsheets()
    return sheet

def get_entries(SHEET,SPREADHSEET_ID:str, SPREADSHEET_RANGE:str, TYPE:str = ""):
    """
    Also gets the # of rows and columns.
    Returns: [VALUES, num_rows]
    """
    print(f"Fetching {TYPE} entries...")
    ls = []
    result = (
            SHEET.values()
            .get(spreadsheetId=SPREADHSEET_ID, range=SPREADSHEET_RANGE)
            .execute()
        )
    values = result.get("values", [])
    if not values:
        print("No data found.")
        return
    ls.append(values)
    ls.append(get_num_rows(values))
    print(f"{TYPE} entries fetched successfully.")
    return ls

def get_num_rows(VALUES):
    """ 
    Returns the number of rows.
    The number of rows excludes the title row 
    """
    num_rows = len(VALUES)
    return num_rows

def normalize_table(VALUES, SHEET_TYPE:int):
    """
    Ensures all rows have the same number of columns by filling missing values with empty strings that == False in boolean context
    SHEEET_TYPE: 1 = GM, 2 = MENTEE, 3 = ALUMNI
    """
    expected_cols = 0
    if SHEET_TYPE == 1:
        expected_cols = GM_NUMBER_OF_COLUMNS
    elif SHEET_TYPE == 2:
        expected_cols = MENTEE__NUMBER_OF_COLUMNS
    elif SHEET_TYPE == 3:
        expected_cols = ALUMNI_NUMBER_OF_COLUMNS

    for row in VALUES:
        if len(row) < expected_cols:
            row += [""]
    return VALUES
    
def verify_applicant(SPREADSHEET_ID:str, ROW_INDEX:int, SERVICE):
    """ 
    Writes a 'Verified' status to the specified cell in the spreadsheet.
    This action is not dynamic, so it will need to be modified or updated to match the current spreadsheet schema
    everything in the program is relative to the first entry/row below the title row (that will be row 1)
    although the title row is row 1 on the spreadsheet UI, this program will treat is as row 0.
    """
    cell_to_update = f"{MENTEE_VERIFICATION_COLUMN_LETTER}{ROW_INDEX+1}" 
    # no need to subtract to take into account the title row since the cell reference is direct
    value_range_body = {
        "values": [
            ["Verified"] # Values must be in a nested list [ [row1], [row2] ]
        ]
    }
    SERVICE.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=cell_to_update,
        valueInputOption="RAW",
        body=value_range_body
    ).execute()

def mark_as_not_gm(SPREADSHEET_ID:str, ROW_INDEX:int, SERVICE):
    """ 
    Marks the applicant as not a GM in the specified cell in the spreadsheet.
    This action is not dynamic, so it will need to be modified or updated to match the current spreadsheet schema
    everything in the program is relative to the first entry/row below the title row (that will be row 1)
    although the title row is row 1 on the spreadsheet UI, this program will treat is as row 0.
    """
    cell_to_update = f"{MENTEE_VERIFICATION_COLUMN_LETTER}{ROW_INDEX+1}" 
    # no need to subtract to take into account the title row since the cell reference is direct
    value_range_body = {
        "values": [
            ["No"] # Values must be in a nested list [ [row1], [row2] ]
        ]
    }
    SERVICE.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=cell_to_update,
        valueInputOption="RAW",
        body=value_range_body
    ).execute()

def check_is_verified(ENTRY):
    """
    Checks if the applicant is verified based on the verification column
    """
    verification_status = ENTRY[MENTEE_VERIFICATION_COLUMN_INDEX]  
    return verification_status.strip().lower() == "verified"

def verify_with_GM():
    """
    Placeholder for function to verify with GM Sheet.
    """
    pass

def get_first_name(ENTRY):
    """
    Returns the first name from the entry in lowercase.
    Assumes first name is in column C (index 2).
    """
    return ENTRY[MENTEE_FIRST_NAME_COLUMN_INDEX].strip().lower()
def get_last_name(ENTRY):
    """
    Returns the last name from the entry in lowercase.
    Assumes last name is in column D (index 3).
    """
    return ENTRY[MENTEE_LAST_NAME_COLUMN_INDEX].strip().lower()
def get_email(ENTRY):
    """
    Returns the email from the entry.
    Assumes email is in column E (index 4).
    """
    return ENTRY[MENTEE_EMAIL_COLUMN_INDEX].strip()
    
    