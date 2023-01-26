# NASA EO-Metadata-Tools Python interface for the Common Metadata Repository (CMR)
#
#     https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html
#
# Copyright (c) 2020 United States Government as represented by the Administrator
# of the National Aeronautics and Space Administration. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
"""
A utility script to scan through the projects python files looking for specially
formatted comments which denote where a configuration setting from the config
parameter has been consumed. These notations are then bubbled up to the public
methods that wish to advertise these settings and reported out in a markdown
file.

Script Usage:
    python3 docit.py -v -h
        -v for verbose
        -h for hidden functions

Documentation Tag:
Above, not below, the function definition, use add a single line comment for
every configuration the function uses. If function uses other functions which
use configurations, then use the 'from' syntax to have those docit strings
included.

    # document-it: {"key":"cmr-token", "default":"None"}
    # document-it: {"from":".cmr_basic_url"}
    def some_function(config=None):

In the first case, a function uses the setting 'cmr-token' which defaults to None
In the second case, the function reports to use a function in the same file
called 'cmr_basic_url()'. Provided a full module path if the function is not in
the same file.

date 2020-12-21
since 0.0
"""

# ##############################################################################
# Modules needed to do the work

import inspect
import json
from datetime import datetime

import cmr.util.common as common

# ##############################################################################
# Where to find the packages that are to be documented

import os
import sys
sys.path.append(os.path.expanduser('.'))

# ##############################################################################
# Load the modules that are to be documented, and do this after we add the
# path above

# pylint: disable=C0413
# pylint: disable=W0611
import cmr as cmr_mod
import cmr.util.common
import cmr.util.network
import cmr.auth.token
import cmr.search.common
import cmr.search.collection
import cmr.search.granule

# ##############################################################################
#mark - Constants - markdown line templates

DOCUMENT_IT = "# document-it:" #magic key to id comments this file is interested in

FORMAT_HEADER = "# Document-it report"
FORMAT_DOCIT_TEXT = "All the code 'document-it' tags are listed here by package"
FORMAT_FULL_NAME = "## `{}`\n"
FORMAT_FUNC = "### `{}()`\n"
FORMAT_LINE = "{}\n"
FORMAT_DOCIT_LINE2 = "`{}` (defaults to `{}`)."
FORMAT_DOCIT_LINE3 = "`{}` (defaults to `{}`). Notes: {}"
FORMAT_ALSO = "{}* also from `{}`"
FORMAT_ALSO_LINE = "{}* {}"
FORMAT_FOOTER = "----\nCMR Library - NASA - Copyright {}\nCreated {}"

# ##############################################################################
#mark - Utility functions

def now_iso():
    """ Return the current time (now) in an ISO style output """
    my_date = datetime.now()
    return my_date.strftime('%Y-%m-%d %H:%M:%S%z')

def today_iso():
    """ Return the current date (now) in an ISO style output """
    my_date = datetime.now()
    return my_date.strftime('%Y-%m-%d')

def add_to_tree_database(func_db:dict, key:str, value:str):
    """
    Adds a value to the list of values stored with the key. If no value exists
    for the key, then a new list is created and the value is appended to it.
        {key: [value,...]}
    Parameters:
        db: dictionary of key and value lists (changed by function)
        key: full module path and function name
        value: value to add to the list at the key
    """
    if not key in func_db:
        func_db[key] = []
    func_db[key].append(value)

def document_it_tag_to_str(raw_json):
    """
    Convert a json to a human readable string
    Parameters:
        raw_json: a JSON string or dictionary from JSON
    Returns:
        String formatted with FORMAT_DOCIT_LINE constant
    """
    if isinstance(raw_json, str):
        clean_json = json.loads(raw_json)
    else:
        clean_json = raw_json
    key = clean_json.get('key', '')
    default = clean_json.get('default', '')
    msg = clean_json.get('msg', '')
    if len(msg)<1:
        ret = FORMAT_DOCIT_LINE2.format(key, default)
    else:
        ret = FORMAT_DOCIT_LINE3.format(key, default, msg)
    return ret

