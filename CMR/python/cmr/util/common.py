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

from enum import Enum # requires Python 3.4
import os
import subprocess

def enum_value(value):
    """ Get a value either directly or from an Enum """
    if isinstance(value, Enum):
        value = value.value
    return value

def drop_key_safely(dictionary, key):
    """drop a key from a dict if it exists and return that change"""
    if key in dictionary:
        del dictionary[key]
    return dictionary

def dict_or_default(dictionary, key, default):
    """
    return the contents of a dictionary pointed to with a key, or a default
    value. The default can either be a raw value or a pointer to a function
    that will return the default
    dictionary(dictionary)= thing to check
    key(string)= index in dictionary to look for
    default(string/lambda)= text or function that gets text to use if value does not exist
    """
    if dictionary is None:
        dictionary = {}
    if key in dictionary:
        ret = dictionary[key]
    else:
        if hasattr(default, '__call__'):
            # Python > 3.2 way of doing things
            ret = default()
        else:
            ret = default
    return ret

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
        file = open(path, "r")
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
    cache = open(path, "w+")
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

def help_format_lambda(prefix=""):
    """
    Return a lambda to be used to format help output for a function
    """
    layout = "\n{}:\n{}\n"
    # n=name, c=content ; made short to keep line length down and pylint happy
    out = lambda n, c : (layout.format(n, c.__doc__.strip())) if n.startswith(prefix) else ""
    return out
