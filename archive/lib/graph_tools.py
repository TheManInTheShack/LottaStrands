# ------------------------------------------------------------------------------
# Set of graph-related tools, using the Python neo4j library for direct control
# ------------------------------------------------------------------------------
from neo4j import GraphDatabase
#import numpy as np
#import math
from datetime import datetime
import sys
from utilities import kill_program
from utilities import is_number
from utilities import sort_strings_by_numeric_suffix

# ------------------------------------------------------------------------------
# Connect to the appropriate local or remote graph
# ------------------------------------------------------------------------------
def connect_to_graph(config):
    if config['use_local_graph']:
        graph = connect_to_local_graph(config['local_graph_user'], config['local_graph_pwd'])
    else:
        graph = connect_to_remote_graph(config['remote_graph_uri'], config['remote_graph_user'], config['remote_graph_pwd'])
    return graph

# ------------------------------------------------------------------------------
# Connect to the currently-running neo4j database, or warn the user
# ------------------------------------------------------------------------------
def connect_to_local_graph(graph_user, graph_pwd):
    uri = "neo4j://localhost:7687"
    print(f"...connecting to remote graph db at {uri}...")
    try:
        graph = GraphDatabase.driver(uri, auth=(graph_user, graph_pwd))
        print("...successfully connected to open local graph at " + uri + "...")
        return graph
    except:
        kill_program("There is no local open Neo4j session detected, or the given password is incorrect.  Please check and try again.")

# ------------------------------------------------------------------------------
# Make a connection to a remote graph
# ------------------------------------------------------------------------------
def connect_to_remote_graph(graph_loc, graph_user, graph_pwd):
    print("...connecting to remote graph db at " + graph_loc + "...")
    try:
        #uri = "bolt://" + graph_loc + ":7687"
        uri = graph_loc
        graph = GraphDatabase.driver(uri, auth=(graph_user, graph_pwd))
        print("...successfully connected to db...")
        return graph
    except:
        kill_program("WARNING!  Failed to connect to remote db.")

# ------------------------------------------------------------------------------
# Clean out a graph based on a flag
# ------------------------------------------------------------------------------
def restart_graph(graph, do=False, constrain=[]):
    # --------------------------------------------------------------------------
    # Maybe we want to do it
    # --------------------------------------------------------------------------
    if do:
        # ----------------------------------------------------------------------
        # We never want to do this without being interactive, do we?
        # ----------------------------------------------------------------------
        check = input("Are you really sure you want to restart this graph?  It's going to erase the whole thing.  Put in 'yEs' specifically if you really mean it:\n")
        if not check == "yEs":
            print("you have chosen NOT to restart, so that's not happening. Be really careful with this choice in the future.  Have you backed it up?")
            kill_program("...since you don't seem too sure about this, I'm going to ditch.")
        print("...okay then, here we go!")

        # ----------------------------------------------------------------------
        # Remove all nodes and connections
        # ----------------------------------------------------------------------
        query = "MATCH (n) CALL {WITH n DETACH DELETE n} IN TRANSACTIONS OF 10000 ROWS"
        graph.session().run(query)
        print("...graph reset, all existing nodes deleted...")

        # ----------------------------------------------------------------------
        # Add or re-add any constraints for Unique node types
        # ----------------------------------------------------------------------
        if constrain:
            print("...setting up constraint instructions for unique node types...")
            for node_type in constrain:
                query = "CREATE CONSTRAINT " + node_type + " IF NOT EXISTS FOR (a:" + node_type + ") REQUIRE a.idx IS UNIQUE"
                graph.session().run(query)
            print("...constraints setup complete...")

        # ----------------------------------------------------------------------
        # Ok it worked
        # ----------------------------------------------------------------------
        return True

    # --------------------------------------------------------------------------
    # Maybe we just don't want to do it
    # --------------------------------------------------------------------------
    else:
        return False


