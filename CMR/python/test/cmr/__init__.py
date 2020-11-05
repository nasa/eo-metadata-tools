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

#Classes and functions defined here are for use as utilities in tests.
#Created: 2020-10-26
#since: 0.0.0

import os

class MockResponse():
    """
    Mock up a Response object like what would be returned from
    `urllib.request.urlopen()`. Respond to a read() request.
    """
    def __init__(self, result):
        self.result = result
    def read(self):
        """ Respond to the read request and return a stream """
        return MockStream(self.result)
    def get_result(self):
        """ return the internal result ; silence PEP8 R0903 """
        return self.result

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

def delete_file(path):
    """ A basic delete file function for use by tests that need to clean up """
    if os.path.isfile(path):
        os.remove(path)
