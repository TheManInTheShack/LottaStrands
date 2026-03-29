import os
import sys
from datetime import datetime
import pandas as pd

# ------------------------------------------------------------------------------
# Always force-exit the program in the same way
# ------------------------------------------------------------------------------
def kill_program(msg):
    print(f"FATALITY!: {msg}")
    sys.exit()

# ------------------------------------------------------------------------------
# Check real quick - does this thing evaluate to a number?
# ------------------------------------------------------------------------------
def is_number(s):
    try:
        float(str(s))
        return True
    except ValueError:
        return False

# ------------------------------------------------------------------------------
# Summarize and display the contents of an object for debugging or learning
# ------------------------------------------------------------------------------
def show_me(obj, kill=False):
    # --------------------------------------------------------------------------
    # There's a host of libraries that might only apply in this, so do this here
    # --------------------------------------------------------------------------
    from traceback import extract_stack
    import re
    import numpy as np
    from datetime import datetime
    import bs4
    import pandas as pd

    # --------------------------------------------------------------------------
    # Get the name of the variable that was passed in as the parameter
    # --------------------------------------------------------------------------
    stack = extract_stack()
    filename, lineno, function_name, code = stack[-2]
    vname = re.compile(r'\((.*?)\).*$').search(code).groups()[0]

    # --------------------------------------------------------------------------
    # This thing is a little sub-function that will add a type-dependent detail
    # --------------------------------------------------------------------------
    def add_line_for_object_key(obj, key):
        v = obj[key]
        # ----------------------------------------------------------------------
        # Primitive types get the actual data
        # ----------------------------------------------------------------------
        if type(v) is str or type(v) is int or type(v) is float or isinstance(v, np.float64) or isinstance(v, np.int64) or isinstance(v, np.bool_) or type(v) is bool or isinstance(v, datetime):
            line = str(key).ljust(80) + str(type(obj[key])).ljust(40) + str(obj[key])

        elif isinstance(obj[key], bs4.element.NavigableString):
            line = str(key).ljust(80) + str(type(obj[key])).ljust(40) + str(obj[key])

        # ----------------------------------------------------------------------
        # Data frames get the shape, so does series
        # ----------------------------------------------------------------------
        elif isinstance(obj[key], pd.core.frame.DataFrame) or isinstance(obj[key], pd.core.series.Series):
            line = str(key).ljust(80) + str(type(obj[key])).ljust(40) + "Shape: " + str(obj[key].shape)

        # ----------------------------------------------------------------------
        # Hierarchy nodes get the breadth and depth of their children
        # ----------------------------------------------------------------------
        elif isinstance(obj[key], bs4.element.Tag):
            direct_children = len([x for x in obj[key].find_all(recursive=False)])
            all_children    = len([x for x in obj[key].find_all()])
            line = str(key).ljust(80) + str(type(obj[key])).ljust(40) + "Direct/All: " + str(direct_children) + "/" + str(all_children)

        # ----------------------------------------------------------------------
        # Lists and dicts are iterables
        # ----------------------------------------------------------------------
        elif type(v) is list or type(v) is dict:
            line = str(key).ljust(80) + str(type(obj[key])).ljust(40) + "# Items: " + str(len(obj[key]))

        # ----------------------------------------------------------------------
        # Anything else valid is iterables
        # ----------------------------------------------------------------------
        elif valid_value(obj[key]):
            line = str(key).ljust(80) + str(type(obj[key])).ljust(40) + "# Items: " + str(len(obj[key]))

        # ----------------------------------------------------------------------
        # ...or it's just blank
        # ----------------------------------------------------------------------
        else:
            line = str(key).ljust(80) + str(type(obj[key])).ljust(40)

        return line

    # --------------------------------------------------------------------------
    # Construct a little mini-report - start with a heading
    # --------------------------------------------------------------------------
    block = []
    block.append("-"*50)
    block.append("Variable name: " + vname)
    block.append("Variable type: " + str(type(obj)))
    block.append("-"*50)

    # --------------------------------------------------------------------------
    # Single types - string, integer, float, numpy int/float/bool, date, null
    # --------------------------------------------------------------------------
    if type(obj) is str:
        block.append("Value:  " + obj)
        block.append("Length: " + str(len(obj)))

    elif type(obj) is int or type(obj) is float or isinstance(obj, np.float64) or isinstance(obj, np.int64):
        block.append("Value:   " + str(obj))
        block.append("Digits:  " + str(len(str(obj))))

    elif isinstance(obj, np.bool_) or type(obj) is bool:
        block.append(obj)

    elif isinstance(obj, datetime):
        block.append(obj)

    # --------------------------------------------------------------------------
    # ...list or tuple might contain other things
    # --------------------------------------------------------------------------
    elif type(obj) is list or type(obj) is tuple:
        block.append("Items on list: " + str(len(obj)) )
        types = {}
        for item in obj:
            this_type = str(type(item))
            if not this_type in types:
                types[this_type] = 0
            types[this_type] += 1
        block.append("Items by type: ")
        for t in types:
            block.append(t.ljust(40) + str(types[t]))


        if len(obj) < 20:
            for i, item in enumerate(obj):
                idx = "[" + str(i) + "]"
                block.append(idx.ljust(20) + str(item))
        else:
            for i in range(0,5):
                idx = "[" + str(i) + "]"
                block.append(idx.ljust(20) + str(obj[i]))

            block.append("...")
            block.append("... (+ " +str(len(obj)-5-5) + " more items)")
            block.append("...")

            for i in range(len(obj)-5,len(obj)):
                idx = "[" + str(i) + "]"
                block.append(idx.ljust(20) + str(obj[i]))


    # --------------------------------------------------------------------------
    # ...dict definitely contains other things
    # --------------------------------------------------------------------------
    elif type(obj) is dict:
        block.append("Keys in dict: " + str(len(obj)) )

        keys = [x for x in obj]

        block.append("keys by type of value:")
        if len(keys) < 20:
            for key in keys:
                block.append(add_line_for_object_key(obj, key))
        else:
            for key in keys[0:5]:
                block.append(add_line_for_object_key(obj, key))

            block.append("...")
            block.append("... (+ " +str(len(obj)-5-5) + " more keys)")
            block.append("...")

            for key in keys[-6:-1]:
                block.append(add_line_for_object_key(obj, key))

    # --------------------------------------------------------------------------
    # Pandas Dataframe, just print the dataframe with whatever current settings
    # --------------------------------------------------------------------------
    elif isinstance(obj, pd.core.frame.DataFrame):
        block.append("Shape:  " + str(obj.shape))
        block.append(obj)

    # --------------------------------------------------------------------------
    # Pandas series, print out with whatever current settings
    # --------------------------------------------------------------------------
    elif isinstance(obj, pd.core.series.Series):
        block.append("Shape:  " + str(obj.shape))
        block.append(obj)

    # --------------------------------------------------------------------------
    # Pandas multiIndex
    # --------------------------------------------------------------------------
    elif isinstance(obj, pd.core.indexes.multi.MultiIndex):
        block.append("Shape:  " + str(obj.shape))
        block.append(obj)

    # --------------------------------------------------------------------------
    # BeautifulSoup string is just another string
    # --------------------------------------------------------------------------
    elif isinstance(obj, bs4.element.NavigableString):
        block.append("Value:  " + obj)
        block.append("Length: " + str(len(obj)))

    # --------------------------------------------------------------------------
    # BeautifulSoup node
    # --------------------------------------------------------------------------
    elif isinstance(obj, bs4.element.Tag):
        direct_children = len([x for x in obj.find_all(recursive=False)])
        all_children    = len([x for x in obj.find_all()])
        block.append("Direct Children: " + str(direct_children))
        block.append("All Children:    " + str(all_children))

    # --------------------------------------------------------------------------
    # ...unidentified is called out as nothing
    # --------------------------------------------------------------------------
    else:
        block.append("OBJECT'S TYPE NOT ACCOUNTED FOR IN show_me: " + str(type(obj)))

    # --------------------------------------------------------------------------
    # Finish the block
    # --------------------------------------------------------------------------
    block.append("")


    # --------------------------------------------------------------------------
    # Dump that to the screen
    # --------------------------------------------------------------------------
    for line in block:
        print(line)

    # --------------------------------------------------------------------------
    # 
    # --------------------------------------------------------------------------
    if kill:
        print("Dumping out of program")
        sys.exit()

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return True


