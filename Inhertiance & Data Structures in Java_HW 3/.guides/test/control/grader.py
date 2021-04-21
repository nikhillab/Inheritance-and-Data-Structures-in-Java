# coding=utf-8
import util, xml_parser, json
from xml.etree import ElementTree


class grader:
    """ This class exists to perform the actual grading functions. It should be isntantiated after
    testing is complete (using the tester) as it relies on file output from tester. That said,
    it is independent of the tester itself and should be governed by the manager.

    Basic flow:
        1. Instantiate the grader
        2. Run grade_submission
    """

    def __init__(self, manager):
        """ Initialization function.
        """
        self.manager = manager
        self.name = "grader"
        self.has_unit_testing = False
        self.test_funcs = {
            "c": (self.retrieve_c_output, None),
            "java": (self.retrieve_java_text_output, None),
            "python": (self.retrieve_python_based_output, "python"),
            "jupyter": (self.retrieve_python_based_output, "jupyter")
        }
        self.tests, self.ungraded_tests = {}, {}
        self.debug_mode = manager.debug_mode

    def grade_submission(self):
        """ This function will grade a given submission. It first registers the tests that languages,
        test files, and test cases that exist as well as their weights, then retrieves the test results
        output to the log folder. It then determines the test result outcomes and calculates a grade.

        return: (received, possible, int_percentage, tests)

                    received:       total points received on all tests aggregated (inclusive of extra credit)
                    possible:       total points possible on all tests aggregated
                    int_percentage: received / possible as an integer multiplied by 100
                    tests:          the full dictionary of all tests
        """
        self.register_all_tests()
        self.determine_test_outcomes()
        self.get_unit_testing_grading()
        return self.calculate_grade()

    def determine_test_outcomes(self):
        """ Go through the test_funcs dictionary, then figure out which function needs to be called.
        This is a helper to reduce needing 4+ if statements
        """
        for lang in self.tests:
            fn, arg = self.test_funcs[lang]
            if arg is None:
                fn()
            else:
                fn(arg)

    def calculate_grade(self):
        """ Calculate the final grade, then return: possible, received, grade (% rounded)
        """
        self.debug("Calculating grade. Current tests:")
        self.debug(json.dumps(self.tests, indent=2))
        possible, received = 0, 0
        for lang in self.tests:
            if not self.tests[lang]['included']:
                continue
            for test_file in self.tests[lang]:
                # Skip the 'included' flag (boolean)
                if test_file == 'included':
                    continue
                for test_case in self.tests[lang][test_file]:
                    test_case = self.tests[lang][test_file][test_case]
                    if 'extra_credit' not in test_case.keys():
                        possible += float(test_case['weight'])
                    elif not test_case['extra_credit']:
                        possible += float(test_case['weight'])
                    received += float(test_case['weight']) if test_case['passed'] else 0
                    if 'partial' in test_case.keys():
                        received += test_case['partial']
        return received, possible, int(round((received / possible) * 100)), self.tests, self.ungraded_tests

    def register_all_tests(self):
        """ Add all of the possible test files, cases to the self.tests dictionary
        """
        # Grab the languages to be included
        for lang in self.manager.assignment_manifest_contents['assignment_overview']['assignment_types']:
            self.tests[lang] = {"included": True}
            self.ungraded_tests[lang] = {"included": True}
        # Grab the test files and test cases
        self.debug("Registering tests")
        self.register_all_tests_helper()
        # Grab the extra credit, if available
        self.debug("Registering EC")
        self.register_all_tests_helper(ec=True)

    def register_all_tests_helper(self, ec=False):
        """ Helper function to remove duplicate code; only difference between EC and standard scoring
        is name, structure is same
        """
        contents = self.manager.assignment_manifest_contents['scoring']
        if ec:
            contents = self.manager.assignment_manifest_contents['extra_credit']
        for lang in contents:
            self.debug("Finding all tests for {} language".format(lang))
            test_files = contents[lang]
            self.debug("Found all files: {}".format(json.dumps(test_files, indent=2)))
            
            # Go through all non-unit testing files first
            for file in test_files:
                self.debug("Looking specifically at {}".format(file))
                if file == 'unit_testing':
                    self.has_unit_testing = True
                    continue
                if file not in self.tests[lang].keys():
                    self.tests[lang][file] = {}

                test_cases = test_files[file]
                self.debug("Now looking at test cases: {}".format(test_cases))
                for test_case in test_cases:
                    self.debug("Adding test case: {}".format(test_case))
                    self.tests[lang][file][test_case] = {
                        "weight": test_cases[test_case],
                        "passed": False,
                        "message": None,
                        "extra_credit": ec,
                        "performed": False
                    }

    def get_unit_testing_grading(self):
        # Then go through all unit testing
        if self.has_unit_testing:
            total_tests = {}
            test_contents = self.manager.tester.test_contents
            if len(test_contents) > 0:
                for lang in test_contents:
                    total_tests[lang] = 0
                    for file in test_contents[lang]:
                        if 'unit_testing' not in self.tests[lang].keys():
                            self.tests[lang]['unit_testing'] = {}

                        # Score based on individual passing test method
                        for tc in test_contents[lang][file]:
                            temp_fname = ''.join(file.split('/')[-1].split('.')[:-1])
                            fail_type = ''
                            if 'found' not in test_contents[lang][file][tc] or 'required' not in test_contents[lang][file][tc]:
                                continue
                            if not self.tests[lang][temp_fname][tc]['passed']:
                                fail_type += 'Test method fails'
                            if test_contents[lang][file][tc]['found'] < test_contents[lang][file][tc]['required']:
                                if len(fail_type) == 0:
                                    fail_type = 'Test method passes, but required {} total asserts but found {} ({} provided)'.format(
                                        test_contents[lang][file][tc]['required'],
                                        test_contents[lang][file][tc]['found'],
                                        test_contents[lang][file][tc]['provided']
                                    )
                                else:
                                    fail_type += ' & required {} total asserts but found {} ({} provided)'.format(
                                        test_contents[lang][file][tc]['required'],
                                        test_contents[lang][file][tc]['found'],
                                        test_contents[lang][file][tc]['provided']
                                    )

                            self.tests[lang]['unit_testing']['{}.{}'.format(temp_fname, tc)] = {
                                'weight': 1,
                                'passed': len(fail_type) == 0,
                                'message': None if len(fail_type) == 0 else fail_type,
                                'extra_credit': False,
                                'performed': True
                            }
                            total_tests[lang] += 1

                for lang in self.tests:
                    for tc in self.tests[lang]['unit_testing']:
                        self.tests[lang]['unit_testing'][tc]['weight'] = \
                            self.manager.assignment_manifest_contents['scoring'][lang]['unit_testing'] / total_tests[
                                lang]


    def retrieve_python_based_output(self, output_lang):
        """ This method will go out and retrieve the output for python classes
        autograding
        """
        self.debug("Retrieving python results")
        contents = util.get_file_contents_as_list('{}/results_{}.txt'.format(self.manager.log_path, output_lang))
        test_lang, test_class, test_case, tc = output_lang, None, None, None
        active_test, active_message = False, False
        break_counter = 0
        self.debug("Found {} records in file converted to list".format(len(contents)))
        for line in contents:
            line = line.strip()
            line = line.split(' ')
            # Empty line checking
            if len(line) == 0:
                continue
            # Test case result parsing
            elif not active_test and line[0][0:4] == 'test':
                test_case = line[0]
                line[1] = line[1].split('.')
                test_class = line[1][0].strip().replace('(', '')
                self.debug("Trying to retrieve test case. Lang: {}\tClass: {}\tCase: {}".format(test_lang, test_class,
                                                                                                test_case))
                self.debug("Tests look like this:")
                self.debug(json.dumps(self.tests, indent=2))
                tc = None
                try:
                    tc = self.tests[test_lang][test_class][test_case]
                    if len(line) > 2:
                        tc['message'] = line[len(line) - 1]
                        tc['passed'] = tc['message'] == 'ok'
                        active_test = False
                        tc['performed'] = True
                    else:
                        active_test = True
                except KeyError as e:
                    self.debug("Found a test that appears not to exist. Adding to ungraded")
                    if test_class not in self.ungraded_tests[test_lang].keys():
                        self.ungraded_tests[test_lang][test_class] = {}
                    if test_case not in self.ungraded_tests[test_lang][test_class].keys():
                        self.ungraded_tests[test_lang][test_class][test_case] = {}
                    tc = self.ungraded_tests[test_lang][test_class][test_case]
                    if len(line) > 2:
                        tc['message'] = line[len(line) - 1]
                        tc['passed'] = tc['message'] == 'ok'
                        active_test = False
                        tc['performed'] = True
                        tc['weight'] = 0
                    else:
                        active_test = True
            elif active_test:
                tc['message'] = line[len(line) - 1]
                tc['passed'] = tc['message'] == 'ok'
                tc['performed'] = True
                active_test = False
            # Message parsing
            elif line[0][0:5] == '=====':
                active_message = True
                test_class, test_case, tc = None, None, None
                break_counter = 0
            elif active_message:
                if line[0][0:5] == 'FAIL:':
                    test_case = line[1]
                    line[2] = line[2].split('.')
                    test_class = line[2][0].strip().replace('(', '')
                    tc = self.tests[test_lang][test_class][test_case]
                elif tc is not None:
                    if line[0][0:5] == '-----':
                        if break_counter >= 1:
                            active_message = False
                            test_class, test_case, tc = None, None, None
                            break_counter = 0
                        else:
                            break_counter += 1
                    else:
                        tc['message'] += '\n{}'.format(' '.join(line))
                        tc['performed'] = True

    def retrieve_java_text_output(self):
        logpath = self.manager.log_path
        filename = "results_java.txt"
        SUCCESS, FAILURE = "✔", "✘"
        self.manager.log("Trying to retrieve text version of java output", raising_class=self)
        contents = util.get_file_contents_as_list("{}/{}".format(logpath, filename))
        current_class = 'n/a'

        # Check each line
        self.manager.log("Found {} lines in text-output".format(len(contents)), raising_class=self)
        for line in contents:
            # Ignore mostly-blank or blank lines
            if len(line) < 3:
                continue
            else:
                try:
                    line = line.split('─')
                    if len(line) < 2:
                        continue
                    line = line[1].strip()
                    line = line.split(' ')
                    self.manager.log("Examining line: {}".format(' '.join(line)), raising_class=self)

                    # Bool values to figure out what we're doing here...
                    is_test = '()' in line[0]
                    is_junit_declaration = 'JUnit' in line[0]
                    is_class = not (is_test or is_junit_declaration)
                    self.manager.log("Junit Garbage: {}\tClass: {}\tTest: {}".format(
                        is_junit_declaration,
                        is_class,
                        is_test,
                        raising_class=self))

                    # Set class if it is one
                    if is_class:
                        current_class = line[0]
                        self.manager.log("Determined this is class: {}".format(current_class), raising_class=self)
                    # Set test values
                    elif is_test:
                        self.manager.log("Determined this is test: {}".format(line[0]), raising_class=self)
                        passed = line[1] == SUCCESS
                        msg = None
                        if not passed:
                            msg = " ".join(line[2:])
                        test_name = line[0].split('(')[0]
                        if current_class not in self.tests['java']:
                            self.manager.log("Adding new test class; not in list\t[{}]".format(current_class),
                                             raising_class=self)
                            self.tests['java'][current_class] = {}
                        if test_name not in self.tests['java'][current_class]:
                            self.tests['java'][current_class][test_name] = {
                                "passed": False,
                                "message": None,
                                "performed": True,
                                "weight": 0,
                                "extra_credit": False
                            }

                        tc = self.tests['java'][current_class][test_name]
                        self.manager.log("TC pre-update: {}".format(json.dumps(tc, indent=2)), raising_class=self)
                        tc['passed'] = passed
                        tc['message'] = msg
                        tc['performed'] = True
                        self.manager.log("TC post-update: {}".format(json.dumps(tc, indent=2)), raising_class=self)

                    else:
                        continue

                except Exception as e:
                    self.manager.log("Hit an error while trying to parse. Could be dummy line", e, raising_class=self)

    def retrieve_java_output(self):
        """
        Read both the JUnit4 and JUnit5 test reports and extract the
        number of achieved points, number of passed and failed tests
        and the error messages from the failed tests.
        """
        REPORT_FILES = [
            'TEST-junit-jupiter.xml',
            'TEST-junit-vintage.xml',
        ]

        ## Refactored due to XML issues
        self.manager.log("Retrieving java output", raising_class=self)
        for filename in REPORT_FILES:
            # Try standard approach
            self.manager.log("Looking for {}".format(filename), raising_class=self)
            try:
                test_lang = 'java'
                tree = ElementTree.parse('{}/{}'.format(self.manager.log_path, filename)).getroot()
                self.manager.log("Found. Loaded into tree: {}".format(tree), raising_class=self)
                for t in tree.findall('testcase'):
                    self.manager.log("Test case is: {}".format(t), raising_class=self)
                    test_class = t.get('classname')
                    if '$' in test_class:
                        test_class = test_class.split('$')[0]
                    self.log("Test class: {}".format(test_class))
                    if test_class not in self.tests[test_lang]:
                        self.log("Continuing...")
                        continue
                    test_case = t.get('name').replace('()', '')
                    self.log("Test case name: {}".format(test_case))
                    fail = t.find('failure')
                    error = t.find('error')
                    failure = fail if fail is not None else error
                    # Update the tests structure with the passed status, message
                    tc = self.tests[test_lang][test_class][test_case]
                    tc['passed'] = failure is None
                    tc['message'] = 'ok' if tc['passed'] else '{}:\n{}'.format(
                        failure.get('type'),
                        failure.get('message'),
                    )
                    tc['performed'] = True

            # If standard XML parsing doesn't work...
            except Exception as e:
                self.manager.log("Hit the exception. Parsing with alternate method", raising_class=self)
                path_to_xml = '{}/{}'.format(self.manager.log_path, filename)
                xml_parser.get_java_results(path_to_xml, self.tests)
                self.manager.log("Tests currently look like: {}".format(self.tests), raising_class=self)

    def retrieve_c_output(self):
        """
        Read the XML doc that is produced by the Check framework (stored in log folder),
        parse it for test results
        """
        REPORT_FILES = [
            'test_results_c.xml',
        ]
        test_lang = 'c'

        for filename in REPORT_FILES:
            tree = ElementTree.parse('{}/{}'.format(self.manager.log_path, filename))
            root = tree.getroot()
            for child in root:
                if 'suite' in child.tag:
                    for gchild in child:
                        if 'result' not in gchild.attrib:
                            continue
                        result = gchild.attrib['result']
                        test_class, test_case, message = None, None, None
                        for ggchild in gchild:
                            tag = ggchild.tag.title().split('}')[1]
                            if tag == 'Id':
                                test_case = ggchild.text
                            elif tag == 'Fn':
                                test_class = ggchild.text.split('.')[0]
                            elif tag == 'Message':
                                message = ggchild.text
                        tc = self.tests[test_lang][test_class][test_case]
                        tc['passed'] = result == 'success'
                        tc['message'] = 'ok' if tc['passed'] else '{}: {}'.format(result, message)
                        tc['performed'] = True

    def debug(self, msg):
        if self.debug_mode:
            print(msg)