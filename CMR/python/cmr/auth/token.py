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
# Library for generating EDL tokens from CMR
# date: 2020-10-26
# since: 0.0

import json
import os
import time
import urllib.parse
import urllib.request

import cmr.util.common as common
import cmr.util.network as net

# ##############################################################################
# local utilities

SEC_PER_DAY = 86400.0

def _days_old_from_time(past_timestamp, current_timestamp=time.time(), age=1.0):
    """
    Tests if a difference between timestamps are old
    Parameters:
        past_timestamp(float): timestamp of file
        current_timestamp(float): default to now, timestamp
        age(float): defaults to 1.0, days old
    Returns:
        true if the file is older then age
    """
    days_old = (current_timestamp - past_timestamp)/SEC_PER_DAY
    return days_old > age

def _old_file(path):
    """
    non-pure function
    To get age of a file from today
    Parameters:
        path(string): path to file to test
    Returns:
        true if the file is older then one day
    """
    return _days_old_from_time(os.path.getmtime(path))

def _read_token_file(options=None):
    """
    Load a password from a local user file assuming ~/.password
    Parameters:
        options(dictionary): responds to 'cmr.token.file'
    Returns:
        content of token file, None if it does not exist
    """
    if options is None:
        options = {}
    raw_path = common.dict_or_default(options, "cmr.token.file", "~/.cmr_token")
    path = os.path.expanduser(raw_path)
    clear_text = None
    if os.path.isfile(raw_path):
        if not _old_file(path):
            clear_text = common.read_file(path)
    return clear_text

def _write_token_file(token_text, options=None):
    """
    Write out a token cache file
    Parameters:
        token_text (string) : content to write out
        options (dictionary): overrides, responds to 'cmr.token.file'
    """
    if options is None:
        options = {}
    token_path = common.dict_or_default(options, "cmr.token.file", "~/.cmr_token")
    common.write_file(token_path, token_text)

def _cmr_url(env):
    env = env if env=="" else env + "."
    url='https://cmr.{}earthdata.nasa.gov/legacy-services/rest/tokens.json'.format(env)
    return url

# ##############################################################################
# lambdas

# All password lambda functions accept two parameters and return a string
# Parameters:
#   user_id(string): Earth Data Login user name
#   options(dictionary): configuration object which may be used by the lambda
# Returns:
#   password

def password(clear_password):
    """
    Create a pass through lambda function to allow plain text passwords, not an
    encouraged act however
    Parameters:
        clear_password(string): password
    Returns:
        A lambda function with conforms to the definition
    """
    return lambda id, opt : clear_password

def password_file(_, options=None):
    """
    Load a password from a local user file assuming ~/.cmr_password
    """
    if options is None:
        options = {}
    path_to_use = common.dict_or_default(options, "password.path", "~/.cmr_password")
    path = os.path.expanduser(path_to_use)
    clear_text = common.read_file(path)
    return clear_text

def password_manager(account, options=None):
    """
    Use a system like the MacOS X Keychain app. Any os which also has the
    security app would also work.
    Responds to 'password.manager.app' and 'password.manager.service'
    'password.manager.service' defaults to 'cmr-lib'
    """
    if options is None:
        options = {}
    app = common.dict_or_default(options, "password.manager.app", "/usr/bin/security")
    service = common.dict_or_default(options, "password.manager.service", "cmr-lib")
    cmd = [app, "find-generic-password", "-a", account, "-s", service, "-w"]
    result = common.execute_command(cmd)
    if result is not None:
        result = result.strip()
    return result

# ##############################################################################
# functions

def sit():
    """ User to return the URL part that points to SIT """
    return "sit"

def uat():
    """ User to return the URL part that points to UAT """
    return "uat"

def prod():
    """ User to return the URL part that points to production """
    return ""

def _request_token(user, clear_password, options):
    """
    Internal worker function to call CMR and request a token
    Parameters:
        user(string): EDL user name
        clear_password(string): EDL password - in clear text ; protect this
        options(dictionary): configuration object
            cmr.env(string): CMR environment, defaults to prod
            client.name: HTTP client name to use in communications
            client.address(string): ip address of the machine making the request for token
            cache.token(boolean): True if tokens are to be cached and reused

    Returns:
        token or text of exceptions from HTTPError
    """
    #unpack
    env = common.dict_or_default(options, "cmr.env", prod())
    client_address = common.dict_or_default(options, 'client.address', net.get_local_ip)
    client_name = common.dict_or_default(options, 'client.name', 'python_cmr_lib')
    use_cache = common.dict_or_default(options, "cache.token", True)

    if use_cache:
        token_text = _read_token_file(options)
    else:
        token_text = None
    if token_text is not None and len(token_text)>0:
        return token_text
    data='<token>\
<username>{}</username>\
<password>{}</password>\
<client_id>{}</client_id>\
<user_ip_address>{}</user_ip_address>\
</token>'.format(user, clear_password, client_name, client_address)

    url = _cmr_url(env)

    encoded_data = str.encode(data)
    req = urllib.request.Request(url, data=encoded_data)
    req.add_header('Content-Type', 'application/xml')
    req.add_header('User-Agent', client_name)
    try:
        resp = urllib.request.urlopen(req)
        obj_json = json.loads(resp.read().decode('utf-8'))

        token_text = obj_json['token']['id']
        if use_cache:
            _write_token_file(token_text, options)
        return token_text
    except urllib.error.HTTPError as exception:
        return exception

def token(edl_user_name, password_lambda=password_file, opts=None):
    """
    Requests an Earth Data Login Token from CMR
    Parameters:
        edl_user_name(string): EDL user name
        password_lambda(lambda): function for returning password
        opt(dictionary): dictionary of options
    Returns:
        token or text of exceptions from HTTPError
    """
    options = opts.copy() #never change the user's options
    clear_text_password = password_lambda(edl_user_name, options)
    edl_token = _request_token(edl_user_name, clear_text_password, options)
    return edl_token

def print_help(prefix=""):
    """
    Built in help - prints out the public function names
    Parameters:
        filter(string): filters out functions beginning with this text, defaults to all
    """
    layout = "\n%s:\n%s\n"
    # n=name, c=content ; made short to keep line length down and pylint happy
    out = lambda n, c : print (layout % (n, c.__doc__.strip())) if n.startswith(prefix) else None

    print ("**** Functions:")
    out("print_help()", help)
    out("token(id, lambda, options)", token)
    out("sit()", sit)
    out("uat()", uat)
    out("prod()", prod)
    print ("**** Password Lambdas:")
    out("password(password)", password)
    out("password_file", password_file)
    out("password_manager", password_manager)
