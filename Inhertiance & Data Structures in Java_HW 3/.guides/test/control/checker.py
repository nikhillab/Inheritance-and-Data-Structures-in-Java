import util


class checker:
    """ This class checks files and functions to make sure that those that have been
    deemed a requirement for the assignment were implemented / exist.
    """

    def __init__(self, manager):
        """ Initialization function
        """
        self.manager = manager
        self.name = "checker"
        
        
    def check_required_files(self):
        """ Make sure required files exist (as specified in ../config/assignment_manifest.json)
        """
        self.narrate("Checking for required files\n")
        submission_files = util.find_files_recursive('/home/codio/workspace/submit')
        self.manager.log("Found these files in submit folder: {}".format(submission_files), raising_class=self)
        for req_file in self.manager.assignment_manifest_contents['assignment_overview']['required_files']:
            self.manager.log("Looking for file: {}".format(req_file), raising_class=self)
            self.narrate("{}{}{}\t".format(util.bcolors.OKGREEN, req_file, util.bcolors.ENDC))
            if req_file not in submission_files:
                self.narrate("MISSING!\n".format(util.bcolors.FAIL, util.bcolors.ENDC))
                return False
            else:
                self.narrate("{}FOUND!{}\n".format(util.bcolors.OKBLUE, util.bcolors.ENDC))
        self.manager.log("No files missing", raising_class=self)
        return True


    def check_required_functions(self):
        pass
    
    
    def narrate(self, msg):
        print(msg, end='')
        self.manager.log(msg, raising_class=self)
