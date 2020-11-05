"""
NASA EO-Metadata-Tools Python interface for the Common Metadata Repository (CMR)

    https://github.com/nasa/Common-Metadata-Repository/

Copyright (c) 2020 United States Government as represented by the Administrator
of the National Aeronautics and Space Administration. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

#date 2020-10-26
#since 0.0

import os
import subprocess

def dict_or_default(dictionary, key, default):
    """
    return the contents of a dictionary pointed to with a key, or a default
    value. The default can either be a raw value or a pointer to a function
    that will return the default
    dictionary(dictionary)= thing to check
    key(string)= index in dictionary to look for
    default(string/lambda)= text or function that gets text to use if value does not exist
    """
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
