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

As of this time the CMR library is not hosted on [pypy.org][pypi]. To install the library from a [wheel][wheel] file it will need to be generated locally using the 'runme.sh' script. On a command line, do the following from the python/CMR directory:

    ./runme.sh -p -i

This will create a file like `dist/eo_metadata_tools_cmr-0.0.1-py3-none-any.whl` (version number may very) and install it with pip3. Reviewing the script will show the exact steps to be:
    
    python3 setup.py sdist bdist_wheel
    pip3 install dist/eo_metadata_tools_cmr-0.0.1-py3-none-any.whl

To uninstall the library, use `runme.sh -u`

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

[pep8]: https://www.python.org/dev/peps/pep-0008/ "Python coding standard"
[cmr]: https://cmr.earthdata.nasa.gov/ "CMR API"
[git_cmr]: https://github.com/nasa/Common-Metadata-Repository/ "CMR GitHub Repository"
[edl]: https://urs.earthdata.nasa.gov/ "Earth Data Login"
[econfig]: https://editorconfig.org/ "Editor Config Definition"
[pypi]: https://pypi.org "Python Package Index"
[wheel]: https://pypi.org/project/wheel/0.25.0/ "What is a Wheel file?"
