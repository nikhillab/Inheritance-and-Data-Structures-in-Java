import os, shutil, datetime, json, sys, pathlib

""" Helper utility class containing various functions for use across all other classes
"""

def clear_out_dir(path_to_dir, exclude=[]):
    """ This method will remove all files and folders in a path
    """
    current_files, current_dirs = get_dir_contents(path_to_dir)

    # File removal
    for direc in current_dirs:
        if direc not in exclude:
            shutil.rmtree('{}/{}'.format(path_to_dir, direc), ignore_errors=True)
    for file in current_files:
        if file == '.gitignore':
            continue
        if file not in exclude:
            os.remove('{}/{}'.format(path_to_dir, file))


def get_dir_contents(path_to_dir):
    """ This method will return all files and directories in a path as a tuple of lists
    """
    current_files, current_dirs = [], []
    for (_, dirnames, filenames) in os.walk('{}'.format(path_to_dir)):
        current_files.extend(filenames)
        current_dirs.extend(dirnames)
        break
    return current_files, current_dirs


def find_files_recursive(path_to_dir, prefix='', output=[]):
    current_files, current_dirs = get_dir_contents(path_to_dir)
    for direc in current_dirs:
        next_prefix = '{}/{}'.format(prefix, direc) if prefix != '' else direc
        find_files_recursive('{}/{}'.format(path_to_dir, direc), prefix=next_prefix, output=output)
        
    for cfile in current_files:
        filename = '{}/{}'.format(prefix, cfile) if prefix != '' else cfile
        output += [filename]
    
    return output


