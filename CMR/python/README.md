# CMR Python Wrapper

A wrapper for [github.com/nasa/Common-Metadata-Repository][git_cmr] in python

## Assumptions

1. Python 3.4 or better.
2. Can access [cmr.earthdata.nasa.gov][cmr]
3. Optional: an account on [urs.earthdata.nasa.gov][edl]
4. Third party libraries are not to be used unless absolutely necessary (none as of now)

## Styles

1. Coding Styles are defined as [PEP 8][pep8].
2. This project uses the [editorconfig.org][econfig] file .editorconfig 
3. Use: `pylint *` or `runme.sh -l` to check code

## Building and Installing

As of this time the CMR library is not hosted on [pypy.org][pypi]. There are several ways to install the library:

### Stable from github:

***NOTE***: Not yet implemented, as there is not a current stable build yet. When the first version is created, this section will be updated.

### Latest from git hub:

***WARNING***: This will install the latest build and may not be the most stable code!

To install the latest build directly from github, the following command can be.
used. But be warned, 

    pip3 install 'https://github.com/nasa/eo-metadata-tools/releases/download/latest/eo_metadata_tools_cmr-0.0.1-py3-none-any.whl'{code}

### Install Local Build:

***NOTE***: Preferred method.

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

### Testing
Use either `runme.sh -t` or `python3 -m unittest discover`

## Using the runme.sh script
The runme.sh script documents how to run all the software life cycles for the project like testing, building, and installing. The script takes many flags, the lastest can be viewed by calling `./runme.sh -h`. Below is also a table of these flags. All flags can be called more then once except -h which ends the script.

Usage example: `./runme.sh -f -u -f -p -i -f` which means:
find, uninstall, find, package, install, find

| Flag | Name      | Description |
| ---- | --------- | -------------------------------------------- |
| -c   | clean     | Clean up all generated files and directories
| -f   | find      | Find the package in pip3
| -h   | help      | Print out this help message
| -i   | install   | Install latest wheel file
| -u   | uninstall | Uninstall the wheel file
| -l   | lint      | Print out this help message
| -p   | package   | Package project into a whl file
| -t   | unit test | Run the unit tests

If no flags are given, then `-l -u` is assumed.


[pep8]: https://www.python.org/dev/peps/pep-0008/ "Python coding standard"
[cmr]: https://cmr.earthdata.nasa.gov/ "CMR API"
[git_cmr]: https://github.com/nasa/Common-Metadata-Repository/ "CMR GitHub Repository"
[edl]: https://urs.earthdata.nasa.gov/ "Earth Data Login"
[econfig]: https://editorconfig.org/ "Editor Config Definition"
[pypi]: https://pypi.org "Python Package Index"
[wheel]: https://pypi.org/project/wheel/0.25.0/ "What is a Wheel file?"
