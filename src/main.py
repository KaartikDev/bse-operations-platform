# this is the entry point of the application

# so far the program is structured to work on only 1 cohort at a time. 
# Future versions may want to support multiple cohorts in a dynamic way that doesn't require
# code changes or new scripts to switch between cohorts.

import schedule
import time
from menteeChecker import run_mentee_checker

def main():
    schedule.every().minute.do(run_mentee_checker)
    while True:
        schedule.run_pending()
        time.sleep(1)
# forms should be 1 form per email and editable and copies of responses should be sent to the user


if __name__ == "__main__":
    main()