def get_datetime():
    """ Helper to get formatted date time
    """
    now = datetime.datetime.now
    tz = datetime.timezone(-datetime.timedelta(hours=4))
    time = now(tz=tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    return '[{}]'.format(time)


def get_file_ext(filename):
    """ Return the file extension of a filename passed in
    """
    f = filename.split('.')
    return f[len(f) - 1]


def copy_files_from_dir(source_dir, dest_dir, include_types=[], exclude_types=[], keep_structure=False):
    """ This method will copy all files in a source folder to a destination folder.
    Anything specified in include types (file extensions) will be copied. If blank,
    all will be copied, less any exclude types.
    
    Added recursive functionality on keep_structure
    """
    current_files, current_dirs = get_dir_contents(source_dir)
    to_copy = []
    
    if not os.path.exists(dest_dir):
        try:
            os.mkdir(dest_dir)
        except Exception as e:
            print("ERROR Creating new directory: {}".format(dest_dir))
        
    for file in current_files:
        if len(include_types) == 0 and len(exclude_types) == 0:
            to_copy = current_files + current_dirs
            break
        elif len(include_types) > 0:
            if get_file_ext(file) in include_types:
                to_copy.append(file)
        else:
            if get_file_ext(file) not in exclude_types and file not in exclude_types:
                to_copy.append(file)
    for elt in to_copy:
        os.system('cp {}/{} {}'.format(source_dir, elt, dest_dir))
    
    if keep_structure and len(current_dirs) > 0:
        for direc in current_dirs:
            copy_files_from_dir('{}/{}'.format(source_dir, direc), '{}/{}'.format(dest_dir, direc), include_types, exclude_types, keep_structure)
        
        
def get_file_contents_as_list(path):
    ''' This function will retrieve a file and return it as a list
    '''
    if not os.path.exists(path):
        return []
    file = open(path, 'r')
    contents = file.read().split('\n')
    file.close()
    return contents


def generate_blank_assignment_manifest():
    output = """
    {
      "assignment_overview": {
        "assignment_types": ["jupyter", "python"],
        "required_files": [],
        "ignore_files": [],
        "required_functions": {},
        "extra_credit_functions": {},
      "extra_credit": {
        "java": {},
        "jupyter": {},
        "python": {},
        "c": {}
      },
      "scoring": {
        "java": {},
        "jupyter": {},
        "python": {},
        "c": {}
        }
      }
    }
    """
#     print(output)
    return output
    
    
def generate_example_assignment_manifest():
    output = """
    {
      "assignment_overview": {
        "assignment_types": [
          "c", "java", "jupyter", "python"
        ],
        "required_files": [
          "my_string.c",
          "my_string.h"
        ],
        "ignore_files": ["lcc", "cpp", "rcc"],
        "required_functions": {
            "my_string.c": [
                "my_strcmp",
                "my_strcmp2",
                "my_strcat",
                "my_strcat2",
                "my_strccase",
                "my_strrev",
                "my_strchr",
                "my_strchr2",
                "my_strcpy",
                "my_strcpy2"
          ]
        },
        "extra_credit_functions": {
            "my_string.c": {
                "my_strtok": { 
                    "check_test_cases.c" : "EC_testStrtok" 
                }
            }
        }
      },
      "extra_credit": {
        "java": {},
        "jupyter": {},
        "python": {},
        "c": {
          "check_test_cases": {
            "EC_testStrtok": 5
          }
        }
      },
      "scoring": {
        "java": {},
        "jupyter": {},
        "python": {},
        "c": {
          "check_test_cases": {
            "testStrCatHelloWorld": 1
          }
        }
      }
    }
    """
#     print(output)
    return output
    
    
def parse_tests(base_path, asg_man_path):
    ''' This function will go through and parse each test case so that it can be copied into the assignment manifest
    '''
    std_output, ec_output = {}, {}
    test_cases_path = '{}/test-env/test-cases'.format(base_path)

    _, direcs = get_dir_contents(test_cases_path)
    for direc in direcs:
        std_output[direc], ec_output[direc] = {}, {}
        files, sub_direcs = get_dir_contents('{}/{}'.format(test_cases_path, direc))
        
        for file in files:
            if file == '.gitignore' or get_file_ext(file) == "txt":
                continue
            func = None
            if direc == 'jupyter':
                if get_file_ext(file) != 'py' or file == 'runner.py':
                    continue
                func = parse_jupyter_tests
            elif direc == 'python':
                if get_file_ext(file) != 'py' or file == 'runner.py':
                    continue
                func = parse_python_tests
            elif direc == 'java':
                if get_file_ext(file) == 'jar':
                    continue
                func = parse_java_tests
            elif direc == 'c':
                func = parse_c_tests
            else:
                continue
            std_output[direc][file.split('.')[0]], ec_output[direc][file.split('.')[0]] = func('{}/{}/{}'.format(test_cases_path, direc, file))
                    
#     print(json.dumps(std_output, indent=2))
#     print(json.dumps(ec_output, indent=2))
    
    # Write it to the assignment manifest
    f = open(asg_man_path, 'r')
    contents = json.loads(f.read())
    f.close()
    
    total_output = {}
    for key in contents.keys():
        if key != 'scoring':
            total_output[key] = contents[key]
            
    total_output['scoring'], total_output['extra_credit'] = std_output, ec_output
    total_output['unit_testing'] = std_output

    f = open(asg_man_path, 'w+')
    f.write(json.dumps(total_output, indent=2))
    print(json.dumps(total_output, indent=2))
    f.close()
        
    
def parse_jupyter_tests(filepath):
    ''' Jupyter and python use same unittest framework, same parsing
    '''
    return parse_python_tests(filepath)
    
    
def parse_c_tests(filepath):
    ''' This function will parse out test methods from the python unittest framework
    '''
    f = open(filepath, 'r')
    contents = f.read()
    f.close()
    contents = contents.split('\n')
    filename = filepath.split('/')[-1].split('.')[0]
    std_output, ec_output = {filename: {}}, {filename: {}}
    
    for line in contents:
        if 'tcase_add_test' in line:
            testname = line.split('(')[1].split(')')[0].split(',')[1].strip()
            if testname[:3] == 'EC_':
                ec_output[filename][testname] = 1
            else:
                std_output[filename][testname] = 1
    return std_output[filename], ec_output[filename]


def parse_python_tests(filepath):
    ''' This function will parse out test methods from the python unittest framework
    '''
    f = open(filepath, 'r')
    contents = f.read()
    f.close()
    contents = contents.split('\n')
    filename = filepath.split('/')[-1].split('.')[0]
    output = {}
    
    for line in contents:
        if 'def ' in line:
            blocks = line.strip().split(' ')
            testname = ''
            for i in range(0, len(blocks)):
                if '(' in blocks[i]:
                    if blocks[i][0] == '(':
                        testname = blocks[i - 1]
                    else:
                        testname = blocks[i].split('(')[0]
            if testname[0:4] != 'test':
                continue
            if filename not in output.keys():
                output[filename] = { testname: 1 }
            else:
                output[filename][testname] = 1
    return output[filename], {}


def parse_java_tests(filepath):
    ''' This function will parse out test methods from the java junit framework
    '''
    f = open(filepath, 'r')
    contents = f.read()
    f.close()
    contents = contents.split('\n')
    filename = filepath.split('/')[-1].split('.')[0]
    isTest = False
    output = {}
    for line in contents:
        if '@Test' in line:
            isTest = True
        elif isTest:
            blocks = line.split(' ')
            testname = ''
            for i in range(0, len(blocks)):
                if '()' in blocks[i]:
                    if len(blocks[i]) < 3:
                        testname = blocks[i - 1]
                    else:
                        testname = blocks[i].split('()')[0]
            if filename not in output.keys():
                output[filename] = { testname: 1 }
            else:
                output[filename][testname] = 1
            isTest = False
    return output[filename], {}


class bcolors:
    """ Colors for color coded terminal printing
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def main():
    if len(sys.argv) >= 2:
        if sys.argv[1] == 'build_assignment_manifest':
            current_path = str(pathlib.Path(__file__).parent.absolute())
            asg_man_path = current_path.split('/')
            asg_man_path = '/'.join(asg_man_path[:-1])
            base_path = asg_man_path
            asg_man_path += '/config/assignment_manifest.json'
            f = open(asg_man_path, 'w+')
            f.write(generate_blank_assignment_manifest())
            f.close()
            parse_tests(base_path, asg_man_path)
            
    

if __name__ == "__main__":
    main()