#!/usr/bin/env python3


""" This is the main runner class that can be invoked to kick off autograding for
both student pre-submission testing and final submission testing
"""

from manager import manager
from io import StringIO
import sys, pathlib
sys.path.append('/usr/share/codio/assessments')
from lib.grade import send_grade

def run_test():
    """ Run the standard tests
    """
    m = manager()


if __name__ == "__main__":
    # Determine if this is secure test or not. If secure, then log to results.txt
    # If not, don't log it
    run_location = pathlib.Path(__file__).parent.absolute()
    
    if len(sys.argv) > 1:
        if (sys.argv[1] == 'force'):
            send_grade(int(0))
            sys.exit(0)
    
    try:
        run_test()
    except Exception as e:
        send_grade(int(0))