# ------------------------------------------------------------------------------
# Given two text slugs, calculate their direct similarity using adjusted
# Levenshtein distance, limited by a Jaccard score
# ------------------------------------------------------------------------------
def text_similarity_score(v1, v2):
    # --------------------------------------------------------------------------
    # If one or the other isn't there, we can't do this
    # --------------------------------------------------------------------------
    if not isinstance(v1, str):
        return False
    elif not isinstance(v2, str):
        return False

    # --------------------------------------------------------------------------
    # Basic Lev distance
    # --------------------------------------------------------------------------
    #dist = lvs.distance(str(v1), str(v2))
    dist = jellyfish.damerau_levenshtein_distance(str(v1), str(v2))

    # --------------------------------------------------------------------------
    # Get the ratio of the smaller to the larger
    # --------------------------------------------------------------------------
    if len(v1) > len(v2):
        ratio = round(len(v1) / len(v2), 4)
    elif len(v2) > len(v1):
        ratio = round(len(v2) / len(v1), 4)
    else:
        ratio = 1.0

    # --------------------------------------------------------------------------
    # Adjust the score by the ratio - we are punishing matches where one is 
    # long and the other short
    # --------------------------------------------------------------------------
    if v1 == v2:
        adj_dist = 0.0
    else:
        adj_dist = dist * math.sqrt(ratio)

    # --------------------------------------------------------------------------
    # Score starts as that adjusted distance
    # --------------------------------------------------------------------------
    score = adj_dist

    # --------------------------------------------------------------------------
    # Jaccard similarity
    # --------------------------------------------------------------------------
    jac = jaccard_score(v1, v2)

    # --------------------------------------------------------------------------
    # Maybe we ditch based on that
    # --------------------------------------------------------------------------
    if jac == 0:
        score = None

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return score

