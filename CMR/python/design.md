# CMR Python Wrapper Design

Design concepts for the code.

## Overview

The CMR Python Wrapper was created to be a wrapper around the CMR API and to be a bridge between Jypter Notebooks and CMR.

## Code Conventions

### Lambdas
When ever there is a choice on how to process some data or which "method" should be used for some algorithm, then these choices should be captured as lambda functions. Lambda functions can defer processing to the point where it is actually needed (or skipped if it no longer makes since to run).

    def search(query = None,
    	filters = None,
		limit = None,
		config: dict = None):
		
For the search function in cmr/search/collection.py, the second parameter is actually a list. For filter it is a list of lambda functions which reduced the number of fields returned. These filters can then be applied in any order and can be swapped out as needed by the user in a notebook. These filters should be short and very specific, handling only one item at a time. In this way the calling code can figure out how best to loop through the set of items, especially in the case where function generators are to be used and data is not processed till it is needed, at which time lambda functions can be executed on demand using the smallest chuck of data available.

    for each item ready in the list:
        lambda 1 -> lambda 2 -> ...

### Configurations

Public functions should only take the most important parameters and push everything else off to a configuration dictionary. Many such configurations are of general use to all calls, like which environment is to be used (UAT vs OPS) or what login token should be used. These values, once in a dictionary, can then be shared at all levels of the code, from the public functions down to the utility functions. The linter also enforces function calls to have a limited number of parameters, so having this standard way to handle the less important parameters helps the code stay in line with standards.

### Functional Programing

Functions should strive to be "pure" ; functions should not change internal state and always return the same result given the same inputs.

Borrow from Clojure when possible.

### Documentation as Code

Since the library is to be run in notebooks, provide a way to communicate to the user API calls available. Do this using python's "reflection" abilities to dynamically discover functions and docstrings. All functions should assume that the associated docstring will be accessed through the `__doc__` parameter.

### Libraries

Use as few libraries as maintainers. All libraries become a support nightmare for not only the maintainers of code but also for users who may not be able to meet the ever expanding requirements of third party libraries which in turn require their own libraries. Do not require running code to link to any library, Python has everything one would need. To assist with this principle, do not be afraid to use the newer version of Python. When moving the version up, document which exact feature is needed to justify moving the version number up.

Exceptions to this principle are made for the build infrastructure as it makes no since to implement our own linter.