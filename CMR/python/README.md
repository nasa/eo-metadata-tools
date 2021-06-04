# CMR Python Wrapper

A wrapper for [github.com/nasa/Common-Metadata-Repository][git_cmr] in python

## Assumptions

1. Python 3.6 or better.
2. Can access [cmr.earthdata.nasa.gov][cmr]
3. Optional: an account on [urs.earthdata.nasa.gov][edl]
4. Third party libraries are not to be used unless absolutely necessary (none as of now)
    * some tools like pylint and pydoc_markdown are used however for the development envirnment

## Styles

1. Coding Styles are defined as [PEP 8][pep8].
2. This project uses the [editorconfig.org][econfig] file .editorconfig 
3. Use: `pylint *` or `runme.sh -l` to check code
4. Local rules can be found in [doc/style_rules.md](doc/style_rules.md)
5. [Architectural Design](design.md)

## Building and Installing

This tool is not presently hosted on [pypy.org][pypi]. There are several ways to install the library:

### Stable from github:

***NOTE***: Not yet implemented, as there is not a current stable build yet. When the first official version is created, this section will be updated.

### Latest from github:

***WARNING***: This will install the latest build which may not be the most stable code!

To install the latest build directly from github, the following command can be used. 

    pip3 install https://github.com/nasa/eo-metadata-tools/releases/download/latest-master/eo_metadata_tools_cmr-0.0.1-py3-none-any.whl

### Install Local Build:

***NOTE***: Preferred method.

    pip3 install wheel

To install the library from a local [wheel][wheel] file it will first need to be generated using the 'runme.sh' script. On a command line, run the following from the `python/CMR` directory:

    ./runme.sh -p -i

This will create a file like `dist/eo_metadata_tools_cmr-0.0.1-py3-none-any.whl` (version number may very) and install it with pip3. Reviewing the script will show the exact steps to be:
    
    python3 setup.py sdist bdist_wheel
    pip3 install dist/eo_metadata_tools_cmr-0.0.1-py3-none-any.whl

### Uninstalling
To uninstall the library, use `runme.sh -u`

### Using Library without pip3

To run the library without installing it, then try the following in the calling script (where the path is the location of the CMR/python directory inside the git clone directory):

    import sys, os
    sys.path.append(os.path.expanduser('~/src/project/eo-meta-tools-demo/CMR/python'))

## Usage

For usage help on the runme.sh command, try: `runme.sh -h` for help.

### UAT vs Production

For testing and general exploration it is advised that the User Acceptance Testing (UAT) environment of CMR be used instead of Production. These two end points have different URLs which are managed by the API. The default is production, however to use the UAT service pass in an optional configuration as shown here:

    results = coll.search(params, config={'env':'uat'})

### Tokens
If you need to use tokens, use the [EDL Token Generator](https://urs.earthdata.nasa.gov/user_tokens) to create a token. Then if your on a Macintosh, store the token in the `Keychain Access.app` application (found in the Utilities folder) by creating a password. Do this by selecting either `File->New Password Item...` or pressing `command-n`. In the resulting window make the following settings:

* **Name**: `cmr-lib-token`
* **Account**: `user`
* **Where**: `cmr lib token`
* **Comments**: put a note here that this is for the cmr python library and which envirnment the token is foro
* **Show Password**: put your token here

Save. When you request a token in code, a popup will display asking for your keychain password.

A less secure way to store your token is to save it to a text file at `~/.cmr_token`. The code will use the first line which does not start with `#`. For non-production environments you can save the token to `~/.cmr-token.uat` or `~/.cmr-token.sit`. Once your token is saved, you can have it included in your queries by calling the following:

    import cmr.search.collection as coll
    import cmr.auth.token as t
    coll.search({'keyword':'modis'},
        config=t.use_bearer_token(config={'env': 'uat'}))

This example shows how to use a token stored in `~/.cmr-token.uat` against the UAT version of CMR.
 
### Testing
Use either `runme.sh -t` or `python3 -m unittest discover`

## Using the runme.sh script
The runme.sh script documents how to run all the software stages for the project like testing, building, and installing. The script takes many flags. Below is a table of these flags.

Usage example: `./runme.sh -f -u -f -p -i -f` which means:
find, uninstall, find, package, install, find

| Flag | Option   | Name      | Description |
| ---- | -------- | --------- | -------------------------------------------- |
| -c   |          | clean     | Clean up all generated files and directories
| -d   |          | document  | Generate documentation files
| -f   |          | find      | Find the package in pip3
| -h   |          | help      | Print out this help message and then exits
| -i   |          | install   | Install latest wheel file
| -u   |          | uninstall | Uninstall the wheel file
| -l   |          | lint      | Print out this help message
| -p   |          | package   | Package project into a whl file
| -r   |          | report    | Doc-It tag report
| -t   |          | unit test | Run the unit tests
| -v   | \<value> | version   | Appends a version number to python and pip commands

If no flags are given, then `-l -u` is assumed.


[pep8]: https://www.python.org/dev/peps/pep-0008/ "Python coding standard"
[cmr]: https://cmr.earthdata.nasa.gov/ "CMR API"
[git_cmr]: https://github.com/nasa/Common-Metadata-Repository/ "CMR GitHub Repository"
[edl]: https://urs.earthdata.nasa.gov/ "Earth Data Login"
[econfig]: https://editorconfig.org/ "Editor Config Definition"
[pypi]: https://pypi.org "Python Package Index"
[wheel]: https://pypi.org/project/wheel/0.25.0/ "What is a Wheel file?"