# ------------------------------------------------------------------------------
# Takes any number of inputs and arranges them in a single matrix
# Return product will be a list of lists of primitives, no matter what is
# given as the input - any cell contents of complex type will be stringified
# ------------------------------------------------------------------------------
def matrixify(inputs, gutter=0, vertical=False):
    # --------------------------------------------------------------------------
    # Identify the type of each input and listify it if it isn't
    # --------------------------------------------------------------------------
    pass1 = []
    for item in inputs:
        if type(item) is list:
            pass1.append(item)
        elif type(item) is tuple:
            pass1.append(list(x for x in item))
        elif type(item) is dict:
            pass1.append(matrix_from_dict(item))
        else:
            pass1.append([[item]])

    # --------------------------------------------------------------------------
    # We now know that each input is a list, so we need to check that each
    # item in each of those lists is itself a list.
    # --------------------------------------------------------------------------
    pass2 = []
    for matrix in pass1:
        clean_matrix = []
        for row in matrix:
            if type(row) is list:
                clean_matrix.append(row)
            elif type(row) is tuple:
                clean_matrix.append(list(x for x in row))
            elif type(row) is dict:
                clean_matrix.append(listify_dict(row))
            else:
                clean_matrix.append([row])
        pass2.append(clean_matrix)

    # --------------------------------------------------------------------------
    # Finally, make sure that all the interior 'cells' are primitives
    # --------------------------------------------------------------------------
    matrices = []
    for matrix in pass2:
        clean_matrix = []
        for row in matrix:
            clean_line = []
            for cell in row:
                if type(cell) is list or type(cell) is tuple:
                    clean_line.append(",".join(str(cell)))
                elif type(cell) is float or type(cell) is int or type(cell) is str:
                    clean_line.append(cell)
                else:
                    clean_line.append(str(cell))
            clean_matrix.append(clean_line)
        matrices.append(clean_matrix)

    # --------------------------------------------------------------------------
    # At this point they are all matrices...
    # Presuming we want to stack these on top of each other
    # --------------------------------------------------------------------------
    if not vertical:
        # ----------------------------------------------------------------------
        # Figure out the widest row of any of them
        # ----------------------------------------------------------------------
        width = 0
        for matrix in matrices:
            # ------------------------------------------------------------------
            # Maybe it's just empty
            # ------------------------------------------------------------------
            if not matrix:
                continue
    
            # ------------------------------------------------------------------
            # check each internal row
            # ------------------------------------------------------------------
            for row in matrix:
                if len(row) > width:
                    width = len(row)
    
        # ----------------------------------------------------------------------
        # Go through each matrix line by line and write it into a final version
        # ----------------------------------------------------------------------
        final_matrix = []
        for i, matrix in enumerate(matrices):
            # ------------------------------------------------------------------
            # Maybe it's empty, so we want to make it a blank line
            # ------------------------------------------------------------------
            if not matrix:
                final_matrix.append([""]*width)
    
            # ------------------------------------------------------------------
            # Each row of the matrix, filled out with empty cells for however 
            # much to make it the common 'width'
            # ------------------------------------------------------------------
            for row in matrix:
                filler = list([""]*(width-len(row)))
                final_row = row + filler
                final_matrix.append(final_row)
    
            # ------------------------------------------------------------------
            # Gutter between matrices if necessary
            # ------------------------------------------------------------------
            if gutter and i < len(matrices)-1:
                for j in range(gutter):
                    final_matrix.append([""]*width)

    # --------------------------------------------------------------------------
    # Alternatively, if it is a vertical merge, we want to do the same thing
    # but sideways-to-slideways instead of upways-to-downways
    # --------------------------------------------------------------------------
    else:
        # ----------------------------------------------------------------------
        # Figure out the tallest column of any of them
        # ----------------------------------------------------------------------
        height = 0
        for matrix in matrices:
            if len(matrix) > height:
                height = len(matrix)

        # ----------------------------------------------------------------------
        # Go through each matrix
        # ----------------------------------------------------------------------
        for i, matrix in enumerate(matrices):
            # ------------------------------------------------------------------
            # we need to blank-fill the thing to match the tallest one
            # ------------------------------------------------------------------
            if matrix:
                width  = len(matrix[0])
            else:
                width  = 0
            filler = list([""]*width)
            for j in range(len(matrix),height):
                matrix.append(filler)

            # ------------------------------------------------------------------
            # Make the gutter with the specified number of cells wide by the
            # height that we got before
            # ------------------------------------------------------------------
            gutter_row = list([""] * gutter)
            gutter_matrix = list([gutter_row] * height)

            # ------------------------------------------------------------------
            # Now, positionally:
            # - first matrix becomes the basis for the rest
            # - any others are tacked on line-by-line
            # ------------------------------------------------------------------
            if i==0:
                final_matrix = matrix
            else:
                if gutter:
                    final_matrix = list(map(list.__add__, final_matrix, gutter_matrix))
                final_matrix = list(map(list.__add__, final_matrix, matrix))

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return final_matrix


