# CMR Python Wrapper

A wrapper for [github.com/nasa/Common-Metadata-Repository][git_cmr] in python

## Assumptions

1. Python 3.2 or better.
2. Can access [cmr.earthdata.nasa.gov][cmr]
3. Optional: an account on [urs.earthdata.nasa.gov][edl]
4. Third party libraries are not to be used unless absolutely necessary (none as of now)

## Styles

1. Coding Styles are defined as [PEP 8][pep8].
2. This project uses the [editorconfig.org][econfig] file .editorconfig 
3. Use: `pylint *` to check code

## Usage

### Getting an EDL token

There are three ways to store a password for use in scripts. Plain text in the script (not recommended), in a file, but still clear text, or if you are on a mac or compatible system, you can use the password manager which on Mac OS X will come from Keychain. These three methods are selected by passing in a lambda function to the token() function

    import cmr.auth.token as edl
    edl_token = edl.token(user_id)
    edl_token = edl.token(user_id, edl.password("clear_text"))
    edl_token = edl.token(user_id, edl.password_file, {"password_file":"~/.passwd"})
    edl_token = edl.token(user_id, edl.password_manager, {})

* user_id is the Earthdata login name
* `password_lambda` is a function for returning passwords and defaults to `password_file`.
    * `password(text)` = creates a lambda using a hard coded password.
    * `password_file` = uses the contents of `~/.cmr_password`. File can be overwritten by setting `password.path`
    * `password_manager` = will check a password manager, specifically the `/usr/bin/security` command and response to the following overrides
        * `password.manager.app` = command to use
        * `password.manager.service` = keychain object name, defaults to cmr-lib
* options is a dictionary where overrides can be passed in
    * "cmr.env" - cmr server to use, defaults to production, can also be set to    
        * "sit"
        * "uat",
        * "" (empty string ; the default) for production.
    * 'client.address' - client IP address to use, will try to discover it if not provided
    * 'client.name' - HTTP Agent name to use
    * "cache.token" - will cache tokens to a file - default is True
    * "cmr.token.file" - location of token cache

### Testing
`python3 -m unittest discover`

[pep8]: https://www.python.org/dev/peps/pep-0008/ "Python coding standard"
[cmr]: https://cmr.earthdata.nasa.gov/ "CMR API"
[git_cmr]: https://github.com/nasa/Common-Metadata-Repository/ "CMR GitHub Repository"
[edl]: https://urs.earthdata.nasa.gov/ "Earth Data Login"
[econfig]: https://editorconfig.org/ "Editor Config Definition"
