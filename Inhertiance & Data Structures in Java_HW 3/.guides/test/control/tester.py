import shutil, os, json
import util
import notebook_convert as nbconv


class tester:
    """ This class is responsible for testing submissions and writing to a log location
    with various, language-specific forms of output.
    """

    def __init__(self, manager):
        """ Initialization function, does a lot of setup but nothing actually gets done yet
        """
        self.name = "tester"
        self.test_funcs = {
            "c": self.test_c,
            "java": self.test_java,
            "python": self.test_python,
            "jupyter": self.test_jupyter
        }
        self.manager = manager
        self.abs_path = self.manager.abs_path
        self.define_abs_paths()
        self.test_contents = {}

    def define_abs_paths(self):
        """ Helper to set class variables
        """
        self.workspace_path = "/home/codio/workspace"
        self.guides_path = "{}/.guides".format(self.workspace_path)
        self.submission_path = "{}/submit".format(self.workspace_path)
        self.is_secure = False if '{}/test/'.format(self.guides_path) in self.abs_path else True
        self.current_root = "{}/{}".format(self.guides_path, "secure" if self.is_secure else "test")
        self.manager.log("Current Root: {}\tIs Secure: {}".format(self.current_root, self.is_secure),
                         raising_class=self)

    def test_unit_testing(self):
        """ Parse the unit testing files to confirm whether student completed
        the required number of additional tests
        """

        # Check to make sure that this assignment actually uses unit testing
        if 'unit_testing' not in self.manager.assignment_manifest_contents.keys():
            print("No unit testing in keys")
            return
        requires_unit_testing = False
        for asg_lang in self.manager.assignment_manifest_contents['assignment_overview']['assignment_types']:
            if 'unit_testing' not in self.manager.assignment_manifest_contents['scoring'][asg_lang].keys():
                print("No unit testing in scoring")
                continue
            elif self.manager.assignment_manifest_contents['scoring'][asg_lang]['unit_testing'] > 0:
                requires_unit_testing = True
                print("Unit testing detected")
                continue
        if not requires_unit_testing:
            print("Skipping unit testing")
            return

        # Check each assignment language to figure out which unit testing to grade
        for asg_lang in self.manager.assignment_manifest_contents['assignment_overview']['assignment_types']:
            self.test_contents[asg_lang] = {}
            for file in self.manager.assignment_manifest_contents['unit_testing'][asg_lang]:
                self.test_contents[asg_lang][file] = {}
                contents = util.get_file_contents_as_list("{}/{}".format(self.submission_path, file))
                is_test_case = False
                test_case_name = None