# ------------------------------------------------------------------------------
# Simply run a query (given as a list or a string) and maybe show it
# ------------------------------------------------------------------------------
def run_cypher_query(graph, query, params={}, show=False, timer=True):
    # --------------------------------------------------------------------------
    # Start timer
    # --------------------------------------------------------------------------
    if timer:
        t1 = datetime.utcnow()

    # --------------------------------------------------------------------------
    # User info if we want it
    # --------------------------------------------------------------------------
    if show:
        print("...running cypher query:")
        if type(query) is list:
            for line in query:
                print("......|", line)
        elif type(query) is str:
            print("......|", query)
        

    # --------------------------------------------------------------------------
    # Run the query
    # --------------------------------------------------------------------------
    if type(query) is list:
        if params:
            result = graph.session().run(" ".join(query), parameters=params)
        else:
            result = graph.session().run(" ".join(query))
    elif type(query) is str:
        if params:
            result = graph.session().run(query, parameters=params)
        else:
            result = graph.session().run(query)
    else:
        print("DEV: Unfortunately this query is not in the form of a list or a string...please fix this in your code.")
        sys.exit()

    # --------------------------------------------------------------------------
    # Finish the timer
    # --------------------------------------------------------------------------
    if timer:
        t2 = datetime.utcnow()
        te = t2 - t1
        if show:
            print(f"......query finished running in {te}...")

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return result

# ------------------------------------------------------------------------------
# Retrieve existing nodes from the graph following patterns
# ------------------------------------------------------------------------------
def get_existing_nodes(graph, query="", ntype="", idx="", single=False, required=False):
    # --------------------------------------------------------------------------
    # If we are after: 
    # - a type and an index
    # - Only a type
    # - Not even a type
    # --------------------------------------------------------------------------
    if not query:
        if ntype and idx:
            query = f"MATCH (n:{ntype}) WHERE n.idx = '{idx}' RETURN n"
        elif ntype:
            query = f"MATCH (n:{ntype}) RETURN n"
        else:
            query = "MATCH (n) RETURN n"

    # --------------------------------------------------------------------------
    # Run the query
    # --------------------------------------------------------------------------
    result = graph.session().run(query)

    # --------------------------------------------------------------------------
    # Get a node count
    # --------------------------------------------------------------------------
    count = len(result.keys())

    # --------------------------------------------------------------------------
    # If it's required, there must be one or more
    # --------------------------------------------------------------------------
    if required:
        if count == 0:
            kill_program("Required node not found: " + ntype + "/" + idx)

    # --------------------------------------------------------------------------
    # If it's supposed to be single, make sure there's only one and return it
    # --------------------------------------------------------------------------
    if single:
        if count > 1:
            kill_program("More than one of expected single node found: " + ntype + "/" + idx)
        node = dict(result.value()[0])
        return node

    # --------------------------------------------------------------------------
    # Or else return all the nodes
    # --------------------------------------------------------------------------
    else:
        if count > 0:
            nodes = [dict(x) for x in result.value()]
            return nodes
        else:
            print("...no results returned...")
            return []

