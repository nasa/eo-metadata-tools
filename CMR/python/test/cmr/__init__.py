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
Classes and functions defined here are for use as utilities in tests.
Created: 2020-10-26
since: 0.0.0
"""

import os
import json

class MockResponse():
    """
    Mock up a Response object like what would be returned from
    `urllib.request.urlopen()`. Respond to a read() request.
    """
    def __init__(self, result, status=200, headers=()):
        self.result = result
        self.status = status
        self.headers = headers
    def read(self):
        """Respond to the read request and return a stream"""
        return MockStream(self.result)
    def get_result(self):
        """Return the internal result ; silence PEP8 R0903"""
        return self.result
    def getheaders(self):
        """Return headers"""
        return self.headers
class MockStream():
    """
    Mock up a Stream object like what would be returned from a read() method.
    """
    def __init__(self, result):
        self.result = result
    def decode(self, _):
        """ Just return the result """
        return self.result
    def get_result(self):
        """ return the internal result ; silence PEP8 R0903 """
        return self.result

# note, this read_file() is from cmr.util.common, but it should not be imorted
# because tests have not proven the file yet

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
        with open(path, 'r', encoding='utf-8') as file:
            text = file.read().strip()
            file.close()
    return text

def delete_file(path):
    """ A basic delete file function for use by tests that need to clean up """
    if os.path.isfile(path):
        os.remove(path)

def resolve_full_path(relative_file_path):
    """ find a relative file and return it's json object based on the content """
    full_file_path = os.path.join (os.path.dirname(__file__), relative_file_path)
    return full_file_path

def load_relative_file(relative_file_path):
    """ find a relative file and return it's json object based on the content """
    full_file_path = resolve_full_path(relative_file_path)
    content = read_file(full_file_path)
    return content

def load_relative_json_file(relative_file_path : str):
    """ find a relative file and return it's json object based on the content """
    content = json.loads(load_relative_file(relative_file_path))
    return content
