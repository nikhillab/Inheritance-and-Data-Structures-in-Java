import json, datetime, pathlib, sys, os
import tester, grader, util, logger, checker

sys.path.append('/usr/share/codio/assessments')


from lib.grade import send_grade

class manager:
    """ This is the manager of all subprocesses that grading entails. Everything is called from here.
    Basic flow:
        1. Initialize any required class variables
        2. Instantiate the logger
        3. Consume configuration (../config/config.json) and assignment_manifest.json (../config/assignment_manifest.json)
        4. Create the tester and grader
        5. Test the submission (will test all languages, files)
        6. Grade the results of the testing
        7. Print out the results to the student
        8. If this is a final submission, send a response via LTI
    """

    # TURN THIS ON FOR VERBOSE DEBUG PRINTING #
    debug_mode = False

    def __init__(self):
        """ Initialization function. Read in all of the required configuration. Optional override for the
        path containing this config
        """
        print("Beginning submission testing")
        self.checkpoint = "Init"
        try:
            # Setup required class variables
            self.name = "manager"
            self.abs_path = str(pathlib.Path(__file__).parent.absolute())
            self.is_secure = False if '/test/' in self.abs_path else True
            self.config_path = "/home/codio/workspace/.guides/{}/config".format("secure" if self.is_secure else "test")

            # Initialize logger
            self.checkpoint = "Logger creation"
            self.configure_logging()
            self.log("\n\n\nKicking off new manager instance and associated tests, grading")

            # Read in configuration, manifest
            self.checkpoint = "Consumption of data"
            self.consume_config()
            self.log("Successfully created manager instance")
            self.consume_assignment_manifest()

            # Initialize checker
            self.checkpoint = "Checker creation"
            self.checker = checker.checker(self)
            if not self.checker.check_required_files():
                self.log("Required files missing. Aborting")
                sys.exit(1)

            # Create tester & grader, then test & grade
            self.checkpoint = "Creating grader, tester"
            self.create_dependent_classes()
            status = "Testing submission"
            self.test_assignment()
            self.checkpoint = "Grading submission"
            int_grade_as_percent = self.grade_assignment()
            status = "Finalizing"
            self.finalize(int_grade_as_percent)
            self.checkpoint = "Complete"
        except Exception as e:
            self.log("Error. Failed in the manager init. Made it to checkpoint: {}".format(self.checkpoint), e)
            print("""
            Something went wrong. Autograding script did not execute. 
            There are many reasons that this could happen, such as syntax 
            errors, missing files that are required, or improperly spelled 
            function/method names. Make sure that all of your function/method 
            names and arguments match the instructions exactly, that you've 
            included all required files and implementations, and that you have 
            all of those files in the submit folder. If you have checked all 
            of those and believe there is an issue in the execution of the 
            tests, please contact course staff.
            """)

    def finalize(self, int_grade_as_percent):
        """ End of life functions - this should run right at the very end of all the execution, will
        send a grade via LTI connection to the host system
        """
        if self.is_secure:
            self.log("Attempting to send grade back via LTI connection")
            res = "UNKNOWN"
            try:
                res = send_grade(min(int(round(int_grade_as_percent)), 100))
                self.log("Response code: {}. Exiting manager.".format(res))
            except Exception as e:
                self.log("Error while sending LTI grade (response code: {})".format(res), e)
        else:
            self.log("Exiting, no need to send LTI connection as not secure test")

    def test_assignment(self):
        """ Go through and test the assignment
        """
        self.log("Beginning tests by invoking tester from manager")
        self.tester.test_unit_testing()
        self.tester.test_submission()
        self.log("Finished testing")

    def grade_assignment(self):
        """ Go through and grade the assignment
        """
        self.log("Beginning grading process using the grader invoked from manager")
        received, possible, int_grade, tests, ungraded_tests = self.grader.grade_submission()
        self.log("Finished grading. Results to follow")
        self.log(json.dumps(tests, indent=2))
        self.log("Ungraded...")
        self.log(json.dumps(ungraded_tests, indent=2))
        self.logger.print_formatted_tests(received, possible, int_grade, tests, ungraded_tests)
        self.log("Received {} / {}, grade: {}".format(received, possible, int_grade))
        return int_grade

    def consume_config(self):
        """ Read in the contents of the config.json file. This will contain all of the required configuration
        elements as a string in the config_contents class variable
        """
        try:
            f = open("{}/config.json".format(self.config_path), "r")
            self.config_contents = f.read()
            f.close()
            self.parse_config_contents()
        except Exception as e:
            msg = "Error while trying to consume the configuration file at {}/config.json".format(self.config_path)
            print(msg)
            self.log(msg, e)

    def consume_assignment_manifest(self):
        """ Load in the assignment manifest as a json object
        """
        try:
            f = open("{}/assignment_manifest.json".format(self.config_path), "r")
            self.assignment_manifest_contents = json.loads(f.read())
            f.close()
        except Exception as e:
            msg = ""
            print(msg)
            self.log(msg, e)

    def parse_config_contents(self):
        """ Turn the config_contents into class variables by parsing the JSON
        """
        try:
            config_lines = json.loads(self.config_contents)
            self.assignment_repo = config_lines['assignment_repo']
            self.assignment_path = config_lines['assignment_path']
            self.is_mooc = config_lines['is_mooc']
        except Exception as e:
            msg = "Error. Could not initialize the manager. Check to make sure you have a valid JSON config file"
            print(msg)
            self.log(msg, e)

    def verify_assignment_config(self):
        """ TODO: Verify the contents, filepaths, etc. """
        pass

    def configure_logging(self):
        """ Create required variables and logging configuration, then instantiate the logger
        """
        self.log_path = "/home/codio/workspace/.guides/logs/{}".format("sec" if self.is_secure else "test")
        self.manager_logger = "{}/manager.log".format(self.log_path)
        util.clear_out_dir(self.log_path, exclude=["manager.log"])
        self.logger = logger.logger(self)

    def log(self, message, error=None, raising_class=None):
        """ Wrapper for logging
        """
        if raising_class is None:
            raising_class = self
        self.logger.log(message, error, raising_class)

    def create_dependent_classes(self):
        """ Instantiate the tester and grader for use in scoring calculations
        """
        self.log("Creating tester")
        self.tester = tester.tester(self)
        self.log("Successfully exited tester!")
        self.log("Creating grader")
        self.grader = grader.grader(self)
        self.log("Successfully exited grader!")


if __name__ == "__main__":
    m = manager()