# ------------------------------------------------------------------------------
# Create a new node, with properties and connections to existing nodes
# The 'node' object here is a dictionary containing the details:
# {
# label: a string indicating the primary label (discipline is only one label)
# index: a unique index for the label type
# props: a standard dictionary of properties that will be added to the node
# rels:  a dictionary of relationships, each stored as a sub-dict
#        {
#        from: a tuple of label and index of a node to come FROM 
#        to:   a tuple of label and index of a node to go TOWARD
#              (only one of from or to will be used per relationship)
#        verb: a string (uppercase) indicating the label on the relationship
#        props: same as for the node, a dict of props that will go on the rel
#        }
# }
#
# EXAMPLE QUERY - we create this as a text block
# This creates a new instance of a node in a chain and adds properties:
#    MATCH  (prev:Brandy {idx: "Brandy round 1"})
#    CREATE (this:Brandy {idx: "Brandy round 2"})
#    MERGE  (prev)-[NEXT_BATCH]->(this)
#    SET this.created = timestamp()
#    SET this.src_path = "S:\Trackers\Foo\Some.mdd"
# ------------------------------------------------------------------------------
def create_single_node(graph, node, constrain=False):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    query = []

    # --------------------------------------------------------------------------
    # Make the match section if we need it
    # --------------------------------------------------------------------------
    if 'rels' in node:
        # ----------------------------------------------------------------------
        # We need to have a match for each of them
        # ----------------------------------------------------------------------
        matches = []
        for rel in node['rels']:
            # ------------------------------------------------------------------
            # Get the node reference
            # ------------------------------------------------------------------
            if 'from' in node['rels'][rel]:
                ref = node['rels'][rel]['from']
            elif 'to' in node['rels'][rel]:
                ref = node['rels'][rel]['to']
            else:
                kill_program("WAIT A MINUTE HOW ARE YOU PASSING A RELATIONSHIP REFERENCE WITHOUT A 'from' OR A 'to'?")

            # ------------------------------------------------------------------
            # Add it to the list
            # ------------------------------------------------------------------
            slug = rel + ":" + ref[0] + " {idx:" + '"' + ref[1] + '"}'
            matches.append(slug)

        # ----------------------------------------------------------------------
        # Make the match statement
        # ----------------------------------------------------------------------
        if matches:
            statement = "MATCH (" + ") WITH * MATCH (".join(matches) + ")"
            query.append(statement)

    # --------------------------------------------------------------------------
    # Make the create statement, or merge if we are constraining
    # --------------------------------------------------------------------------
    if constrain:
        statement = "MERGE (this:" + node['label'] + " {idx:" + '"' + node['index'] + '"' + '})'
    else:
        statement = "CREATE (this:" + node['label'] + " {idx:" + '"' + node['index'] + '"' + '})'
    query.append(statement)

    # --------------------------------------------------------------------------
    # Add properties to the node
    # --------------------------------------------------------------------------
    if 'props' in node:
        for prop in node['props']:
            val = node['props'][prop]
            if val == "{TIMESTAMP}":
                statement = "SET this." + prop + "=" + "timestamp()"
            elif is_number(val):
                statement = "SET this." + prop + "=" + str(val)
            else:
                statement = "SET this." + prop + "=" + '"' + str(val) + '"'
            query.append(statement)

    # --------------------------------------------------------------------------
    # Make the merge statement if we need it
    # --------------------------------------------------------------------------
    if 'rels' in node:
        # ----------------------------------------------------------------------
        # One for each relationship
        # ----------------------------------------------------------------------
        for rel in node['rels']:
            # ------------------------------------------------------------------
            # Always with* it to make sure
            # ------------------------------------------------------------------
            query.append("WITH * ")

            # ------------------------------------------------------------------
            # Maybe it's coming from that node to this one
            # ------------------------------------------------------------------
            if 'from' in node['rels'][rel]:
                nref = rel
                rref = "r_" + nref
                verb = node['rels'][rel]['verb']
                statement = "MERGE (" + nref + ")-[" + rref + ":" + verb + "]->(this)"
                query.append(statement)

            # ------------------------------------------------------------------
            # Maybe it's going from this node to that one
            # ------------------------------------------------------------------
            elif 'to' in node['rels'][rel]:
                nref = rel
                rref = "r_" + nref
                verb = node['rels'][rel]['verb']
                statement = "MERGE (this)-[" + rref + ":" + verb + "]->(" + nref + ")"
                query.append(statement)

            # ------------------------------------------------------------------
            # Add properties to the relationship
            # ------------------------------------------------------------------
            if 'props' in node['rels'][rel]:
                for prop in node['rels'][rel]['props']:
                    val = node['rels'][rel]['props'][prop]
                    if val == "{TIMESTAMP}":
                        statement = "SET " + rref + "." + prop + "=" + "timestamp()"
                    elif is_number(val):
                        statement = "SET " + rref + "." + prop + "=" + str(val)
                    else:
                        statement = "SET " + rref + "." + prop + "=" + '"' + str(val) + '"'
                    query.append(statement)

            # ------------------------------------------------------------------
            # Add a comma between the rels if there
            # ------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Call the query
    # --------------------------------------------------------------------------
    x = graph.session().run(" ".join(query))

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return True