#                 file = ".".join(file.split("/")[-1].split(".")[:-1])
                for line in contents:
                    line = line.strip()

                    # Java-specific parsing
                    if asg_lang == 'java':
                        # Case: beginning of a test
                        if line.startswith("@Test") and not is_test_case:
                            is_test_case = True
                            test_case_name = None
                        # Case: actual test contents
                        elif is_test_case and test_case_name is None:
                            split = line.split(' ')
                            for elt in split:
                                if 'test' in elt.lower():
                                    test_case_name = elt.split('(')[0]
                                    is_test_case = False
                                    self.test_contents[asg_lang][file][test_case_name] = {"asserts": []}
                                    break
                        # Case: scan for asserts
                        elif test_case_name is not None and not is_test_case:
                            if line.startswith("assert"):
                                self.test_contents[asg_lang][file][test_case_name]["asserts"].append(line)

                    # Python-specific parsing
                    elif asg_lang == "python":
                        if line.startswith("def"):
                            split = line.split(' ')
                            for elt in split:
                                if 'test' in elt.lower():
                                    test_case_name = elt.split('(')[0]
                                    self.test_contents[asg_lang][file][test_case_name] = {"asserts": []}
                                    break
                        elif test_case_name is not None:
                            if line.startswith("self.assert"):
                                self.test_contents[asg_lang][file][test_case_name]["asserts"].append(line)

                # Figure out which test cases were actually required
                required = self.manager.assignment_manifest_contents['unit_testing'][asg_lang][file]
                for test_case in self.test_contents[asg_lang][file]:

                    # Make sure that we're actually interested in this one
                    if test_case not in required['min_asserts']:
                        continue
                    
                    this_test = {
                        'provided': required['provided_asserts'][test_case],
                        'required': required['min_asserts'][test_case],
                        'found': len(self.test_contents[asg_lang][file][test_case]['asserts']),
                    }
                    this_test['required_new'] = this_test['required'] - this_test['provided']
                    self.test_contents[asg_lang][file][test_case] = this_test
                    
        return self.test_contents
    

    def test_submission(self):
        """ This determines which test function should be used based on the language being tested. This is
        the function that should be called to actually perform testing
        """
        for lang in self.manager.assignment_manifest_contents['assignment_overview']['assignment_types']:
            self.manager.log("Testing {}".format(lang), raising_class=self)
            try:
                # Grab the appropriate language-specific function, then execute
                fn = self.test_funcs[lang]
                fn("{}/execution-environment/{}".format(self.current_root, lang))
            except Exception as e:
                msg = "Ran into an error while testing {}".format(lang)
                print(msg)
                self.manager.log(msg, e, self)

    def test_c(self, test_env_path):
        ''' This method will clear out the testing environment, copy in the test cases along with the submission,
            then execute the tests using the Aceunit framework
        '''
        # Clear test location for compilation
        util.clear_out_dir(test_env_path, exclude=['src', 'tests', 'Makefile'])
        util.clear_out_dir('{}/src'.format(test_env_path))
        util.clear_out_dir('{}/tests'.format(test_env_path))

        # Copy in the appropriate files (extra credit agnostic)
        dont_copy = []
        dont_copy += self.manager.assignment_manifest_contents['assignment_overview']['ignore_files']
        dont_copy += ['java', 'class', 'py', 'ipynb', 'Makefile']
        util.copy_files_from_dir(self.submission_path, '{}/src'.format(test_env_path), exclude_types=dont_copy)
        util.copy_files_from_dir('{}/test-cases/c'.format(self.current_root), '{}/tests'.format(test_env_path),
                                 exclude_types=['Makefile'])
        util.copy_files_from_dir('{}/test-cases/c'.format(self.current_root), test_env_path, include_types=['Makefile'])

        # If there are extra credit implementations, parse through the test cases
        ec_implementations = self.check_files_for_ec_funcs(
            self.manager.assignment_manifest_contents['assignment_overview'])
        if len(ec_implementations) > 0:
            self.parse_ec_tests(
                '{}/tests'.format(test_env_path),
                ec_implementations)

        files_present, _ = util.get_dir_contents(test_env_path)
        os.chdir(test_env_path)
        os.system('make test 2>&1 | tee -a {}/log_c.txt'.format(self.manager.log_path))
        os.system('mv results_c.xml {}/test_results_c.xml'.format(self.manager.log_path))

    def test_java(self, test_env_path):
        ''' This method will perform actions needed to clear the testing library (test location),
        copy in all test cases, copy in the submission, then execute the test cases for java
        submissions
        '''
        conf_json = json.loads(self.manager.config_contents)

        # Clear test location
        util.clear_out_dir(test_env_path)

        # Copy in the appropriate files (submissions, tests, libraries)
        dont_copy = []
        dont_copy += self.manager.assignment_manifest_contents['assignment_overview']['ignore_files']
        dont_copy += ['py', 'class', 'ipynb']
        util.copy_files_from_dir(self.submission_path, test_env_path, exclude_types=dont_copy, keep_structure=True)

        # Make sure that the tests are copied to the proper directory
        path_modifier = ''
        if 'package_location' in conf_json.keys():
            if conf_json['package_location'] != "":
                path_modifier = conf_json['package_location']
        util.copy_files_from_dir('{}/test-cases/java'.format(self.current_root),
                                 '{}/{}'.format(test_env_path, path_modifier))
        util.copy_files_from_dir('{}/libs'.format(self.workspace_path), test_env_path)

        # Determine relevant jar files
        files_present, _ = util.get_dir_contents(test_env_path)
        jar_files = ''
        for file in files_present:
            if util.get_file_ext(file) == 'jar':
                jar_files += file

        # Check for the config.json overrides; set the compile and run commands
        compile_cmd = ""
        if 'compile_override' in conf_json.keys():
            if conf_json['compile_override'] != "":
                compile_cmd = conf_json['compile_override']
        if compile_cmd == "":
            compile_cmd = 'javac -cp {}:{} {}/*.java'.format(test_env_path, jar_files, test_env_path)
        self.manager.log("Compile command is: {}".format(compile_cmd), raising_class=self)
        run_cmd = """java -jar junit-platform-console-standalone-1.3.2.jar \
            --disable-ansi-colors \
            --classpath="{}:{}:bin" \
            --reports-dir="{}" \
            --scan-class-path 2>&1 | tee -a {}/results_java.txt""".format(test_env_path,
                                                                          jar_files,
                                                                          self.manager.log_path,
                                                                          self.manager.log_path)

        # Compile the submission, then run it
        print(' > Attempting to compile submission')
        os.chdir(test_env_path)
        res = os.system(compile_cmd)
        if res != 0:
            print(" > ERROR: Could not compile submission")
            exit(9)
        else:
            print(" > Successfully compiled")
        print("\n > Running test cases")
        res = os.system(run_cmd)

    def test_python(self, test_env_path):
        ''' This method will perform actions needed to clear the testing library (test location),
        copy in all test cases, copy in the submission, then execute the test cases for python
        submissions
        '''

        # Clear test location
        util.clear_out_dir(test_env_path)

        # Copy in the appropriate files
        dont_copy = []
        dont_copy += self.manager.assignment_manifest_contents['assignment_overview']['ignore_files']
        dont_copy += ['java', 'class', 'ipynb']
        util.copy_files_from_dir(self.submission_path, test_env_path, exclude_types=dont_copy)
        util.copy_files_from_dir('{}/test-cases/python'.format(self.current_root), test_env_path)

        # Execute test cases
        os.chdir(test_env_path)
        os.system(
            'python3 {}/runner.py 2>&1 | tee -a {}/results_python.txt'.format(test_env_path, self.manager.log_path))

    def test_jupyter(self, test_env_path):
        ''' This method will perform actions needed to clear the testing library (test location),
        copy in all test cases, copy in the submission, then execute the test cases for Jupyter NB
        submissions
        '''

        # Clear test location, get submission files to see which need to be converted
        # using runipy
        util.clear_out_dir(test_env_path)

        # Copy in the appropriate files
        dont_copy = []
        dont_copy += self.manager.assignment_manifest_contents['assignment_overview']['ignore_files']
        dont_copy += ['java', 'class', 'py']
        util.copy_files_from_dir(self.submission_path, test_env_path, exclude_types=dont_copy)
        util.copy_files_from_dir('{}/test-cases/jupyter'.format(self.current_root), test_env_path)

        files_present, _ = util.get_dir_contents(test_env_path)

        # Execute each file using runipy, then parse to a .py file for actual testing
        # also copy in all additional files
        for file in files_present:
            infile = '{}/{}'.format(test_env_path, file)

            if file[-6:] == '.ipynb':
                outfile = '{}/{}.py'.format(test_env_path, file.split('.')[0])
                os.system('/home/codio/.local/bin/runipy -o -q {}'.format(infile))
                self.manager.log("About to convert notebook {}".format(infile), raising_class=self)
                try:
                    nbconv.convert_notebook(infile, outfile, self.manager.log_path)
                    self.manager.log("Successfully converted {}".format(infile), raising_class=self)
                except Exception as e:
                    self.manager.log("Error converting {}".format(infile), e, raising_class=self)

        # Execute test cases
        os.chdir(test_env_path)
        os.system(
            'python3 {}/runner.py 2>&1 | tee -a {}/results_jupyter.txt'.format(test_env_path, self.manager.log_path))

    def check_files_for_ec_funcs(self, asg_overview):
        ''' This function will check whether the student attempted any of the extra credit
        implementations. It will then return a dictionary with those that were attempted
        '''
        ec_func_files = asg_overview['extra_credit_functions']
        implementations = {}
        for file in ec_func_files:
            self.manager.log("Looking in {} for extra credit functions".format(file), raising_class=self)
            try:
                submission_file = open('{}/{}'.format(self.submission_path, file), 'r')
                contents = submission_file.read()
                submission_file.close()
                ec_funcs = ec_func_files[file]  # Student function names in student submission file

                for ec_func in ec_funcs:
                    self.manager.log('Searching for function {}'.format(ec_func), raising_class=self)
                    if ec_func not in contents:
                        self.manager.log('Not found', raising_class=self)
                    else:
                        self.manager.log('Found', raising_class=self)
                        if file not in implementations:
                            implementations[file] = ec_func_files[file]
            except IOError as e:
                self.manager.log("Unable to open file: {}".format(file), raising_class=self)
                return []
        return implementations

    def parse_ec_tests(path_to_excec_env, ec_funcs_included):
        ''' This function will go through the extra credit tests and uncomment them
        based on specified regular expression below. It currently is only implemented
        for C language.
        '''
        regex = ['BEGIN_EC_TEST_', 'END_EC_TEST_']

        ec_files_and_funcs = {}
        for student_file in ec_funcs_included:
            for student_func in ec_funcs_included[student_file]:
                ec_file = ec_funcs_included[student_file][student_func]
                for key in ec_file:
                    if key not in ec_files_and_funcs:
                        ec_files_and_funcs[key] = [ec_file[key]]
                    else:
                        ec_files_and_funcs[key].append(ec_file[key])

        # In each test case file that's included, look for the regex indicating the
        # start and end of a conditional test case.
        for file in ec_files_and_funcs:
            parsed_file = []
            ec_file = open('{}/{}'.format(path_to_excec_env, file), 'r').read().split('\n')
            for line in ec_file:
                skip = False
                for expression in regex:
                    if expression in line:
                        split_line = line.replace('/*', '').replace('*/', '').strip().split(expression)
                        test_name = split_line[1]
                        # If it's a test case regex, we're deleting the comment, so set skip flag to be true
                        if test_name in ec_files_and_funcs[file]:
                            skip = True
                # Base case, add the line as is
                if skip:
                    continue
                parsed_file.append(line)

            # Overwrite existing file if there are changes
            if len(parsed_file) != len(ec_file):
                write_to = open('{}/{}'.format(path_to_excec_env, file), 'w+')
                write_to.write('\n'.join(parsed_file))
                write_to.close()

    def check_files_for_required_funcs(self):
        """ This function will confirm that all required functions are present
        for student submission, then return the number of missing (if any)
        """
        missing = 0
        required_funcs_files = self.manager.assignment_manifest_contents['assignment_overview']['required_functions']
        for file in required_funcs_files:
            self.manager.log("Looking in {} for required functions".format(file), raising_class=self)
            try:
                fd = open('{}/{}'.format(self.submission_path, file), 'r')
                contents = fd.read()
                req_funcs = required_funcs_files[file]
                for req_func in req_funcs:
                    self.manager.log('Searching for function {}'.format(req_func), raising_class=self)
                    if req_func not in contents:
                        self.manager.log("Not Found".format(file), raising_class=self)
                        missing += 1
                    else:
                        self.manager.log("Found".format(file), raising_class=self)
                fd.close()
            except IOError as e:
                self.manager.log("Error checking files for required functions", e, self)
                return -1
        return missing

    def check_for_required_files(self):
        """ This function will confirm that all required files are present
        for student submission, then return the number of missing (if any)
        """
        required_files = self.manager.assignment_manifest_contents['assignment_overview']['required_files']
        files_present = []
        self.manager.log("Determining present files", raising_class=self)
        for (_, _, filenames) in os.walk('{}'.format(self.submission_path)):
            files_present.extend(filenames)
            break
        missing = 0
        for req_file in required_files:
            self.manager.log('Searching for {}'.format(req_file), raising_class=self)
            if req_file not in files_present:
                self.manager.log("Not found", raising_class=self)
                missing += 1
            else:
                self.manager.log("Found", raising_class=self)
        return missing