def find_froms(func_db, out:list, data:dict, tab:str='    '):
    """
    Recursively search for references to doc-its from other functions
    Parameters:
        func_db: dictionary of functions
        module: current module being processed
        out: array of string which will make up the markdown output, one item is one line
        data: dictionary from docit tag
        tab: spaces to prefix each output line with
    """
    key = data['from']
    other_items = func_db.get(key, [])
    if len(other_items) > 0:
        out.append(FORMAT_ALSO.format(tab[2:], key))
        for others in other_items:
            if 'from' in others:
                find_froms(func_db, out, others, tab+'    ')
            else:
                txt = document_it_tag_to_str(others)
                out.append(FORMAT_ALSO_LINE.format(tab, txt))

def fix_local_from(module, data):
    """
    Look for a local from value and make it global by prepending the module name
    Parameters:
        module: a python module (not a string)
        data: dictionary of the document-it tag
    """
    if 'from' in data and data['from'].startswith('.'):
        data['from'] = module.__name__ + data['from']

def handle_function(func_db, module, out, obj_info, config):
    """
    Most of the work from tree is here, print out the documentation for a
    function
    Parameters:
        func_db: function database, all the functions and their doc-it strings
        module: module currently working on
        out: list of markdown strings to be sent as output
        obj_info: (object type, object)
        config: Configuration dictionary
    """
    func_name = obj_info[0]
    obj = obj_info[1]
    first = True
    comments = inspect.getcomments(obj)
    if comments is not None and len(comments) > 0:
        for raw_item in comments.strip().split("\n"):
            posible_item = raw_item.strip()
            if len(posible_item) < 1:
                continue
            if posible_item.startswith(DOCUMENT_IT):
                item = posible_item[len(DOCUMENT_IT):]
                if first:
                    # Function documentation is inserted herehere
                    out.append (FORMAT_FUNC.format(func_name))
                    if config.get('verbose', False) and obj.__doc__ is not None:
                        out.append (obj.__doc__)
                    if func_name in config:
                        out.append(config.get(func_name, '') + '\n')
                data = json.loads(item)

                if 'from' in data:
                    fix_local_from(module, data)
                    find_froms(func_db, out, data)
                else:
                    txt = document_it_tag_to_str(item)
                    out.append ("* {}".format( txt ))
                first = False
    if not first:
        out.append('')

def handle_builtins(out, obj_info, config:dict):
    """
    Handle the built-in use case
    Parameters:
        out: list of strings to be sent through print() as the markdown content
        obj_info: (object type, object)
        config: configuration dictionary, look for 'verbose'
    """
    obj_type = obj_info[0]
    obj = obj_info[1]
    if config.get('verbose', False) and obj.__doc__ is not None:
        out.append("* Global Dictionary - {}".format(obj_type))
        out.append (obj.__doc__)


# ##############################################################################
#mark - Public Functions

def pre_tree(func_db, module, config=None, cache=None):
    """
    Scan the modules ahead of time and make a map of all the documents-its for
    future use. Must be called before tree(). This database of functions will
    then be called by tree() to query and walk the 'froms'
    """
    config = common.always(config)
    cache = common.always(cache)
    if module.__name__ in cache:
        # Been here before, nothing to do
        return
    cache[module.__name__] = {'processed':True}
    for obj_type, obj in inspect.getmembers(module):
        if inspect.ismodule(obj):
            if obj.__package__.startswith(module.__package__):
                pre_tree(func_db, obj, config, cache)
        elif inspect.isfunction(obj):
            comments = inspect.getcomments(obj)
            if comments is not None and len(comments) > 0:
                for raw_item in comments.strip().split("\n"):
                    item = raw_item.strip()
                    if item.startswith(DOCUMENT_IT):
                        key = module.__name__ + "." + obj_type
                        value = json.loads(item[len(DOCUMENT_IT):])
                        fix_local_from(module, value)
                        add_to_tree_database(func_db, key, value)