# ------------------------------------------------------------------------------
# Recursively check through a directory tree and make a list of file paths that
# match a given list of extensions
# ------------------------------------------------------------------------------
def get_files_of_type(folder, extensions=[]):
    # --------------------------------------------------------------------------
    # Use the current if they didn't specify a folder)
    # --------------------------------------------------------------------------
    if not folder:
        folder = os.getcwd()

    # --------------------------------------------------------------------------
    # The extensions should always be a list 
    # --------------------------------------------------------------------------
    if type(extensions) is str:
        extensions = [extensions]

    # --------------------------------------------------------------------------
    # Roll through the directory tree and find all the ones we like
    # --------------------------------------------------------------------------
    files_of_type = []
    for root, dirs, files in os.walk(folder):
        # ----------------------------------------------------------------------
        # Look at each file
        # ----------------------------------------------------------------------
        for fname in files:
            # ------------------------------------------------------------------
            # Get that thing's path
            # ------------------------------------------------------------------
            fpath = os.path.join(root, fname)
            fplow = fpath.lower()

            # ------------------------------------------------------------------
            # Check it vs each extension on the list, maybe add it
            # ------------------------------------------------------------------
            for ext in extensions:
                exlow = ext.lower()
                if fplow.endswith(exlow):
                    files_of_type.append(fpath)

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return files_of_type


