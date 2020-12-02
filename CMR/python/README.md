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
3. Use: `pylint *` to check code

## Usage

### UAT vs Production

For testing and general exploration it is advised that the User Acceptance Testing (UAT) environment of CMR be used instead of Production. These two end points have different URLs which are managed by the API. The default is production, however to use the UAT service pass in an optional configuration as shown here:

    results = coll.search(params, config={'env':'uat'})

### Testing
`python3 -m unittest discover`

[pep8]: https://www.python.org/dev/peps/pep-0008/ "Python coding standard"
[cmr]: https://cmr.earthdata.nasa.gov/ "CMR API"
[git_cmr]: https://github.com/nasa/Common-Metadata-Repository/ "CMR GitHub Repository"
[edl]: https://urs.earthdata.nasa.gov/ "Earth Data Login"
[econfig]: https://editorconfig.org/ "Editor Config Definition"