# ------------------------------------------------------------------------------
# Given a dataframe, we want the rows to become nodes where the index is the
# index, and the columns are properties. We need the data and the node type,
# and we can potentially take a dictionary of relationships that all nodes will
# have, and potentially a dictionary that specifies the usage of certain columns
# as relationships instead of properties
# Note that because 'nidx' and 'dn' (where n is 0-n) are used as variable names
# in the queries, that column names in the data frame CANNOT have those names,
# because the columns want to become variable names too sometimes.
# ------------------------------------------------------------------------------
def dataframe_to_nodes(graph, df, node_type, common_rels={}, column_rels={}, display_query=False):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    print("...merging nodes into graph from source sized " + str(df.shape[0]) + " rows / " + str(df.shape[1]) + " columns...")

    # --------------------------------------------------------------------------
    # We're going to have to write something to deal with multiindexed records.
    # I think we should just combine them into a single delimited text field 
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Clean up the data
    # - Fill in missing because query bombs on empty property. 
    #   - we should figure out a way to ignore the property in the query if
    #     it is none, but for now this works
    # - name the index 'nidx'
    # - Put the ID back into columns and name it index
    # --------------------------------------------------------------------------
    df = df.fillna("# MISSING #")
    df.index.name = "nidx"
    df = df.reset_index()


    # --------------------------------------------------------------------------
    # If there are common relationships, we need to set up the match statements
    # for those nodes
    # --------------------------------------------------------------------------
    matches = []
    for i, rel in enumerate(common_rels):
        # ----------------------------------------------------------------------
        # Unpack
        # ----------------------------------------------------------------------
        verb  = common_rels[rel]['verb']
        dtype = common_rels[rel]['dtype']
        adir  = common_rels[rel]['adir']
        idx   = common_rels[rel]['idx']

        # ----------------------------------------------------------------------
        # construct the line we'll need
        # ----------------------------------------------------------------------
        line = "(" + rel + ":" + dtype + " {idx:'" + idx + "'})"
        matches.append(line)

    # --------------------------------------------------------------------------
    # If there are columns which are relationships, separate them
    # --------------------------------------------------------------------------
    col_rel_vars = []
    if column_rels:
        col_rel_vars = [x for x in column_rels]

    # --------------------------------------------------------------------------
    # get the node property names, which are just the rest of the columns
    # --------------------------------------------------------------------------
    props = [x for x in df.columns if not x == "nidx" and not x in col_rel_vars]

    # --------------------------------------------------------------------------
    # Start building the query
    # --------------------------------------------------------------------------
    query = []

    # --------------------------------------------------------------------------
    # Match statements
    # --------------------------------------------------------------------------
    if matches:
        query.append("MATCH " + ",".join(matches) )
    query.append("WITH *")

    # --------------------------------------------------------------------------
    # We want to run it in batches
    # --------------------------------------------------------------------------
    #query.append("CALL {")

    # --------------------------------------------------------------------------
    # Start the query with the unwind statement to access the rows passed in
    # --------------------------------------------------------------------------
    query.append("UNWIND $rows AS row")

    # --------------------------------------------------------------------------
    # query for verifying/adding the nodes
    # --------------------------------------------------------------------------
    #addnode = 
    #addnode += "MERGE (n:" + node_type + " { "
    #addnode += "idx:row.nidx"
    #for prop in props:
        #addnode += ", " + prop + ":row." + prop
    #addnode += " })"

    query.append(f"MERGE (n:{node_type} {{ idx:row.nidx }})")

    # --------------------------------------------------------------------------
    # Set the properties
    # --------------------------------------------------------------------------
    if len(props) > 0:
        addprops = []
        for i, prop in enumerate(props):
            line = f"n.{prop} = row.{prop}"
            if i < len(props)-1:
                line += ","
            addprops.append(line)

        query.append("ON CREATE SET ")
        query.extend(addprops)
        query.append("ON MATCH SET ")
        query.extend(addprops)

    #query.append("WITH n")

    # --------------------------------------------------------------------------
    # Add any common relationships
    # --------------------------------------------------------------------------
    for i, rel in enumerate(common_rels):
        # ----------------------------------------------------------------------
        # Unpack
        # ----------------------------------------------------------------------
        verb  = common_rels[rel]['verb']
        dtype = common_rels[rel]['dtype']
        adir  = common_rels[rel]['adir']
        idx   = common_rels[rel]['idx']

        # ----------------------------------------------------------------------
        # Set the action
        # ----------------------------------------------------------------------
        if adir == "to":
            action = "-[:" + verb + "]->"
        elif adir == "from":
            action = "<-[:" + verb + "]-"
        else:
            kill_program("hey dev, how come there's a relationship call with no direction 'from' or 'to'?")

        # ----------------------------------------------------------------------
        # Add to the query
        # ----------------------------------------------------------------------
        query.append("MERGE (n)" + action + "(" + rel + ")")

    #if common_rels:
    #    query.append("WITH n")

    # --------------------------------------------------------------------------
    # Add any secondary nodes/relationships that are in other columns
    # --------------------------------------------------------------------------
    for i, rel in enumerate(column_rels):
        # ----------------------------------------------------------------------
        # Unpack
        # ----------------------------------------------------------------------
        verb  = column_rels[rel]['verb']
        dtype = column_rels[rel]['dtype']
        adir  = column_rels[rel]['adir']

        # ----------------------------------------------------------------------
        # Destination reference node
        # ----------------------------------------------------------------------
        dvar = "d" + str(i)
        dref = "(" + dvar + ":" + dtype + " { idx:row." + rel + " })"

        # ----------------------------------------------------------------------
        # Set the action
        # ----------------------------------------------------------------------
        if adir == "to":
            action = "-[:" + verb + "]->"
        elif adir == "from":
            action = "<-[:" + verb + "]-"
        else:
            kill_program("hey dev, how come there's a relationship call with no direction 'from' or 'to'?")

        # ----------------------------------------------------------------------
        # Match or merge depending on if it's expected to exist already
        # ----------------------------------------------------------------------
        if 'exists' in column_rels[rel]:
            #grab = "MATCH"
            grab = "MERGE"
        else:
            grab = "MERGE"

        # ----------------------------------------------------------------------
        # Add to the query
        # ----------------------------------------------------------------------
        query.append(grab + " " + dref)
        query.append("MERGE (n)" + action + "(" + dvar + ")")
        #query.append("WITH n")

    # --------------------------------------------------------------------------
    # Add the return to the query
    # --------------------------------------------------------------------------
    #query.append("RETURN count(n) AS count")

    # --------------------------------------------------------------------------
    # Finish the batch call
    # --------------------------------------------------------------------------
    #query.append("} IN TRANSACTIONS OF 10000 ROWS")
    #query.append("RETURN count")

    # --------------------------------------------------------------------------
    # Print a nice version of the query if we want to
    # --------------------------------------------------------------------------
    if display_query:
        print("...running cypher query:")
        for line in query:
            print("......|", line)

    # --------------------------------------------------------------------------
    # Even with the "IN BATCHES OF", it's still possibly filling up the single-
    # transaction memory block.  We can read that number in the running db,
    # and then do math on the size of this dataframe and (maybe break it up?)
    # --------------------------------------------------------------------------
    bound = 250000
    numcells = df.shape[0] * df.shape[1]

    chunks = []
    if numcells > bound:
        rows_per_bound = bound / df.shape[1]
        target_chunks = math.ceil(df.shape[0] / rows_per_bound)

        cutoff = 0
        for j in range(target_chunks):
            start  = int(j * rows_per_bound)
            cutoff = int((j+1) * rows_per_bound)
            dfx = df.iloc[start:cutoff,:]
            chunks.append(dfx)
    else:
         chunks.append(df)

    if len(chunks) > 1:
        print(f"...due to the amount of data, this query will be run in {len(chunks)} chunks...")

    # --------------------------------------------------------------------------
    # Now run the query on each chunk in turn
    # --------------------------------------------------------------------------
    for i, dfx in enumerate(chunks):
        # ----------------------------------------------------------------------
        # User info
        # ----------------------------------------------------------------------
        if len(chunks) > 1:
            print(f"...running cypher query for chunk {i+1} of {len(chunks)}...")
        else:
            print("...running cypher query...")

        # ----------------------------------------------------------------------
        # Put together the parameters
        # ----------------------------------------------------------------------
        params = {}
        params['rows'] = dfx.to_dict('records')
    
        # ----------------------------------------------------------------------
        # Run the query
        # ----------------------------------------------------------------------
        result = graph.session().run(" ".join(query), parameters=params)
        #print("...result count of nodes:", result.peek())
        print("...query transaction completed...")

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return result

