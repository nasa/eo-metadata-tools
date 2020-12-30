# Local Rules for Styles

Local Style rules for cases where PIP 8 is not clear.

## Overview

State the problem, the local rule, and cite where on the internet someone can find precidences.


## Spaces Around Type Hints and defaults:
Should spaces be around the ':' and '=' when using both type hints and default values?

### Example

    def search_by_page(base, query = None, filters = None, page_state = None, config: dict = None):

### Ruling

Yes, put a space after ':' and around the '='.

### Citation:

* [stack overflow](https://stackoverflow.com/questions/43914201/type-annotation-style-to-space-or-not-to-space)
* [PEP 0484](https://www.python.org/dev/peps/pep-0484/#arbitrary-argument-lists-and-default-argument-values)