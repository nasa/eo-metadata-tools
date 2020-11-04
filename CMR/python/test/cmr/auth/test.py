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
#Test cases for the cmr.auth package
#date 2020-10-15
#since 0.0

from unittest.mock import Mock
from unittest.mock import patch
import json
import unittest
import urllib.error as e

import test.cmr as util
import cmr.auth.token as t

# ******************************************************************************

# **********************************************************************
# Util methods

def login_response(client, edl_id, address, name):
    """return a raw json response that cmr would return on successful login"""
    data = {"token": {
        "client_id": client,
        "id": edl_id,
        "user_ip_address": address,
        "username": name}}
    return json.dumps(data)

def valid_login_response():
    """return a valid login response"""
    json_response = login_response('python_cmr_lib', 'fake-token', '127.0.0.1', 'Test.User')
    return util.MockResponse(json_response)

class TestToken(unittest.TestCase):
    """ Test suit for cmr.auth.token """


    # **********************************************************************
    # Tests

    def test_url(self):
        """ test how CMR urls are built """
        # pylint: disable=W0212
        self.assertEqual("https://cmr.sit.earthdata.nasa.gov/legacy-services/rest/tokens.json",
            t._cmr_url(t.sit()))
        self.assertEqual("https://cmr.uat.earthdata.nasa.gov/legacy-services/rest/tokens.json",
            t._cmr_url(t.uat()))
        self.assertEqual("https://cmr.earthdata.nasa.gov/legacy-services/rest/tokens.json",
            t._cmr_url(t.prod()))

    def test_age(self):
        """ test the function used to judge if a file is too old to use """
        # pylint: disable=W0212
        self.assertEqual(True, t._days_old_from_time(1))
        self.assertEqual(False, t._days_old_from_time(86400, 86400))
        self.assertEqual(False, t._days_old_from_time(86400, 86400, 1.0))
        self.assertEqual(False, t._days_old_from_time(86400, 86400*2, 1.0))
        self.assertEqual(True, t._days_old_from_time(86400, 86400*2+1, 1.0))
        self.assertEqual(True, t._days_old_from_time(86400, 86400*3, 1.0))
        self.assertEqual(False, t._days_old_from_time(86400, 86400*3, 2.0))
        self.assertEqual(True, t._days_old_from_time(86400, 86400*4, 2.0))

    def test_password(self):
        """Test the password pass through function"""
        pass_func = t.password("test")
        self.assertEqual(pass_func("foo", {}), "test")
        self.assertEqual(pass_func("", {}), "test")
        self.assertEqual(pass_func(None, {}), "test")

    @patch('urllib.request.urlopen')
    def test_token(self, urlopen_mock):
        """Test a valid login using the clear text password lambda"""
        options = {'cache.token': False, 'client.address':'127.0.0.1'}
        pfunc = t.password("Text-Password")
        self.assertEqual ("Text-Password", pfunc("Test.User", options))

        urlopen_mock.return_value = valid_login_response()
        actual = t.token("Test.User", t.password("Text-Password"), options)
        self.assertEqual('fake-token', actual)

    @patch('urllib.request.urlopen')
    @patch('cmr.auth.token._read_file')
    def test_password_file(self, read_mock, urlopen_mock):
        """Test a valid login using the password file lambda"""
        user = "Test.User"
        expected_password = "File-Password"
        options = {'cache.token': False, 'client.address':'127.0.0.1'}
        read_mock.return_value = expected_password
        self.assertEqual (expected_password, t.password_file(user, options))

        urlopen_mock.return_value = valid_login_response()
        actual = str(t.token(user, t.password_file, options))
        self.assertEqual ("fake-token", actual)

    @patch('urllib.request.urlopen')
    @patch('cmr.auth.token._execute_command')
    def test_password_manager(self, cmd_mock, urlopen_mock):
        """test a valid login using the password manager"""
        user = "Test.User"
        expected_password = "Secure-Password"
        options = {'cache.token': False, 'client.address':'127.0.0.1'}
        cmd_mock.return_value = expected_password
        self.assertEqual(cmd_mock.return_value, t.password_manager(user, options))

        urlopen_mock.return_value = valid_login_response()
        actual = str(t.token(user, t.password_manager, options))
        self.assertEqual ('fake-token', actual)

    @patch('urllib.request.urlopen')
    def test_bad_login(self, urlopen_mock):
        """Test an invalid login"""
        options = {'cache.token': False, 'client.address':'127.0.0.1'}
        urlopen_mock.side_effect = e.HTTPError(Mock(status=422), "422",
            "Unprocessable Entity", None, None)
        expected = 'HTTP Error 422: Unprocessable Entity'
        actual = str(t.token("Test.User", t.password("test"), options))
        self.assertEqual (expected, actual)

if __name__ == '__main__':
    unittest.main()
    #unittest.main(warnings='ignore')
