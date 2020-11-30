# NASA EO-Metadata-Tools Python interface for the Common Metadata Repository (CMR)
#
#     https://github.com/nasa/Common-Metadata-Repository/
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
A Library for managing EDL tokens to be used with CMR
date: 2020-10-26
since: 0.0

Overview:
    The function token(lambda_list, options) will iterate over a list of token
    managers and return the value from the first manager that finds a token.

    Token Managers are lambda functions that take in an 'options' dictionary for
    use as a source for configurations, and returns a token as a string.

"""

import os
import subprocess
import cmr.util.common as common

# ##############################################################################
# lambdas

# All password lambda functions accept two parameters and return a string
# Parameters:
#   user_id(string): Earth Data Login user name
#   options(dictionary): configuration object which may be used by the lambda
# Returns:
#   password

def token_literal(token_text):
    """
    Generates an token lambda file which always returns the same value, this is
    used for testing, and also as an example of how to write token managers
    Parameters:
        token_text(string): the token which should always be returned by the lambda
    Return:
        A lambda function which takes a dictionary and returns a token
    """
    return lambda _ : token_text

def token_config(options=None):
    """
    Pull a token from the configuration dictionary
    Parameters:
        options (dictionary): Responds to:
            "cmr.token.value": value of token, defaults to 'None'
    """
    return common.dict_or_default(options, "cmr.token.value", None)

def token_file(options=None):
    """
    Load a token from a local user file assumed to be ~/.cmr_token
    Parameters:
        options (dictionary): Responds to:
            "cmr.token.file": location of token file, defaults to ~/.cmr_token
    Returns
        token from file
    """
    path_to_use = common.dict_or_default(options, "cmr.token.file", "~/.cmr_token")
    path = os.path.expanduser(path_to_use)
    clear_text = common.read_file(path)
    return clear_text

def token_manager(options=None):
    """
    Use a system like the MacOS X Keychain app. Any os which also has the
    security app would also work.
    Parameters:
        options (dictionary): Responds to the following:
            'token.manager.account': account field in Keychain
            'token.manager.app': Keychain command - defaults to /usr/bin/security
            'token.manager.service' defaults to 'cmr-lib-token'
    Returns:
        token from Keychain
    """
    try:
        account = common.dict_or_default(options, "token.manager.account", "user")
        service = common.dict_or_default(options, "token.manager.service", "cmr-lib-token")
        app = common.dict_or_default(options, "token.manager.app", "/usr/bin/security")
        result = common.call_security(account, service, app)
    except subprocess.CalledProcessError:
        result = None
    return result

# ##############################################################################
# functions

def token(token_lambdas=None, options=None):
    """
    Recursively calls lambdas till a token is found
    Parameters:
        token_lambda: a token lambda or a list of functions
        options (dictionary): Responds to no options
    Returns:
        the EDL Token from the token lambda
    """

    if token_lambdas is None:
        token_lambdas = [token_file,token_config]
    if not isinstance(token_lambdas, list):
        token_lambdas = [token_lambdas]

    handler = token_lambdas.pop()
    edl_token = handler(options)
    if edl_token is None and len(token_lambdas)>0:
        edl_token = token(token_lambdas, options)
    return edl_token

def print_help(prefix=""):
    """
    Built in help - prints out the public function names for the token API
    Parameters:
        filter(string): filters out functions beginning with this text, defaults to all
    """
    formater = common.help_format_lambda(prefix)

    out = __doc__

    out += ("\n**** Functions:\n")
    for item in [print_help, token]:
        out += formater(item.__name__+"()", item)

    out += "\n**** Token Lambdas:\n"
    for item in [token_literal, token_config, token_file, token_manager]:
        out += formater(item.__name__, item)
    return out
