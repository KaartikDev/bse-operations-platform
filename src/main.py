# this is the entry point of the application

# so far the program is structured to work on only 1 cohort at a time. 
# Future versions may want to support multiple cohorts in a dynamic way that doesn't require
# code changes or new scripts to switch between cohorts.

import schedule
import time
from menteeChecker import run_mentee_checker
from checker import runChecker

def main():
    # schedule.every().minute.do(run_mentee_checker)

    #Jane Street Checker
    # schedule.every().minute.do(runChecker("1bJcGFdZnSSlRCgARXxkFcMMMAl4t5T0tCStawPVFFrQ", "1917791920", "Form Responses 1", "Jane Street"))
    schedule.every().minute.do(runChecker("1hMJk9mpSDcma9rFefAB4dTe1Ho_cttq0InDg7TC6b3I", "1640604549", "Form Responses 1", "the Fireside Chat with Senior Spotify Engineer"))

    while True:
        schedule.run_pending()
        time.sleep(1)
# forms should be 1 form per email and editable and copies of responses should be sent to the user


if __name__ == "__main__":
    main()