def tree(report, func_db, module, config=None, cache=None):
    """
    Walk the module tree and create the mark down output
    Parameters:
        report: list of strings, output for print
        func_db: dictionary of known functions
        module: current module being processed
        config: settings
        cache: record of which modules have been processed
    """
    cache = cache if isinstance(cache, dict) else {}
    config = config if isinstance(config, dict) else {}
    if module.__name__ in cache:
        return
    cache[module.__name__] = {'processed':True}

    head = []   # text for the top of the page
    post = []   # text of sub modules
    out = []

    if config.get('verbose', False) and module.__doc__ is not None:
        head.append(module.__doc__)
    head.append(FORMAT_FULL_NAME.format(module.__name__))

    for obj_info in inspect.getmembers(module):
        obj_type = obj_info[0]
        obj = obj_info[1]
        if inspect.ismodule(obj) and obj.__package__.startswith(module.__package__.split('.')[0]):
            # recursively call these latter
            post.append(obj)
        elif obj_type == '__version__':
            out.append(FORMAT_FULL_NAME.format("API Version"))
            out.append(FORMAT_LINE.format(obj))
        elif inspect.ismodule(obj) or inspect.isbuiltin(obj):
            continue
        elif inspect.isfunction(obj):
            hide_private = not config.get('show-private', False)
            if hide_private and obj_type.startswith("_") and (not obj_type.startswith("__")):
                continue
            handle_function(func_db, module, out, obj_info, config)
        elif isinstance(obj, dict) and obj_type != '__builtins__':
            handle_builtins(out, obj_info, config)
        elif not obj_type in ['__builtins__',
            '__cached__',
            '__doc__',
            '__file__',
            '__loader__',
            '__name__',
            '__package__',
            '__path__',
            '__spec__',
            'Callable',
            'logger',
            'datetime']:
            out.append ("unknown: {} {}".format(obj_type, obj))
    if len(out) > 0:
        report.append ("\n".join(head))
        report.append ("\n".join(out))

    for sub_module in post:
        tree(report, func_db, sub_module, config, cache)

# ##############################################################################
#mark - Command line interface

def show_help():
    """ Print out a help message to the command line """
    fmt = "{:>4} {:<14}{:<10} - {:8} {}"
    print (fmt.format('flag', 'long flag', 'Option', 'Default', 'Description'))
    print (fmt.format('----', '-------------', '------', '--------', '------------'))
    print (fmt.format('-f', '--flag', 'name:value', '', 'Hide private functions'))
    print (fmt.format('-d', '--dump', 'none', '', 'Dump out the internal function db'))
    print (fmt.format('-h', '--help', 'none', '', 'This help message'))
    print (fmt.format('-p', '--private-on', 'none', '', 'Show private functions'))
    print (fmt.format('-P', '--private-off', 'none', 'yes', 'Hide private functions'))
    print (fmt.format('-v', '--verbose', 'none', '', 'Include more details'))
    print (fmt.format('-q', '--quiet', 'none', 'yes', 'Show less details'))

def dump(func_db:dict, config:dict):
    """
    Dump out the function database for debugging if config has an active setting
    Parameters:
        func_db: function database to dump out
        config: check the dump setting to test if option is active
    """
    if config.get('dump', False):
        print (json.dumps(func_db, indent=4))

def main():
    """ It's the main function, response to launches from command line """
    config = {}
    for index, arg in enumerate(sys.argv):
        next_arg = sys.argv[index + 1] if len(sys.argv)>index + 1 else None
        if arg in ('-d', '--dump'):
            config['dump'] = True
        if arg in ('-p', '--private-on'):
            config['show-private'] = True
        elif arg in ('-P', '--private-off'):
            config['show-private'] = False
        elif arg in ('-v', '--verbose'):
            config['verbose'] = True
        elif arg in ('-q', '--quiet'):
            config['verbose'] = False
        elif (arg in ('-f', '--flag')) and next_arg is not None:
            parts = next_arg.split(":")
            config[parts[0]] = parts[1]
        elif arg in ('-h', '--help'):
            show_help()
            sys.exit()

    function_database = {}
    pre_tree(function_database, cmr_mod, config)

    report = [FORMAT_HEADER, FORMAT_DOCIT_TEXT]

    for key in config:
        if key.startswith('header-'):
            report.append("{}: {}".format(key[7:], config.get(key)))

    tree(report, function_database, cmr_mod, config)
    report.append(FORMAT_FOOTER.format(today_iso(), now_iso()))

    for key in config:
        if key.startswith('footer-'):
            report.append("{}: {}".format(key[7:], config.get(key)))

    print ( "\n".join(report) )
    dump(function_database, config)

if __name__ == '__main__':
    main()
