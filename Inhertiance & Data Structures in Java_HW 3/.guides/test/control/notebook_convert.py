import sys, json, time, re
import util

''' ===============================================================================================
    This class is used to convert a .ipynb file into a .py file for grading using the unittest
    python framework
    ===============================================================================================
'''

def seed_random(source):
    ''' This function is used to seed the random library with a common
    seed so that the test cases can compare apples-to-apples
    '''
    source_as_list = source.split('\n')
    for i in range(len(source_as_list)):
        line = source_as_list[i]
        location = re.search('import\s+random', line)
        if location is not None:
            
            # Find indentation level, then match and append
            prefix = ''
            for c in line:
                if c == ' ' or c == '\t':
                    prefix += c
                else:
                    break
            line += '\n{}random.seed(0)'.format(prefix)
            source_as_list[i] = line
    
    source = '\n'.join(source_as_list)
    return source.split('\n')
    

def list_to_dict_str(the_list):
    ''' This function creates a string version of a list to be written
    to the output file as a dictionary. Pass in a list, you'll receive
    a dictionary - it's used to parse the check_val field
    '''
    ret_val = '{'
    for i in range(len(the_list)):
        ret_val += '"{}": {}'.format(the_list[i], the_list[i])
        if i == len(the_list) - 1:
            ret_val += '}'
        else:
            ret_val += ', '
    return ret_val


def parse_cell(cell, outfile, nb_version):
    ''' This function will parse a cell and write it to the outfile
    '''
    if cell['cell_type'] == 'code':
        ret = parse_code_cell(cell, outfile, nb_version)
        outfile.write('\n\n')
        return ret
    else:
        return 0, 0


def parse_code_cell(cell, outfile, nb_version):
    ''' This function will format a new .py file from .ipynb with structure such that
    each named cell (name must be in metadata) is assigned as a variable to 
    '''
    source = cell['source'] if nb_version == 'old' else cell['input']
    source_str = '\n'.join(source)
    if len(re.findall('import\s+random', source_str)) > 0 or len(re.findall('from\s+random', source_str)) > 0:
        source = seed_random(source_str)
    
    if 'name' not in cell['metadata'].keys():
        # Non-named cell, don't care, just write it
        source_to_write = []
        for line in source:
            for char in line:
                if char == ' ' or char == '\t':
                    continue
                elif char == '%':
                    break
                else:
                    source_to_write.append(line)
                    break
                    
        outfile.write('\n'.join(source_to_write))
        return 0, 1
    else:
        name = cell['metadata']['name']
        if 'check_val' in cell['metadata'].keys():
            # Override case. This is where we tell the script exactly
            # which variables to check, and is preferable
            outfile.write('\n'.join(source))
            outfile.write('\n\n{} = {}'.format(cell['metadata']['name'], list_to_dict_str(cell['metadata']['check_val'])))
        elif 'def' in '\n'.join(source):
            # If defined function, get the name of the function and pass that back
            # as the return value
            func_name = '\n'.join(source).split(' ')[1].split('(')[0]
            outfile.write('\n'.join(source))
            outfile.write('\n\n{} = {}'.format(name, func_name))
        elif 'print' in '\n'.join(source):
            # If there are print statements, use those instead
            outfile.write('\n'.join(source))
            text_to_write = cell['outputs'][0]['text']
            for i in range(len(text_to_write)):
                text_to_write[i] = text_to_write[i].strip()
            outfile.write('\n\n{} = {}'.format(name, text_to_write))
        else:
            # In line case
            for i in range(len(source)):
                if i == len(source) - 1:
                    to_write = ''
                    for c in source[i]:
                        if c == '\t' or c == ' ':
                            to_write += c
                        else:
                            break
                    stop_location = len(to_write)
                    to_write += "{} = ".format(name)
                    to_write += source[i][stop_location:]
                    outfile.write(to_write)
                else:
                    outfile.write(source[i])
        return 1, 0
            

def convert_notebook(infile, outfile_arg, log_path):
    """ Convert a jupyter notebook to python, write it to the logging location
    """
    logger = open("{}/nbconvert.log".format(log_path), "a+")
    logger.write('\n\n\n\n======================================================================\n')
    logger.write('{}\n'.format(util.get_datetime()))
    logger.write(' > Beginning conversion of {}\n'.format(infile))
    f = open(infile)
    contents = f.read()
    f.close()
    contents = json.loads(contents)
    cells = contents['cells'] if 'cells' in contents.keys() else contents['worksheets'][0]['cells']
    nb_version = 'old' if 'cells' in contents.keys() else 'new'
    logger.write(' > Found {} cells\n'.format(len(cells)))
    outfile = open('{}'.format(outfile_arg), 'w+')
    outfile.write('#!/bin/python3\n\n\n')
    definitions, declarations = 0, 0
    for cell in cells:
        x, y = parse_cell(cell, outfile, nb_version)
        definitions += x
        declarations += y
            
    logger.write(' > Wrote {} function definition cells\n'.format(definitions))
    logger.write(' > Wrote {} declarative cells\n'.format(declarations))
    logger.write('======================================================================\n')
    logger.write(' > Finished writing to {}\n'.format(outfile_arg))
    logger.write('======================================================================\n')


def main():    
    convert_notebook(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()