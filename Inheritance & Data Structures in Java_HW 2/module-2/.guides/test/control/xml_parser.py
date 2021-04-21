import json

""" Helper xml parsing class for use in junit output. Sometimes, it comes out with a broken xml (or at least
one that the python library I'm using doesn't like), so this makes sure that we can still parse it
"""

def get_java_results(path_to_file, tests):
    """ Parse through XML output for java results.
    """
    root = parse_xml_doc(path_to_file)
    test_cases = get_all_tags_of_type('testcase', root)
    if len(test_cases) == 0:
        return tests

    for test_case in test_cases:
        test_class = test_case.properties['classname']
        if '$' in test_class:
            test_class = test_class.split('$')[0]
        test_name = test_case.properties['name']
        passed = True
        message = 'ok'
        cpt = test_case.get_children_prop_types()
        if 'failure' in cpt.keys():
            passed = False
            # print("Failure props: {}".format(cpt['failure'][0].properties.keys()))
            # print(cpt['failure'][0].properties)
            if 'message' in cpt['failure'][0].properties.keys():
                message = cpt['failure'][0].properties['message']
            else:
                message = cpt['failure'][0].properties['type']

        tests['java'][test_class][test_name]['passed'] = passed
        tests['java'][test_class][test_name]['message'] = message

    return tests


def parse_xml_doc(path_to_file):
    """ Simple helper to parse through poorly constructed XML doc. The only reason this exists is because
    JUnit outputs illegal characters in the standard XML reporting format, at least as according to both
    the lxml and xml python libraries
    """
    f = open(path_to_file, 'r')
    contents = f.read()
    active_tag = False
    closing_tag = False
    this_tag = ''
    current_open_parent = None
    current_open_tag = None
    root = None
    is_cdata = False

    for char in contents:

        # Check for character data (content)
        if active_tag and len(this_tag) > 5:
            if this_tag[:7] == '![CDATA':
                is_cdata, active_tag, closing_tag = True, False, False

        # If not content, begin tag parsing
        if not is_cdata:
            # Blind tag beginning
            if not active_tag and char == '<':
                active_tag = True
                this_tag = ''
            # Opening tag start
            elif active_tag and char != '/' and this_tag == '':
                closing_tag = False
                this_tag += char
            # Closing tag start
            elif active_tag and char == '/' and this_tag == '':
                closing_tag = True
                this_tag += char

            # Blind tag ending
            elif active_tag and char == '>':
                # Closing tag end. Pop this tag, shift parents down
                if closing_tag:
                    current_open_tag = current_open_parent
                    if current_open_tag is None:
                        break
                    current_open_parent = current_open_tag.parent
                # Opening tag end. Push this tag, shift parents up
                else:
                    if this_tag[-1] == '/':
                        current_open_tag.children.append(Tag(this_tag, current_open_tag))
                    elif this_tag[-1] != '?':
                        current_open_parent = current_open_tag
                        current_open_tag = Tag(this_tag, current_open_parent)
                        if root is None:
                            root = current_open_tag

                # Reset all flags
                active_tag, closing_tag = False, False

            elif active_tag:
                this_tag += char

        # Continue adding content to ![CDATA
        else:
            this_tag += char
            if this_tag[-3:] == ']]>':
                is_cdata = False
                content = this_tag
                current_open_tag.register_content(content)

    return root


def print_full_tree(root, indent=0):
    """ Method to visualize the tree
    """
    print('{}{}\n{}\n\n'.format(' ' * indent, root.prop_type, root.properties))
    for child in root.children:
        print_full_tree(child, indent + 2)


def get_all_tags_of_type(xml_tag_type, root, output=[]):
    for child in root.children:
        get_all_tags_of_type(xml_tag_type, child, output)

    if root.prop_type == xml_tag_type:
        output.append(root)

    return output


##################### XML TAG CLASS ########################

class Tag:
    """ Tag class is used to represent individual XML tags. Houses children,
    has content, properties, etc.
    """

    def __init__(self, raw_text, parent):
        """ Constructor taking in the parent and raw text
        """
        self.raw_text = raw_text
        self.children = []
        self.parent = parent
        self.properties = {}
        self.prop_type = 'unknown'
        self.set_properties()
        if parent is not None:
            parent.children.append(self)

    def register_content(self, content):
        """ function to register cdata as content
        """
        content = content.strip()
        content = content.replace('![CDATA[', '')
        content = content.replace(']]>', '')
        self.properties['cdata'] = content

    def set_properties(self):
        """ Parses the properties from the raw_text
        """
        self.properties = {}
        split_str = self.raw_text.split(' ')
        self.prop_type = split_str[0].strip()
        if len(split_str) > 0:
            split_str = self.raw_text[len(self.prop_type) + 1:]
            split_str = split_str.split("\" ")
            for term in split_str:
                term = term.split("=")
                if len(term) > 1:
                    key, val = term[0], term[1]
                    key = key.strip()
                    val = val.replace('\"', '').strip()
                    self.properties[key] = val

    def __str__(self):
        """ String representation of an XML tag
        """
        return("Name: {}\nChildren Count: {}\nParent: {}".format(
            self.raw_text,
            len(self.children),
            self.parent.raw_text if self.parent is not None else "<none>")
        )

    def get_children_prop_types(self):
        out = {}
        for child in self.children:
            c = child.prop_type
            if c in out.keys():
                out[c] = out[c].append(child)
            else:
                out[c] = [child]
        return out