# this is the entry point of the application

# so far the program is structured to work on only 1 cohort at a time. 
# Future versions may want to support multiple cohorts in a dynamic way that doesn't require
# code changes or new scripts to switch between cohorts.

def main():
    print("Hello, World!")
    # work flow:
    # 1. Authenticate and connect to Google Sheets API
    # 2. Fetch the mentee application data from the Google Sheet
    # 3. Process the data to verify mentee applications
    # 4. Send notification emails to applicants using Gmail API
    # 

# forms should be 1 form per email and editable and copies of responses should be sent to the user


if __name__ == "__main__":
    main()