# ------------------------------------------------------------------------------
# Given a list of things, divide them into two buckets to track duplicates
# and non-duplicates, and their positions in the master list
# ------------------------------------------------------------------------------
def dupify(input_list, ignore_case=True):
    # --------------------------------------------------------------------------
    # Set up the structure
    # --------------------------------------------------------------------------
    dupes = {}
    dupes['duplicates'] = {}
    dupes['uniques']    = {}
    dupes['full']       = {}

    # --------------------------------------------------------------------------
    # Roll through the list and build up a new dict where the keys are the item
    # and the value is a list of line numbers
    # --------------------------------------------------------------------------
    for i, item in enumerate(input_list):
        if ignore_case and type(item) is str:
            item = item.lower()

        if not item in dupes['full']:
            dupes['full'][item] = []

        dupes['full'][item].append(i)

    # --------------------------------------------------------------------------
    # Now roll through that and make lists of what are duplicated and what are
    # unique
    # --------------------------------------------------------------------------
    for item in dupes['full']:
        if len(dupes['full'][item]) > 1:
            dupes['duplicates'][item] = dupes['full'][item]
        else:
            dupes['uniques'][item]    = dupes['full'][item]

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return dupes


# ------------------------------------------------------------------------------
# When we have something like this:
# "foo: 1"
# "foo: 4"
# "foo: 3"
# "foo: 185"
# "foo: 10"
# we want to be able to sort it by those numbers. if we just do a plain alpha
# sort we would get:
# "foo: 1"
# "foo: 10"
# "foo: 185"
# "foo: 3"
# "foo: 4"
# ...but if we use this thing, we would get:
# "foo: 1"
# "foo: 3"
# "foo: 4"
# "foo: 10"
# "foo: 185"
# ------------------------------------------------------------------------------
def sort_strings_by_numeric_suffix(strings):
    numbers = {}
    for i, string in enumerate(strings):
        num = string.split()[-1]
        numbers[string] = num

    sorted_strings = sorted(numbers, key=numbers.get)
    return sorted_strings

# ------------------------------------------------------------------------------
# Return a string of a 'version number', based on the current date
# ------------------------------------------------------------------------------
def version_by_day(prefix="", suffix=""):
    now = datetime.utcnow()
    version = f"{prefix}{now:%Y.%m.%d}{suffix}"
    return version

# ------------------------------------------------------------------------------
# Assemble a rectangular matrix with a heading and blank line above the body of
# a data frame...do that for each item on the list of 2-tuples that we receive.
# Then put them together horizontally. There might be only one part, it's fine.
# Note that the index of the data frame in item[1] will be IGNORED, so any cols
# that should actually be in the body should be taken out of the index BEFORE
# this function is called.
# ------------------------------------------------------------------------------
def prepare_map_body(content):
    parts = []
    for item in content:
        title = item[0]
        head = list(item[1].columns)
        body = item[1].values.tolist()
        block = []
        block.append([[title]])
        block.append([[]])
        block.append([head])
        block.append(body)
        matrix = matrixify(block)
        parts.append(matrix)

    map_body = matrixify(parts, vertical=True, gutter=1)
    return map_body