# ------------------------------------------------------------------------------
# Given a dataframe understood to be wholly a relationship matrix, put it in
# a form for easy ingestion and write to the graph, using the index and 
# columns as node 'idx' names, and the internal measure stored as a property
# ------------------------------------------------------------------------------
def apply_relationship_matrix(graph, df, leftnode, rightnode, verb, direction, measure, display_query=True):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    print("...adding measure from relationship matrix: (" + leftnode + ")-[" + verb + "]-(" + rightnode + "), measure=" + measure)

    # --------------------------------------------------------------------------
    # Melt the dataframe into the form we need, which is to-from-value, and
    # remove any blanks
    # --------------------------------------------------------------------------
    df = df.astype(str).replace("",np.nan)
    df = df.melt(ignore_index=False).dropna(how="any")
    df = df.reset_index(drop=False)
    df = df.rename({'index':'fromnode','variable':'tonode','value':measure}, axis=1)

    print("...building input for " + str(df.shape[0]) + " relationships...")

    # --------------------------------------------------------------------------
    # Here's the text blob that indicates the relationship
    # --------------------------------------------------------------------------
    #rel = "[r:" + verb + " {" + measure + ":row." + measure + "}]"
    rel = "[r:" + verb + "]"

    # --------------------------------------------------------------------------
    # Based on the direction set the action
    # --------------------------------------------------------------------------
    if direction   == "to":
        action = "-" + rel + "->"
    elif direction == "from":
        action = "<-" + rel + "-"
    else:
        action = "-" + rel + "-"

    # --------------------------------------------------------------------------
    # start the main query
    # Unwind statement to access the rows passed in
    # --------------------------------------------------------------------------
    query = []
    query.append("UNWIND $rows AS row")

    # --------------------------------------------------------------------------
    # Match and merge
    # --------------------------------------------------------------------------
    query.append("MATCH")
    query.append("(n1:" + leftnode  + " {idx:row.fromnode}),")
    query.append("(n2:" + rightnode + " {idx:row.tonode})")
    query.append("MERGE (n1)" + action + "(n2)")

    # --------------------------------------------------------------------------
    # Add the property
    # --------------------------------------------------------------------------
    query.append("SET r." + measure + " = row." + measure)

    # --------------------------------------------------------------------------
    # Return
    # --------------------------------------------------------------------------
    query.append("RETURN count(r)")

    # --------------------------------------------------------------------------
    # Print a nice version of the query if we want to
    # --------------------------------------------------------------------------
    if display_query:
        print("...running cypher query:")
        for line in query:
            print("......|", line)

    # --------------------------------------------------------------------------
    # Put together the parameters
    # --------------------------------------------------------------------------
    params = {}
    params['rows'] = df.to_dict('records')

    # --------------------------------------------------------------------------
    # Run the query
    # --------------------------------------------------------------------------
    result = graph.session().run(" ".join(query), parameters=params)
    print("...result count of relationship properties set:", result.peek())

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return result

 
## # ------------------------------------------------------------------------------
## # 
## # ------------------------------------------------------------------------------
## def graph_file_system(graph, root_dir, date_cfg):
##     # --------------------------------------------------------------------------
##     # Start
##     # --------------------------------------------------------------------------
##     print("...mapping file system from root directory " + root_dir + "...")
## 
##     # --------------------------------------------------------------------------
##     # Set the kinds of relationships that will be used
##     # --------------------------------------------------------------------------
##     SUBDIR_OF    = Relationship.type("SUBDIR_OF")
##     FILE_WITHIN  = Relationship.type("FILE_WITHIN")
##     FILE_OF_TYPE = Relationship.type("FILE_OF_TYPE")
##     ON_DAY       = Relationship.type("ON_DAY")
## 
##     # --------------------------------------------------------------------------
##     # Make the node for the root directory
##     # --------------------------------------------------------------------------
##     rel_root        = "\\" + os.path.basename(root_dir)
##     abs_parent_root = os.path.dirname(root_dir)
## 
##     n = Node("dir", ref=root_dir)
##     n['abs_dir']        = root_dir
##     n['rel_dir']        = rel_root
##     n['abs_parent_dir'] = abs_parent_root
##     n['rel_parent_dir'] = ""
## 
##     graph.merge(n, "dir", "ref")
## 
##     # --------------------------------------------------------------------------
##     # Walk down through the directory structure
##     # --------------------------------------------------------------------------
##     for root, dirs, files, in os.walk(root_dir):
##         # ----------------------------------------------------------------------
##         # Get the absolute and relative paths of the directory and its parent
##         # ----------------------------------------------------------------------
##         abs_dir         = root
##         rel_dir         = os.path.join(rel_root, root.replace(abs_parent_root, ""))
##         abs_parent_dir  = os.path.dirname(root)
##         rel_parent_dir  = os.path.dirname(root).replace(abs_parent_root, "")
## 
##         # ----------------------------------------------------------------------
##         # Make the node for this directory, if it's not the root
##         # ----------------------------------------------------------------------
##         if rel_parent_dir:
##             n = Node("dir", ref=abs_dir)
##             n['abs_dir']        = abs_dir
##             n['rel_dir']        = rel_dir
##             n['abs_parent_dir'] = abs_parent_dir
##             n['rel_parent_dir'] = rel_parent_dir
## 
##             g = graph.merge(n, "dir", "ref")
## 
##         # ----------------------------------------------------------------------
##         # Get the current and parent node
##         # ----------------------------------------------------------------------
##         cnode = graph.nodes.match("dir", ref=abs_dir       ).first()
##         pnode = graph.nodes.match("dir", ref=abs_parent_dir).first()
## 
##         # ----------------------------------------------------------------------
##         # Tie this directory to its parent
##         # ----------------------------------------------------------------------
##         if rel_parent_dir:
##             g = graph.merge(SUBDIR_OF(cnode, pnode))
## 
##         # ----------------------------------------------------------------------
##         # Go through each file in the directory
##         # ----------------------------------------------------------------------
##         for fname in files:
##             # ------------------------------------------------------------------
##             # Construct the paths
##             # ------------------------------------------------------------------
##             abs_fpath = os.path.join(root, fname)
##             rel_fpath = os.path.join(root, fname).replace(abs_parent_root, "")
## 
##             # ------------------------------------------------------------------
##             # Get the date/time of the file and the size
##             # ------------------------------------------------------------------
##             fstat = os.stat(abs_fpath)
##             fsize = int(fstat.st_size)
##             ftime = datetime.fromtimestamp(fstat.st_mtime)
## 
##             # ------------------------------------------------------------------
##             # Make the node for this file
##             # ------------------------------------------------------------------
##             n = Node("file", ref=abs_fpath)
##             n['abs_fpath'] = abs_fpath
##             n['rel_fpath'] = rel_fpath
##             n['file_date'] = ftime
##             n['file_size'] = fsize
## 
##             g = graph.merge(n, "file", "ref")
## 
##             # ------------------------------------------------------------------
##             # Get the nodes for this file and the directory it's in
##             # ------------------------------------------------------------------
##             cnode = graph.nodes.match("file", ref=abs_fpath  ).first()
##             pnode = graph.nodes.match("dir" , ref=abs_dir    ).first()
## 
##             # ------------------------------------------------------------------
##             # Tie this file to its directory
##             # ------------------------------------------------------------------
##             g = graph.merge(FILE_WITHIN(cnode, pnode))
## 
##             # ------------------------------------------------------------------
##             # Tie the file to the date, if we are tracking them
##             # ------------------------------------------------------------------
##             if date_cfg:
##                 # --------------------------------------------------------------
##                 # Get the string version of the date which will be used as the
##                 # node name as the default
##                 # --------------------------------------------------------------
##                 date_as_str = ftime.strftime('%Y-%m-%d')
## 
##                 date_node_name = date_as_str
## 
##                 # --------------------------------------------------------------
##                 # Maybe override as prior to the specified starting date
##                 # --------------------------------------------------------------
##                 if 'start_date' in date_cfg:
##                     if ftime < date_cfg['start_date']:
##                         date_node_name = date_cfg['past_node']
## 
##                 # --------------------------------------------------------------
##                 # If the date is already there, tie to it; if not, make it
##                 # --------------------------------------------------------------
##                 dnode = match_make_node(graph, "day", date_node_name)
##                 g = graph.merge(ON_DAY(cnode, dnode))
## 
##                 #print("DATES AS NODES", date_as_str, date_node_name)
## 
##             # ------------------------------------------------------------------
##             # If the file type is detectable, tie it to that; make a node for
##             # the type if it's not already there.
##             # ------------------------------------------------------------------
##             fext = os.path.splitext(fname)[1]
##             if not fext:
##                 fext = "(bare)"
## 
##             tnode = match_make_node(graph, "file_type", fext)
## 
##             #tnode = graph.nodes.match("file_type", ref=fext).first()
##             #if not tnode:
##             #    n = Node("file_type", ref=fext)
##             #    graph.merge(n, "file_type", "ref")
##             #    tnode = graph.nodes.match("file_type", ref=fext).first()
## 
##             g = graph.merge(FILE_OF_TYPE(cnode, tnode))
## 
##     # --------------------------------------------------------------------------
##     # Finish
##     # --------------------------------------------------------------------------
##     return rel_root
## 
## # ------------------------------------------------------------------------------
## # 
## # ------------------------------------------------------------------------------
## def build_mesh(graph, ntype, size_x, size_y):
##     # --------------------------------------------------------------------------
##     # Start
##     # --------------------------------------------------------------------------
##     for x in range(size_x):
##         for y in range(size_y):
##             print(x,y)
## 
##     # --------------------------------------------------------------------------
##     # Finish
##     # --------------------------------------------------------------------------
##     return True
## 
## # ------------------------------------------------------------------------------
## # Given a list of items, match/make each item and tie them in a sequence using
## # a verb.  Possible to tie the last back to the first to create a closed loop
## # ------------------------------------------------------------------------------
## def linked_list_in_graph(graph, node_type, source_list, verb, oroborous=False, props={}):
##     # --------------------------------------------------------------------------
##     # Set up the constant for the relationship
##     # --------------------------------------------------------------------------
##     VERB = Relationship.type(verb.upper())
## 
##     # --------------------------------------------------------------------------
##     # Go through each item in the list
##     # --------------------------------------------------------------------------
##     for i, item in enumerate(source_list):
##         # ----------------------------------------------------------------------
##         # Get/make the node
##         # ----------------------------------------------------------------------
##         anode = match_make_node(graph, node_type, item)
## 
##         # ----------------------------------------------------------------------
##         # Attach the previous node to this one
##         # ----------------------------------------------------------------------
##         if i > 0:
##             pnode = match_make_node(graph, node_type, source_list[i-1])
##             x = add_relationship(graph, pnode, anode, verb, props=props)
## 
##     # --------------------------------------------------------------------------
##     # Close the loop if requested
##     # --------------------------------------------------------------------------
##     if oroborous and len(source_list)>1:
##         fnode = match_make_node(graph, node_type, source_list[0])
##         lnode = match_make_node(graph, node_type, source_list[-1])
##         x = add_relationship(graph, fnode, lnode, verb, props=props)
## 
##     # --------------------------------------------------------------------------
##     # Finish
##     # --------------------------------------------------------------------------
##     return True
## 


