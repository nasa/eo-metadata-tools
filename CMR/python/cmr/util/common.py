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
date 2020-10-26
since 0.0
"""

import os
import subprocess
from datetime import datetime

def conj(coll, to_add):
    """
    Similar to clojure's function, add items to a list or dictionary

    See https://clojuredocs.org/clojure.core/conj for more reading

    Returns a new collection with the to_add 'added'. conj(None, item) returns
    (item).  The 'addition' may happen at different 'places' depending on the
    concrete type. if coll is:
    [] - appends            [1, 2, 3, 4] == conj([1, 2], [3, 4])
    () - prepend in reverse ((4, 3, 1, 2) == conj((1, 2), (3, 4))
    {} - appends            {'a': 'A', 'b': 'B'} == conj({'a':'A'}, {'b':'B'})

    Parameters:
        coll: collection to add items to
        to_add: items to be added to coll
    Return:
        object of the same type as coll but with to_add items added
    """
    ret = coll
    if coll is None:
        ret = to_add
    elif isinstance(coll, list):
        ret = coll + to_add
    elif isinstance(coll, tuple):
        ret = list([])
        for item in coll:
            ret.append(item)
        for item in to_add:
            ret.insert(0, item)
        ret = tuple(ret)
    elif isinstance(coll, dict):
        ret = {}
        for key in coll:
            ret[key] = coll[key]
        for key in to_add:
            if key not in ret:
                ret[key] = to_add[key]
    return ret

def always(obj: dict, otype = dict):
    """
    Ensure that something is always returned. Assumes dictionary, but list or
    tuple can be specified, because source may be none, it can not be derived
    Parameters:
        obj: a dictionary, list, or tuple
        otype: object type, the actual type `dict` (default), `list`, or `tuple`
    Returns:
        {}, [], or () as needed, or the object that was passed in if it already exists
    """
    if otype == dict:
        obj = obj if isinstance(obj, dict) else {}
    elif otype == list:
        obj = obj if isinstance(obj, list) else []
    elif otype == tuple:
        obj = obj if isinstance(obj, tuple) else ()
    return obj

def drop_key_safely(dictionary, key):
    """Drop a key from a dict if it exists and return that change"""
    if key in dictionary:
        del dictionary[key]
    return dictionary


def read_file(path):
    """
    Read and return the contents of a file
    Parameters:
        path (string): full path to file to read
    Returns:
        None if file was not found, contents otherwise
    """
    text = None
    if os.path.isfile(path):
        with open(path, "r") as file:
            text = file.read().strip()
            file.close()
    return text

def write_file(path, text):
    """
    Write (creating if need be) file and set it's content
    Parameters:
        path (string): path to file to write
        text (string): content for file
    """
    path = os.path.expanduser(path)
    with open(path, "w+") as cache:
        cache.write(text)
        cache.close()

def execute_command(cmd):
    """
    A utility method to execute a shell command and return a string of the output
    Parameters:
        cmd(string) unix command to execute
    Returns:
        response from command
    """
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return result.stdout.decode('utf-8')

def call_security(account, service, app="/usr/bin/security"):
    """Call the security command to look up encrypted values"""
    cmd = [app, "find-generic-password", "-a", account, "-s", service, "-w"]
    result = execute_command(cmd)
    if result is not None:
        result = result.strip()
    else:
        raise TypeError("account not found in keychain")
    return result

def help_format_lambda(contains=""):
    """
    Return a lambda to be used to format help output for a function
    """
    layout = "\n{}:\n{}\n"
    # n=name, c=content ; made short to keep line length down and pylint happy
    out = lambda n, c : (layout.format(n, c.__doc__.strip())) if contains in n else ""
    return out

def mask_string(unsafe_value):
    """Prevent sensitive information from being printed by masking values """
    if unsafe_value is None:
        return ""
    mask = int(len(unsafe_value)/3)
    return unsafe_value[:mask] + ("*"*mask) + unsafe_value[-1*mask:]

def mask_dictionary(data, keys):
    """
    Prevent sensitive information from being printed by masking values of listed
    keys in a dictionaries. The middle third of the values will be replaced with
    '*'. Uses Dictionaries copy() function.
    Return a shallow copy of the data dictionary that has been updated
    """
    if isinstance(keys, str):
        keys = [keys]
    safe_data = data.copy()
    for key in keys:
        if key in data:
            unsafe_value = data.get(key, "")
            mask = int(len(unsafe_value)/3)
            safe_data[key] = unsafe_value[:mask] + ("*"*mask) + unsafe_value[-1*mask:]
    return safe_data

def now():
    """
    return the current time in a function that can be patched away for testing
    """
    return datetime.now()