# ------------------------------------------------------------------------------
# Read any generic map sheet that follows the basic pattern
# Line 1 - section headings, unique text in first column of each new section
# Line 2 - all blank, ignored
# Line 3 - Column heading in every cell
# Lien 4+ - the data
# 1 |Section A|        |        |        |Section B|        |        |
# 2 |         |        |        |        |         |        |        |
# 3 |Foo      |Bar     |Baz     |Qux     |Quux     |Freb    |Pib     |
# 4 |1        |Abc     |3       |5       |defg     |hijk    |lmnop   |
# yields:
#  data {
#  'Section A': { 'Foo': 1, 'Bar': 'Abc', 'Baz': 3, 'Qux': 5 },
#  'Section B': { 'Quux': 'defg', 'Freb': 'hijk', 'Pib': 'lmnop' }
#  }
# ------------------------------------------------------------------------------
def read_map_sheet(map_file, sheet, index=[]):
    # --------------------------------------------------------------------------
    # Maybe the file doesn't exist?
    # --------------------------------------------------------------------------
    if not os.path.isfile(map_file):
        print(f"NOTE: The file {map_file} does not exist!!")
        return {}

    # --------------------------------------------------------------------------
    # Get the raw data
    # --------------------------------------------------------------------------
    try:
        raw = pd.read_excel(map_file, sheet_name=sheet, header=None, keep_default_na=False, engine="openpyxl")
    except:
        print(f"NOTE: The sheet {sheet} could not be read - might not exist.")
        return {}

    #print(raw)

    # --------------------------------------------------------------------------
    # Maybe there's nothing
    # --------------------------------------------------------------------------
    if raw.shape[0] == 0:
        print(f"NOTE: Be aware there was no data found on sheet {sheet}!")
        return {}

    # --------------------------------------------------------------------------
    # Look at the first line to get the section titles and their positions
    # --------------------------------------------------------------------------
    title = raw.loc[:0]
    columns = list(title.iloc[0])

    sections = []
    startpos = []
    for i, item in enumerate(columns):
        if len(item) > 0:
            sections.append(item)
            startpos.append(i)

    endpos   = []
    for i, section in enumerate(sections):
        if i < len(sections)-1:
            endpos.append(startpos[i+1]-1)
        else:
            endpos.append(len(columns)-1)

    #print(sections)
    #print(startpos)
    #print(endpos)

    # --------------------------------------------------------------------------
    # Is the index key one variable or multiple, or not there?
    # --------------------------------------------------------------------------
    if type(index) is list:
        if len(index) == 0:
            keystyle = "none"
        elif len(index) == 1:
            keystyle = "single"
        else:
            keystyle = "multi"
    else:
        keystyle = "single"

    # --------------------------------------------------------------------------
    # Put together the key based on the index parameter
    # --------------------------------------------------------------------------
    idxdata = raw.iloc[3:]
    idxdata.columns = raw.iloc[2]
    idxdata = idxdata[index]

    keycol_data = idxdata.values.tolist()
    #print(keycol_data)
    #print(keycol_data[0])

    keycol = []
    for i, rec in enumerate(keycol_data):
        # ----------------------------------------------------------------------
        # Multiresponse is a list of tuples
        # ----------------------------------------------------------------------
        if keystyle == "multi":
            if not valid_value(rec[1]):
                rec[1] = ""
            if type(rec[0]) is str:
                rec[0] = rec[0].lower()
            if type(rec[1]) is str:
                rec[1] = rec[1].lower()
            keycol.append((rec[0],rec[1]))

        # ----------------------------------------------------------------------
        # Single
        # TODO - if it's single from a list, it breaks
        # ----------------------------------------------------------------------
        elif keystyle == "single":
            if type(rec) is str:
                rec = rec.lower()
            keycol.append(rec)

        # ----------------------------------------------------------------------
        # None
        # ----------------------------------------------------------------------
        elif keystyle == "none":
            keycol.append(i)

    #print(keycol[0:4])

    # --------------------------------------------------------------------------
    # Pull each section's dataframe
    # --------------------------------------------------------------------------
    data = {}
    for i, section in enumerate(sections):
        # ----------------------------------------------------------------------
        # Organize the parameters we need
        # ----------------------------------------------------------------------
        start      = startpos[i]
        end        = endpos[i] + 1
        df         = raw.iloc[3:,start:end]
        df.columns = raw.iloc[2, start:end]

        # ----------------------------------------------------------------------
        # Apply the key if there is one
        # ----------------------------------------------------------------------
        if keystyle == "multi":
            df.index   = pd.MultiIndex.from_tuples(keycol)
        elif keystyle == "single": 
            df.index = keycol

        # ----------------------------------------------------------------------
        # Add it to the structure
        # ----------------------------------------------------------------------
        data[section] = df

    #for section in data:
    #    print(section)
    #    print(data[section].shape)

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return data
