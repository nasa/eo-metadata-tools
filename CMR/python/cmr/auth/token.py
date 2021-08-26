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
A Library for managing EDL tokens to be used with CMR
date: 2020-10-26
since: 0.0

Overview:
    The function fetch_bearer_token_with_password(user, password, config) will
    handle all network calls to either get or generate a user token and place
    this token inside a config dictionary for use in all other calls.

    The function token(lambda_list, config) will iterate over a list of token
    managers and return the value from the first manager that finds a token.

    Token Managers are lambda functions that take in a 'config' dictionary for
    use as a source for configurations, and returns a token as a string.
"""

import os
import subprocess
import base64 as b64
from datetime import datetime

import cmr.util.common as common
import cmr.util.network as net

# ##############################################################################
#mark - lambdas

# All password lambda functions accept two parameters and return a string
# Parameters:
#   user_id: string - Earth Data Login user name
#   config: dictionary - configuration object which may be used by the lambda
# Returns:
#   password: string

def token_literal(token_text: str):
    """
    Generates an token lambda file which always returns the same value, this is
    used for testing, and also as an example of how to write token managers
    Parameters:
        token_text(string): the token which should always be returned by the lambda
    Return:
        A lambda function which takes a dictionary and returns a token
    """
    return lambda _ : token_text


# document-it: {"key":"cmr.token.value", "default":"None"}
def token_config(config: dict = None):
    """
    Pull a token from the configuration dictionary
    Parameters:
        config: Responds to:
            "cmr.token.value": value of token, defaults to 'None'
    """
    config = common.always(config)
    value = config.get('cmr.token.value', None)
    return value

# document-it: {"from":".token_file_path"}
def token_file(config: dict = None):
    """
    Load a token from a local user file assumed to be ~/.cmr_token
    Parameters:
        config: Responds to:
            "cmr.token.file": location of token file, defaults to ~/.cmr_token
                for production, followed by a dot and the environment name if
                specified.
            "env": if not production, appended to the end of ~/.cmr_token with a dot
    Returns
        token from file
    """
    path_to_use = _token_file_path(config)

    path = os.path.expanduser(path_to_use)
    clear_text = None
    raw_clear_text = common.read_file(path)
    if raw_clear_text is not None:
        for line in raw_clear_text.splitlines():
            if not line.startswith("#"):
                clear_text = line
                break # we only need the first one
    return clear_text

# document-it: {"key":"token.manager.account", "default":"user"}
# document-it: {"key":"token.manager.service", "default":"cmr-lib-token"}
# document-it: {"key":"token.manager.app", "default":"/usr/bin/security"}
def token_manager(config: dict = None):
    """
    Use a system like the MacOS X Keychain app. Any os which also has the
    security app would also work.
    Parameters:
        config: Responds to the following:
            'token.manager.account': account field in Keychain
            'token.manager.app': Keychain command - defaults to /usr/bin/security
            'token.manager.service' defaults to 'cmr-lib-token'
    Returns:
        token from Keychain
    """
    try:
        config = common.always(config)
        account = config.get('token.manager.account', 'user')
        service = config.get('token.manager.service', 'cmr-lib-token')
        app = config.get('token.manager.app', '/usr/bin/security')
        result = common.call_security(account, service, app)
    except subprocess.CalledProcessError:
        result = None
    return result

# ##############################################################################
#mark - internal functions

# document-it: {"key":"env", "default":"", "msg":"uat, ops, prod, production, or blank for ops"}
def _env_to_extention(config: dict = None):
    """
    Allow different files to be loaded for each environment, make an env
    extension which will be appended to the token file path
    Parameters:
        config dictionary containing an env value
    Return:
        empty string or a dot followed by the environment.
    """
    config = common.always(config)

    env = config.get('env', '')
    if env is None:
        env = ''
    env = env.lower().strip()
    if len(env)>0 and env.endswith("."):
        env = env[:-1]
    if env in ['', 'ops', 'prod', 'production']:
        env = "" # no extension
    else:
        env = "." + env
    return env

# document-it: {"key":"env", "default":"", "msg":"uat, ops, prod, production, or blank for ops"}
def _env_to_edl_url(endpoint, config: dict = None):
    """
    Pull out parameters from the config and build an EDL endpoint URL

    Parameters:
        endpoint: part of the URL after 'api/users' such as token, tokens, revoke_token
        config: responds to 'env'
    Return: URL
    """
    config = common.always(config)

    env = config.get('env', '')
    if env is None:
        env = ''
    env = env.lower().strip()
    if env in ['', 'ops', 'prod', 'production']:
        env = "" # no extension

    url = 'https://{}.urs.earthdata.nasa.gov/api/users/{}'.format(env, endpoint)
    url = url.replace("://.urs", "://urs")

    return url

# document-it: {"key":"cmr.token.file", "default":"~/.cmr_token"}
# document-it: {"from":"._env_to_extention"}
def _token_file_path(config: dict = None):
    """
    Return the path to the file which stores a CMR token. This path can be different
    for each environment if specified with the env config.
    Returns
        ~/.cmr_token<.env>, no env if production
    """
    config = common.always(config)
    env_extention = _env_to_extention(config)
    path_to_use = config.get('cmr.token.file', '~/.cmr_token' + env_extention)
    return path_to_use


def _base64_text(text):
    """ Returns a UTF-8 Base 64 encoded value of the input
    Parameters:
        text: raw text to encode
    Return:
        Base 64 encoded text in UTF-8 format
    """
    text_as_bytes = text.encode('utf-8')
    return b64.b64encode(text_as_bytes).decode('utf-8')

def _lamdba_list_always(token_lambdas, default_list = None):
    """
    Ensures that a list of lambda funtions is always returned. If the supplied
    value is valid, it is returned, otherwise the default value list is returned.
    If no default list is supplied that an internal default is used which returns
    token_file and token_config.
    Parameters:
        token_lambdas: a list of lambdas functions
        default_list: a list of lambdas functions
    Return:
        A list of lambda functions
    """
    if token_lambdas is None or len(token_lambdas)<1:
        if default_list is None or len(default_list)<1:
            default_list = [token_file,token_config]
        token_lambdas = default_list
    if not isinstance(token_lambdas, list):
        token_lambdas = [token_lambdas]
    return token_lambdas

def _format_as_bearer_token(raw_token):
    """
    Formats a token as a Bearer Token suitable for use by CMR
    Parameters:
        raw_token: string token value
    Return:
        Bearer Token ready for use with an HTTP header
    """
    return "Bearer {}".format(raw_token)
# ##############################################################################
#mark - public functions

def read_tokens(edl_user, token_lambdas = None, config:dict = None):
    """
    Read and return the EDL tokens for a given user. Using this function makes
    the assumption that your storing the EDL password in one of the token lambda
    handlers and not tokens themself. This can be overwritten in the config file
    if you plan to store both tokens and password.
    Parameters:
        edl_user: EDL User name
        token_lambda: a token lambda or a list of functions
        config: config dictionary to base new dictionary off of
    Returns:
        a dictionary like the following:
    {"hits": 1,
     "items": [{"access_token": "EDL-UToken-Content",
                "expiration_date": "10/31/2121"}]}
    """
    url = _env_to_edl_url("tokens", config)

    token_lambdas = _lamdba_list_always(token_lambdas, [token_manager, token_config])
    tokens = {}

    handler = token_lambdas.pop()
    if handler is None:
        # someone defined a bad list with a none in it
        tokens = read_tokens(edl_user, token_lambdas, config)
    else:
        pass_phrase = handler(config)
        if pass_phrase is None or len(pass_phrase) < 1:
            # handler did not create a valid token, try the next handler
            tokens = read_tokens(edl_user, token_lambdas, config)
        else:
            plain_text = "{}:{}".format(edl_user, pass_phrase)
            cipher_text = _base64_text(plain_text)
            encoded_credentials = "Basic {}".format(cipher_text)
            headers = {"Authorization" : encoded_credentials}
            tokens = net.get(url, None, headers=headers)
    return tokens

def create_token(edl_user, token_lambdas = None, config:dict = None):
    """
    Create and return a EDL token for a given user. Using this function makes
    the assumption that your storing the EDL password in one of the token lambda
    handlers and not tokens themself. This can be overwritten in the config file
    if you plan to store both tokens and password.
    Parameters:
        edl_user: EDL User name
        token_lambda: a token lambda or a list of functions
        config: config dictionary to base new dictionary off of
    Returns:
        a dictionary like the following:
        {"access_token": "EDL-UToken-Content",
         "token_type":"Bearer",
         "expiration_date": "10/31/2121"}
    """
    url = _env_to_edl_url("token", config)
    token_lambdas = _lamdba_list_always(token_lambdas, [token_manager, token_config])
    tokens = {}
    if len(token_lambdas)<1:
        return None
    handler = token_lambdas.pop()
    if  handler is None:
        # someone defined a bad list with a none in it
        tokens = create_token(edl_user, token_lambdas, config)
    else:
        pass_phrase = handler(config)
        if pass_phrase is None or len(pass_phrase) < 1:
            tokens = create_token(edl_user, token_lambdas, config)
        else:
            plain_text = "{}:{}".format(edl_user, pass_phrase)
            cipher_text = _base64_text(plain_text)
            encoded_credentials = "Basic {}".format(cipher_text)
            headers = {"Authorization" : encoded_credentials}
            tokens = net.post(url, None, headers=headers)
    return tokens

def delete_token(access_token, edl_user, token_lambdas = None, config:dict = None):
    """
    Delete a taken from EDL
    Return None if failed, otherwise EDL response
    """
    url = _env_to_edl_url("revoke_token", config)
    token_lambdas = _lamdba_list_always(token_lambdas, [token_manager, token_config])
    if len(token_lambdas)<1:
        return None
    handler = token_lambdas.pop()
    if  handler is None:
        # no handler so try again, remember pop() changed token_lambdas
        tokens = delete_token(access_token, edl_user, token_lambdas, config)
    else:
        pass_phrase = handler(config)
        if pass_phrase is None or len(pass_phrase) < 1:
            # no password so try again, remember pop() changed token_lambdas
            tokens = delete_token(access_token, edl_user, token_lambdas=token_lambdas,
                config=config)
        else:
            # Construct and issue request
            plain_text = "{}:{}".format(edl_user, pass_phrase)
            cipher_text = _base64_text(plain_text)
            encoded_credentials = "Basic {}".format(cipher_text)
            headers = {"Authorization" : encoded_credentials}
            response = net.post(url, "token=" + access_token, headers=headers)
            tokens = response
    return tokens

def fetch_token(edl_user, token_lambdas = None, config:dict = None):
    """
    Talk to EDL and pull out a token for use in CMR calls. To lookup tokens, an
    EDL User name and password will be sent over the network.
    Return: None or Access token
    """
    # get tokens
    token_results = read_tokens(edl_user, token_lambdas=token_lambdas.copy(), config=config)
    if token_results is None:
        return None
    if 'error' in token_results:
        return token_results
    if token_results['hits']<1:
        # no token exists, so create one and package it up in a way to match read_tokens
        created_token = create_token(edl_user, token_lambdas=token_lambdas.copy(), config=config)
        packaged_token = {'access_token' : created_token['access_token'],
            'expiration_date' : created_token['expiration_date']}
        token_results = {'hits': 1, 'items': [packaged_token]}
    token_list = token_results['items']
    #look for a valid token from the list
    for token_item in token_list:
        experation_date = datetime.strptime(token_item['expiration_date'], '%m/%d/%Y')
        if datetime.now() < experation_date:
            access_token = token_item['access_token']
            break
        #token has expired, delete it and try again
        delete_token(token_item['access_token'], edl_user, token_lambdas, config)
        access_token = fetch_token(edl_user, token_lambdas, config)
    return access_token

def fetch_bearer_token_with_password(edl_user, edl_password, config:dict = None):
    """
    This function is the fastest way to use this API, this call will run all
    other functions needed to either get or generate a token on the users behalf.
    Parameters:
        edl_user: user name in the Earth Data Login System
        edl_password: password in the Earth Data Login system
        config: configuration dictionary
    Returns:
        Success: config dict with 'authorization' key added
        Error: {'error': 'invalid_credentials', 'error_description':
            'Invalid user credentials', 'code': 401, 'reason': 'Unauthorized'}
    """
    return fetch_bearer_token(edl_user, token_lambdas=[token_literal(edl_password)], config=config)

def fetch_bearer_token(edl_user, token_lambdas = None, config:dict = None):
    """
    This function is the similar to fetch_bearer_token_with_password() but takes
    lambda lookup functions instead of a fixed password. This call will run all
    other functions needed to either get or generate a token on the users behalf.
    Parameters:
        edl_user: user name in the Earth Data Login System
        token_lambda: a token lambda or a list of functions
        config: configuration dictionary
    Returns:
        Success: config dict with 'authorization' key added
        Error: {'error': 'invalid_credentials', 'error_description':
            'Invalid user credentials', 'code': 401, 'reason': 'Unauthorized'}
    """
    if config is None:
        config = {}
    augmented_config = config.copy()
    token_value = fetch_token(edl_user, token_lambdas=token_lambdas, config=config)
    if 'error' in token_value:
        return token_value
    if token_value is not None and len(token_value)>0:
        bearer_token = _format_as_bearer_token(token_value)
        augmented_config["authorization"] = bearer_token
        return augmented_config
    return None

def use_bearer_token(token_lambdas = None, config:dict = None):
    """
    Create a new config dictionary, optionally based on a supplied one, and add
    the bearer token to the config object abstracting away as many details as
    possible.
    Parameters:
        token_lambda: a token lambda or a list of functions
        config: config dictionary to base new dictionary off of
    Returns:
        new config dictionary with Bearer token assigned as an 'authorization'
    """
    if config is None:
        config = {}
    augmented_config = config.copy()
    bearer_token = bearer(token_lambdas, config)
    augmented_config["authorization"] = bearer_token
    return augmented_config

def bearer(token_lambdas = None, config: dict = None):
    """
    Loops through the list of lambdas till a token is found. These lamdba functions
    return an EDL token which can be passed to Earthdata software to authenticate
    the user. To get a token, go to https://sit.urs.earthdata.nasa.gov/user_tokens
    Token is returned as a Bearer String

    Parameters:
        token_lambda: a token lambda or a list of functions
        config: Responds to no values
    Returns:
        the EDL Bearer Token from the token lambda
    """
    token_value = token(token_lambdas, config)
    if token_value is not None and len(token_value)>0:
        token_value = _format_as_bearer_token(token_value)
    return token_value

def token(token_lambdas = None, config: dict = None):
    """
    Loops through the list of lambdas till a token is found. These lamdba functions
    return an EDL token which can be passed to Earthdata software to authenticate
    the user. To get a token, go to https://sit.urs.earthdata.nasa.gov/user_tokens

    Parameters:
        token_lambda: a token lambda or a list of functions
        config: Responds to no values
    Returns:
        the EDL Token from the token lambda
    """
    if token_lambdas is None:
        token_lambdas = [token_file,token_config]
    if not isinstance(token_lambdas, list):
        token_lambdas = [token_lambdas]

    handler = token_lambdas.pop()
    edl_token = handler(config)
    if edl_token is None and len(token_lambdas)>0:
        edl_token = token(token_lambdas, config)
    return edl_token

def help_text(prefix: str = '') -> str:
    """
    Built in help - prints out the public function names for the token API
    Parameters:
        filter: filters out functions beginning with this text, defaults to all
    Returns:
        text ready to be passed to print()
    """
    formater = common.help_format_lambda(prefix)

    out = __doc__

    out += ('\n**** Functions:\n')
    for item in [help_text, token]:
        out += formater(item.__name__ + '()', item)

    out += '\n**** Token Lambdas:\n'
    for item in [token_literal, token_config, token_file, token_manager]:
        out += formater(item.__name__, item)
    return out