# ------------------------------------------------------------------------------
# We want a node that represents a run of whatever application in the db
# It can connect to the previous instances of itself and whatever other
# applications are passed in
# ------------------------------------------------------------------------------
def make_session_instance(graph, app_name, props={}, other_apps=[]):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    print(f"...adding new instance of {app_name} to database...")

    # --------------------------------------------------------------------------
    # Get whatever instances there already are and keep a count of them
    # --------------------------------------------------------------------------
    anodes = [x for x in graph.session().run(f"MATCH (a:{app_name}) RETURN a")]
    existing = len(anodes)
    print(f"...found {existing} previous runs...")

    # --------------------------------------------------------------------------
    # What are the IDs of this one and the hypothetical last one
    # --------------------------------------------------------------------------
    prev_run_id = f"{app_name} round: " + str(existing)
    this_run_id = f"{app_name} round: " + str(existing + 1)

    # --------------------------------------------------------------------------
    # Check for IDs of previous runs of any other apps being tracked
    # --------------------------------------------------------------------------
    prev_other = {}
    for other_app in other_apps:
        # ----------------------------------------------------------------------
        # What is the ID of the last run if there is one?
        # ----------------------------------------------------------------------
        pnodes = [x['idx'] for x in get_existing_nodes(graph, ntype=other_app)]
        existing_p = len(pnodes)

        pnodes = sort_strings_by_numeric_suffix(pnodes)

        if existing_p:
            prev_other[other_app] = pnodes[-1]

    # --------------------------------------------------------------------------
    # Set up the node information for this one
    # --------------------------------------------------------------------------
    anode = {}
    anode['label'] = app_name
    anode['index'] = this_run_id

    anode['props'] = {}
    anode['props']['created']  = "{TIMESTAMP}"
    for prop in props:
        anode['props'][prop] = props[prop]

    anode['rels'] = {}
    if existing > 0:
        anode['rels']['prev'] = {}
        anode['rels']['prev']['from']  = (app_name, prev_run_id)
        anode['rels']['prev']['verb']  = f"NEXT_{app_name}"
    if prev_other:
        for other in prev_other:
            anode['rels'][other] = {}
            anode['rels'][other]['to']    = (other,prev_other[other])
            anode['rels'][other]['verb']  = f"LAST_{other}"

    # --------------------------------------------------------------------------
    # Add the node, with the connection to the previous one if there.
    # --------------------------------------------------------------------------
    x = create_single_node(graph, anode, constrain=True)

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    print(f"...node for this run added as {this_run_id}")
    return this_run_id
