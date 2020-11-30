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

# Test cases for the cmr.auth package
# Date: 2020-10-15
# Since: 0.0

from unittest.mock import patch
import unittest

import test.cmr as util
import cmr.auth.token as token
import cmr.util.common as common

# ******************************************************************************

class TestToken(unittest.TestCase):
    """ Test suit for cmr.auth.token """

    # **********************************************************************
    # Tests

    def test_token_literal(self):
        """
        Test the literal token manager function which returns a token lambda
        """
        expected = "some-token-value"

        # returns a valid token
        manager = token.token_literal(expected)
        actual = manager({})
        self.assertEqual(expected, actual)
        actual = manager(None)
        self.assertEqual(expected, actual)

        # returns no token
        manager = token.token_literal(None)
        actual = manager({})
        self.assertEqual(None, actual)

    def test_token_config(self):
        """ Test the manager which pulls token from the configuration object """
        expected = "some-token-value"

        actual = token.token_config(None)
        self.assertEqual(None, actual)

        actual = token.token_config({})
        self.assertEqual(None, actual)

        actual = token.token_config({'cmr.token.value':expected})
        self.assertEqual(expected, actual)

    def test_token_file(self):
        """
        Test a valid login using the password file lambda with caching on. This
        will require that the test be able to write to a temp directory
        """
        #setup
        token_file = "/tmp/__test_token_file__.txt"
        util.delete_file(token_file)
        expected_token = "file-token"
        common.write_file(token_file, expected_token)

        #tests
        options = {'cmr.token.file': token_file}
        self.assertEqual (expected_token, token.token_file(options))

        actual = str(token.token(token.token_file, options))
        self.assertEqual (expected_token, actual)

        actual_token = common.read_file(token_file)
        self.assertEqual(expected_token, actual_token)

        #cleanup
        util.delete_file(token_file)

    @patch('cmr.util.common.execute_command')
    def test_password_manager(self, cmd_mock):
        """ Test a valid login using the password manager """
        expected_token = "Secure-Token"
        options = {}
        cmd_mock.return_value = expected_token
        self.assertEqual(expected_token, token.token_manager(options))

        actual = str(token.token(token.token_manager, options))
        self.assertEqual (expected_token, actual)

    @patch('cmr.util.common.execute_command')
    def test_request_token_two_ways(self, cmd_mock):
        """
        Try to get the token using two different handlers. The file handler
        should fail fall back to the manager which will pass
        """
        options = {'cmr.token.file': "/tmp/__fake-file-never-existed.txt"}
        expected = "Secure-Token"
        cmd_mock.return_value = expected

        # try file first, then manager
        actual = token.token([token.token_manager,token.token_file], options)
        self.assertEqual(expected, actual)

        # try the other way around
        actual = token.token([token.token_file,token.token_manager], options)
        self.assertEqual(expected, actual)

    def test_help_full(self):
        """Test the built in help"""
        result_full = token.print_help()
        self.assertTrue (-1<result_full.find("token_file"))
        self.assertTrue (-1<result_full.find("token("))

    def test_help_less(self):
        """Test the built in help for filtering"""
        result_less = token.print_help("token_")
        self.assertTrue (-1<result_less.find("token_file"))
        self.assertFalse (-1<result_less.find("token()"))

if __name__ == '__main__':
    unittest.main()
