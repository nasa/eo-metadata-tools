# Table of Contents

* [cmr](#cmr)
* [cmr.util](#cmr.util)
* [cmr.util.common](#cmr.util.common)
* [cmr.util.network](#cmr.util.network)
* [cmr.auth](#cmr.auth)
* [cmr.auth.token](#cmr.auth.token)
* [cmr.search](#cmr.search)
* [cmr.search.granule](#cmr.search.granule)
* [cmr.search.common](#cmr.search.common)
* [cmr.search.collection](#cmr.search.collection)

<a name="cmr"></a>
# cmr

A Library interfacing with the CMR API

* date: 2020-11-23
* since: 0.0

Create version info Query the BUILD constant for information on the package version

More information can be found at:
https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html

<a name="cmr.__version__"></a>
#### \_\_version\_\_

Package Version number

<a name="cmr.BUILD"></a>
#### BUILD

Build and version information for the entire package

<a name="cmr.util"></a>
# cmr.util

<a name="cmr.util.common"></a>
# cmr.util.common

date 2020-10-26
since 0.0

<a name="cmr.util.common.conj"></a>
#### conj

```python
conj(coll, to_add)
```

Similar to clojure's function, add items to a list or dictionary

See https://clojuredocs.org/clojure.core/conj for more reading

Returns a new collection with the to_add 'added'. conj(None, item) returns
(item).  The 'addition' may happen at different 'places' depending on the
concrete type. if coll is:
[] - appends            [1, 2, 3, 4] == conj([1, 2], [3, 4])
() - prepend in reverse ((4, 3, 1, 2) == conj((1, 2), (3, 4))
{} - appends            {'a': 'A', 'b': 'B'} == conj({'a':'A'}, {'b':'B'})

**Arguments**:

- `coll` - collection to add items to
- `to_add` - items to be added to coll

**Returns**:

  object of the same type as coll but with to_add items added

<a name="cmr.util.common.drop_key_safely"></a>
#### drop\_key\_safely

```python
drop_key_safely(dictionary, key)
```

Drop a key from a dict if it exists and return that change

<a name="cmr.util.common.read_file"></a>
#### read\_file

```python
read_file(path)
```

Read and return the contents of a file

**Arguments**:

- `path` _string_ - full path to file to read

**Returns**:

  None if file was not found, contents otherwise

<a name="cmr.util.common.write_file"></a>
#### write\_file

```python
write_file(path, text)
```

Write (creating if need be) file and set it's content

**Arguments**:

- `path` _string_ - path to file to write
- `text` _string_ - content for file

<a name="cmr.util.common.execute_command"></a>
#### execute\_command

```python
execute_command(cmd)
```

A utility method to execute a shell command and return a string of the output

**Arguments**:

  cmd(string) unix command to execute

**Returns**:

  response from command

<a name="cmr.util.common.call_security"></a>
#### call\_security

```python
call_security(account, service, app="/usr/bin/security")
```

Call the security command to look up encrypted values

<a name="cmr.util.common.help_format_lambda"></a>
#### help\_format\_lambda

```python
help_format_lambda(contains="")
```

Return a lambda to be used to format help output for a function

<a name="cmr.util.network"></a>
# cmr.util.network

date 2020-11-05
since 0.0

<a name="cmr.util.network.get_local_ip"></a>
#### get\_local\_ip

```python
get_local_ip()
```

Rewrite this stub, it is used in code not checked in yet

<a name="cmr.util.network.value_to_param"></a>
#### value\_to\_param

```python
value_to_param(key, value)
```

Convert a key value pair into a URL parameter pair

<a name="cmr.util.network.expand_parameter_to_parameters"></a>
#### expand\_parameter\_to\_parameters

```python
expand_parameter_to_parameters(key, parameter)
```

Convert a list of values into a list of URL parameters

<a name="cmr.util.network.expand_query_to_parameters"></a>
#### expand\_query\_to\_parameters

```python
expand_query_to_parameters(query=None)
```

Convert a dictionary to URL parameters

<a name="cmr.util.network.apply_headers_to_request"></a>
#### apply\_headers\_to\_request

```python
apply_headers_to_request(req, headers)
```

Apply a headers to a urllib request object

<a name="cmr.util.network.transform_results"></a>
#### transform\_results

```python
transform_results(results, keys_of_interest)
```

Take a list of results and convert them to a multi valued dictionary. The
real world use case is to take values from a list of collections and pass
them to a granule search.

[{key1:value1},{key1:value2},...] -> {"key1": [value1,value2]} ->
    &key1=value1&key1=value2 ( via expand_query_to_parameters() )

<a name="cmr.util.network.config_to_header"></a>
#### config\_to\_header

```python
config_to_header(config, source_key, headers, destination_key=None, default=None)
```

Copy a value in the config into a header dictionary for use by urllib. Written
to reduce boiler plate code

config[key] -> [or default] -> [rename] -> headers[key]

**Arguments**:

- `config(dictionary)` - where to look for values
- `source_key(string)` - name if configuration in config
- `headers(dictionary)` - where to copy values to
- `destination_key(string)` - name of key to save to in headers
- `default(string)` - value to use if value can not be found in config

<a name="cmr.util.network.post"></a>
#### post

```python
post(url, body, accept=None, headers=None)
```

Make a basic HTTP call to CMR using the POST action

**Arguments**:

- `url` _string_ - resource to get
- `body` _dictionary_ - parameters to send, or string if raw text to be sent
- `accept` _string_ - encoding of the returned data, some form of json is expected
- `client_id` _string_ - name of the client making the (not python or curl)
- `headers` _dictionary_ - HTTP headers to apply

<a name="cmr.auth"></a>
# cmr.auth

<a name="cmr.auth.token"></a>
# cmr.auth.token

A Library for managing EDL tokens to be used with CMR
date: 2020-10-26
since: 0.0

Overview:
    The function token(lambda_list, config) will iterate over a list of token
    managers and return the value from the first manager that finds a token.

    Token Managers are lambda functions that take in a 'config' dictionary for
    use as a source for configurations, and returns a token as a string.

<a name="cmr.auth.token.token_literal"></a>
#### token\_literal

```python
token_literal(token_text: str)
```

Generates an token lambda file which always returns the same value, this is
used for testing, and also as an example of how to write token managers

**Arguments**:

- `token_text(string)` - the token which should always be returned by the lambda

**Returns**:

  A lambda function which takes a dictionary and returns a token

<a name="cmr.auth.token.token_config"></a>
#### token\_config

```python
token_config(config: dict = None) -> str
```

Pull a token from the configuration dictionary

**Arguments**:

- `config` - Responds to:
- `"cmr.token.value"` - value of token, defaults to 'None'

<a name="cmr.auth.token.token_file"></a>
#### token\_file

```python
token_file(config: dict = None) -> str
```

Load a token from a local user file assumed to be ~/.cmr_token

**Arguments**:

- `config` - Responds to:
- `"cmr.token.file"` - location of token file, defaults to ~/.cmr_token
  Returns
  token from file

<a name="cmr.auth.token.token_manager"></a>
#### token\_manager

```python
token_manager(config: dict = None) -> str
```

Use a system like the MacOS X Keychain app. Any os which also has the
security app would also work.

**Arguments**:

- `config` - Responds to the following:
- `'token.manager.account'` - account field in Keychain
- `'token.manager.app'` - Keychain command - defaults to /usr/bin/security
  'token.manager.service' defaults to 'cmr-lib-token'

**Returns**:

  token from Keychain

<a name="cmr.auth.token.token"></a>
#### token

```python
token(token_lambdas=None, config: dict = None) -> str
```

Recursively calls lambdas till a token is found

**Arguments**:

- `token_lambda` - a token lambda or a list of functions
- `config` - Responds to no values

**Returns**:

  the EDL Token from the token lambda

<a name="cmr.auth.token.help_text"></a>
#### help\_text

```python
help_text(prefix: str = '') -> str
```

Built in help - prints out the public function names for the token API

**Arguments**:

- `filter` - filters out functions beginning with this text, defaults to all

**Returns**:

  text ready to be passed to print()

<a name="cmr.search"></a>
# cmr.search

<a name="cmr.search.granule"></a>
# cmr.search.granule

A Library for building and requesting CMR granule searches
date: 2020-11-23
since: 0.0

A simple search interface for CMR. Use the search() function to perform searches.
This function can handle any query parameter which is supported by the CMR.

    search()
        query - a dictionary of CMR parameters
        filters - a list of result filter lambdas
        limit - int limiting the number of records returned
        config - configurations

More information can be found at:
https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html

<a name="cmr.search.granule.all_fields"></a>
#### all\_fields

```python
all_fields(item)
```

Makes no change to the item, passes through. Used primarily as an example
and for testing the filter workflow

<a name="cmr.search.granule.meta_fields"></a>
#### meta\_fields

```python
meta_fields(item)
```

Return only the the meta objects

<a name="cmr.search.granule.umm_fields"></a>
#### umm\_fields

```python
umm_fields(item)
```

Return only the UMM part of the data

<a name="cmr.search.granule.concept_id_fields"></a>
#### concept\_id\_fields

```python
concept_id_fields(item)
```

Extract only fields that are used to identify a record

<a name="cmr.search.granule.drop_fields"></a>
#### drop\_fields

```python
drop_fields(key)
```

Drop a key from a dictionary

<a name="cmr.search.granule.granule_core_fields"></a>
#### granule\_core\_fields

```python
granule_core_fields(item)
```

Extract only fields that are used to identify a record

<a name="cmr.search.granule.apply_filters"></a>
#### apply\_filters

```python
apply_filters(filters, items)
```

Apply all the filters on the downloaded data

**Arguments**:

- `filters(list)` - a list of filter lambdas which taken in a row and return and row
- `items(list)` - list of records from CMR

**Returns**:

  Filtered data

<a name="cmr.search.granule.search"></a>
#### search

```python
search(query, filters=None, limit=None, config: dict = None)
```

Search and return all records

**Arguments**:

- `query` _dictionary_ - required, CMR search parameters
- `filters` _list_ - column filter lambdas
- `limit` _int_ - number from 1 to 100000
- `config` _dictionary_ - configuration settings

**Returns**:

  JSON results from CMR

<a name="cmr.search.granule.experimental_search_generator"></a>
#### experimental\_search\_generator

```python
experimental_search_generator(query, filters=None, limit=None, config: dict = None)
```

WARNING: This is an experimental function, do not use in an operational
system, this function will go away.

This function performs searches and returns data as a list generator. Errors
will go to logs. A list generator may be more performant on large datasets,
but some experimenting is needed.

**Arguments**:

- `query` _dictionary_ - required, CMR search parameters
- `filters` _list_ - column filter lambdas
- `limit` _int_ - number from 1 to 100000
- `config` _dictionary_ - configuration settings

**Returns**:

  JSON results from CMR

<a name="cmr.search.granule.open_api"></a>
#### open\_api

```python
open_api(section='#granule-search-by-parameters')
```

Ask python to open up the API in a new browser window

**Arguments**:

- `selection(string)` - HTML Anchor Tag, default is `granule`-search-by-parameters

<a name="cmr.search.granule.set_logging_to"></a>
#### set\_logging\_to

```python
set_logging_to(level)
```

Set the logging level to the stated value. Any of the standard logging level
as stated in https://docs.python.org/3/howto/logging.html#when-to-use-logging
can be used here. These include: DEBUG, INFO, WARNING, ERROR, and CRITICAL

**Arguments**:

- `level` - a value like logging.INFO

<a name="cmr.search.granule.help_text"></a>
#### help\_text

```python
help_text(contains: str = "")
```

Return help for the public functions in the Granule api

<a name="cmr.search.common"></a>
# cmr.search.common

Code common to both collection.py and granule.py
date: 2020-11-23
since: 0.0

A simple search interface for CMR. Use the search() function to perform searches.
This function can handle any query parameter which is supported by the CMR.

    search_by_page()
        base - CMR API end point directory
        query - a dictionary of CMR parameters
        filters - a list of result filter lambdas
        page_state - a page_state dictionary for current page
        config - configurations

More information can be found at:
https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html

<a name="cmr.search.common.all_fields"></a>
#### all\_fields

```python
all_fields(item)
```

Makes no change to the item, passes through. Used primarily as an example
and for testing the filter workflow

<a name="cmr.search.common.meta_fields"></a>
#### meta\_fields

```python
meta_fields(item)
```

Return only the the meta objects

<a name="cmr.search.common.umm_fields"></a>
#### umm\_fields

```python
umm_fields(item)
```

Return only the UMM part of the data

<a name="cmr.search.common.concept_id_fields"></a>
#### concept\_id\_fields

```python
concept_id_fields(item)
```

Extract only fields that are used to identify a record

<a name="cmr.search.common.drop_fields"></a>
#### drop\_fields

```python
drop_fields(key)
```

Drop a key from a dictionary

<a name="cmr.search.common.create_page_state"></a>
#### create\_page\_state

```python
create_page_state(page_size=10, page_num=1, took=0, limit=10)
```

Dictionary to hold page state for the recursive call

**Arguments**:

- `page_size` - number of hits per request, can be 1-2000, default to 10
- `page_num` - current page, can be 1-50, default to 1
- `took` - positive number, seconds of total processing
- `limit` - max records to return, 1-100000, default to 10

<a name="cmr.search.common.clear_scroll"></a>
#### clear\_scroll

```python
clear_scroll(scroll_id, config: dict = None)
```

This action is called to clear a scroll ID from CMR allowing CMR to free up
memory associated with the current search.

This call is the same as calling the following CURL command:
curl -i -XPOST -H "Content-Type: application/json" \
https://cmr.earthdata.nasa.gov/search/clear-scroll \
-d '{ "scroll_id" : "xxxx"}'
This API call must send " and not '
API call returns HTTP status code 204 when successful.

**Arguments**:

- `scroll_id(string/number)` - CMR Scroll ID
  config(dictionary) - used to make configurations changes

**Returns**:

  error dictionary if there was a problem, otherwise a JSON object of response headers

<a name="cmr.search.common.apply_filters"></a>
#### apply\_filters

```python
apply_filters(filters, items)
```

Apply all filters to the collection of data, returning the results

**Arguments**:

- `filters(list)` - list of or a single lambda function to apply to items
- `items(list)` - list of objects to be processed

**Returns**:

  the results of the filters

<a name="cmr.search.common.search_by_page"></a>
#### search\_by\_page

```python
search_by_page(base, query=None, filters=None, page_state=None, config: dict = None)
```

Recursive function to download all the pages of data. Note, this function
will only run for 5 minutes and then will refuse to pull more pages
returning what was found in that amount of time.

**Arguments**:

- `query` _dictionary_ - CMR parameters and their values
- `filters` _list_ - A list of lambda functions to reduce the number of columns
- `page_state` _dictionary_ - the current page to download
- `config` _dictionary_ - configurations settings responds to:
  * accept - the format for the return defaults to UMM-JSON
  * max-time - total processing time allowed for all calls
  return collected items

<a name="cmr.search.common.experimental_search_by_page_generator"></a>
#### experimental\_search\_by\_page\_generator

```python
experimental_search_by_page_generator(base, query=None, filters=None, page_state=None, config: dict = None)
```

WARNING: This is an experimental function, do not use in an operational
system, this function will go away.

This function performs searches and returns data as a list generator. Errors
will go mostly to logs.

<a name="cmr.search.common.open_api"></a>
#### open\_api

```python
open_api(section)
```

Ask python to open up the API in a new browser window - unsupported!

<a name="cmr.search.common.set_logging_to"></a>
#### set\_logging\_to

```python
set_logging_to(level=logging.ERROR)
```

Set the logging level to one of the levels 'CRITICAL', 'ERROR', 'WARNING',
'INFO', 'DEBUG', or 'NOTSET'.

**Arguments**:

- `level` - a value like logging.INFO or a string like 'INFO'

<a name="cmr.search.common.help_text"></a>
#### help\_text

```python
help_text(prefix, functions, filters)
```

Built in help - prints out the public function names for the token API

**Arguments**:

- `filter(string)` - filters out functions beginning with this text, defaults to all

<a name="cmr.search.collection"></a>
# cmr.search.collection

A Library for building and requesting CMR collection searches
date: 2020-11-23
since: 0.0

A simple search interface for CMR. Use the search() function to perform searches.
This function can handle any query parameter which is supported by the CMR.

    search()
        query - a dictionary of CMR parameters
        filters - a list of result filter lambdas
        limit - int, limiting the number of records returned
        config - configurations

More information can be found at:
https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html

<a name="cmr.search.collection.all_fields"></a>
#### all\_fields

```python
all_fields(item)
```

Makes no change to the item, passes through. Used primarily as an example
and for testing the filter workflow

<a name="cmr.search.collection.meta_fields"></a>
#### meta\_fields

```python
meta_fields(item)
```

Return only the the meta objects

<a name="cmr.search.collection.umm_fields"></a>
#### umm\_fields

```python
umm_fields(item)
```

Return only the UMM part of the data

<a name="cmr.search.collection.concept_id_fields"></a>
#### concept\_id\_fields

```python
concept_id_fields(item)
```

Extract only fields that are used to identify a record

<a name="cmr.search.collection.drop_fields"></a>
#### drop\_fields

```python
drop_fields(key)
```

Drop a key from a dictionary

<a name="cmr.search.collection.collection_core_fields"></a>
#### collection\_core\_fields

```python
collection_core_fields(item)
```

Extract only fields that are used to identify a record

<a name="cmr.search.collection.collection_ids_for_granules_fields"></a>
#### collection\_ids\_for\_granules\_fields

```python
collection_ids_for_granules_fields(item: object)
```

Extract only the fields that are of interest to doing a granule search

<a name="cmr.search.collection.apply_filters"></a>
#### apply\_filters

```python
apply_filters(filters, items)
```

Apply all the filters on the downloaded data

**Arguments**:

- `filters(list)` - a list of filter lambdas which taken in a row and return and row
- `items(list)` - list of records from CMR

**Returns**:

  Filtered data

<a name="cmr.search.collection.search"></a>
#### search

```python
search(query=None, filters=None, limit=None, config: dict = None)
```

Search and return all records

<a name="cmr.search.collection.set_logging_to"></a>
#### set\_logging\_to

```python
set_logging_to(level)
```

Set the logging level to the stated value. Any of the standard logging level
as stated in https://docs.python.org/3/howto/logging.html#when-to-use-logging
can be used here. These include: DEBUG, INFO, WARNING, ERROR, and CRITICAL

**Arguments**:

- `level` - a value like logging.INFO

<a name="cmr.search.collection.open_api"></a>
#### open\_api

```python
open_api(section='#collection-search-by-parameters')
```

Ask python to open up the API in a new browser window

<a name="cmr.search.collection.help_text"></a>
#### help\_text

```python
help_text(contains: str = "")
```

Built in help - prints out the public function names for the collection object for the token API

**Arguments**:

- `filter(string)` - filters out functions beginning with this text, defaults to all

