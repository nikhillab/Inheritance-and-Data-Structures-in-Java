import util, traceback


class logger:
    """ This class is responsible for most of the communication to the student and logging for
    debugging purposes
    """

    def __init__(self, manager):
        """ Initialization function, not much to see here
        """
        self.manager = manager
        self.name = "logger"

    def print_formatted_tests(self, received, possible, percent_int, tests, ungraded_tests):
        """ This is the basic 'pretty print' function, will return color coded output
        on student test submission, but strips that out for final submission as it makes
        the text come through in a weird way
        """

        # Initial notification block
        msg = "Beginning formatted test printing"
        self.log(msg)
        msg = "{}\n\n\n=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=\n".format(
            util.bcolors.OKBLUE if not self.manager.is_secure else "")
        msg += "=*=*=*=*=*=*=*=*=*=*= {}YOUR AUTOGRADING RESULTS BELOW {}*=*=*=*=*=*=*=*=*=*=*=*=*=*=\n".format(
            util.bcolors.OKGREEN if not self.manager.is_secure else "",
            util.bcolors.OKBLUE if not self.manager.is_secure else "")
        msg += "=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*={}".format(
            util.bcolors.ENDC if not self.manager.is_secure else "")
        msg += "\n\nFor additional details about any error(s), check the output above containing the full stack trace"
        print(msg)

        # Jump to the helper
        self.print_formatted_tests_helper(tests, True)
        self.print_formatted_tests_helper(ungraded_tests, False)

        # If this is the final submission or a MOOC, print out a grade
        if self.manager.is_secure or self.manager.is_mooc:
            self.print_percent_grade(received, possible, percent_int)

    def print_formatted_tests_helper(self, tests, graded):
        """ Instead of writing two functions to do the same thing, this one will print both graded and
        ungraded test results
        """
        if tests is None:
            return
        # Print each test in each language
        for lang in tests:
            if len(tests[lang]) == 0:
                continue
            msg = "{}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{}\n".format(
                util.bcolors.OKBLUE, util.bcolors.ENDC)
            msg += "Results for {}{}{}\n".format(
                util.bcolors.OKGREEN, lang, util.bcolors.ENDC)
            self.log(msg)
            print("\n\n{}".format(msg))

            # List out the file in which the test appears
            for test_file in tests[lang]:
                if test_file == 'included':
                    continue
                msg = "\n\tTest file: {}{}{}".format(
                    util.bcolors.OKGREEN, test_file, util.bcolors.ENDC)
                self.log(msg)
                print(msg)

                # List the test cases below each file in the fashion of:
                # > +1/1 pts [PASS]    test_case_1
                # > +0/1 pts [FAIL]    test_case_2
                for test_case in tests[lang][test_file]:
                    t = tests[lang][test_file][test_case]
                    if not t['performed']:
                        continue

                    received = t['weight'] if t['passed'] else 0
                    if 'partial' in t.keys():
                        received = t['partial']
                    msg = "\t[{}] > +{}/{} pts   {}{}{}".format(
                        "{}PASS{}".format(
                            util.bcolors.OKBLUE if not self.manager.is_secure else "",
                            util.bcolors.ENDC if not self.manager.is_secure else "")
                        if t['passed'] else "{}FAIL{}".format(
                            util.bcolors.FAIL if not self.manager.is_secure else "",
                            util.bcolors.ENDC if not self.manager.is_secure else ""),
                        received,
                        t['weight'],
                        util.bcolors.OKGREEN if not self.manager.is_secure else "",
                        test_case,
                        util.bcolors.ENDC if not self.manager.is_secure else "")
                    if not t['passed']:
                        if t['message'] is not None:
                            msg += ' => {}'.format(t['message'][:min(len(t['message']), 100)])
                        else:
                            msg += ' => n/a'

                    self.log(msg)
                    print(msg)

    def print_percent_grade(self, received, possible, percent_int):
        """ Print out the grade as a %, with test failures shown as fraction.
        This should be used if the script has run in secure mode and all tests
        are included. It will be confusing if this is shown to students when they
        run their available tests, but hidden tests run after the fact as the
        percentage won't match
        """
        msg = "{}\n\n=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*={}\n".format(
            util.bcolors.OKBLUE if not self.manager.is_secure else "",
            util.bcolors.ENDC if not self.manager.is_secure else "")
        msg += "Final score: {}{}% ({}/{} pts){}\n\n".format(
            util.bcolors.OKGREEN if not self.manager.is_secure else "",
            percent_int,
            received,
            possible,
            util.bcolors.ENDC if not self.manager.is_secure else "")
        self.log(msg)
        print(msg)

    def log(self, message, error=None, raising_class=None):
        """ Simple logging function
        """
        f = open(self.manager.manager_logger, 'a+')

        if raising_class is None:
            raising_class = self

        to_write = '{} > {}:\t{}\n'.format(
            util.get_datetime(),
            raising_class.name,
            message)
        f.write(to_write)
        if self.manager.debug_mode:
            print(to_write, end='')
        if error is not None:
            to_write = '\t{}\n'.format(error)
            to_write += '\t{}\n'.format(traceback.format_exc())
            f.write(to_write)
            if self.manager.debug_mode:
                print(to_write, end='')
        f.close()



