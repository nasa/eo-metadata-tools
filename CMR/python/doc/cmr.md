# Table of Contents

* [cmr](#cmr)
* [cmr.util](#cmr.util)
* [cmr.util.common](#cmr.util.common)
* [cmr.util.network](#cmr.util.network)
* [cmr.auth.token](#cmr.auth.token)
* [cmr.auth](#cmr.auth)
* [cmr.search](#cmr.search)
* [cmr.search.granule](#cmr.search.granule)
* [cmr.search.providers](#cmr.search.providers)
* [cmr.search.common](#cmr.search.common)
* [cmr.search.collection](#cmr.search.collection)

<a id="cmr"></a>

# cmr

A Library interfacing with the CMR API

* date: 2020-11-23
* since: 0.0

Create version info Query the BUILD constant for information on the package version

More information can be found at:
https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html

<a id="cmr.__version__"></a>

#### \_\_version\_\_

Package Version number

<a id="cmr.BUILD"></a>

#### BUILD

Build and version information for the entire package

<a id="cmr.util"></a>

# cmr.util

<a id="cmr.util.common"></a>

# cmr.util.common

date 2020-10-26
since 0.0

<a id="cmr.util.common.conj"></a>

#### conj

```python
def conj(coll, to_add)
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

<a id="cmr.util.common.always"></a>

#### always

```python
def always(obj: dict, otype=dict)
```

Ensure that something is always returned. Assumes dictionary, but list or
tuple can be specified, because source may be none, it can not be derived

**Arguments**:

- `obj` - a dictionary, list, or tuple
- `otype` - object type, the actual type `dict` (default), `list`, or `tuple`

**Returns**:

  {}, [], or () as needed, or the object that was passed in if it already exists

<a id="cmr.util.common.drop_key_safely"></a>

#### drop\_key\_safely

```python
def drop_key_safely(dictionary, key)
```

Drop a key from a dict if it exists and return that change

<a id="cmr.util.common.read_file"></a>

#### read\_file

```python
def read_file(path)
```

Read and return the contents of a file

**Arguments**:

- `path` _string_ - full path to file to read

**Returns**:

  None if file was not found, contents otherwise

<a id="cmr.util.common.write_file"></a>

#### write\_file

```python
def write_file(path, text)
```

Write (creating if need be) file and set it's content

**Arguments**:

- `path` _string_ - path to file to write
- `text` _string_ - content for file

<a id="cmr.util.common.execute_command"></a>

#### execute\_command

```python
def execute_command(cmd)
```

A utility method to execute a shell command and return a string of the output

**Arguments**:

  cmd(string) unix command to execute

**Returns**:

  response from command

<a id="cmr.util.common.call_security"></a>

#### call\_security

```python
def call_security(account, service, app="/usr/bin/security")
```

Call the security command to look up encrypted values

<a id="cmr.util.common.help_format_lambda"></a>

#### help\_format\_lambda

```python
def help_format_lambda(contains="")
```

Return a lambda to be used to format help output for a function

<a id="cmr.util.common.mask_string"></a>

#### mask\_string

```python
def mask_string(unsafe_value)
```

Prevent sensitive information from being printed by masking values

<a id="cmr.util.common.mask_dictionary"></a>

#### mask\_dictionary

```python
def mask_dictionary(data, keys)
```

Prevent sensitive information from being printed by masking values of listed
keys in a dictionaries. The middle third of the values will be replaced with
'*'. Uses Dictionaries copy() function.
Return a shallow copy of the data dictionary that has been updated

<a id="cmr.util.common.now"></a>

#### now

```python
def now()
```

return the current time in a function that can be patched away for testing

<a id="cmr.util.network"></a>

# cmr.util.network

date 2020-11-05
since 0.0

<a id="cmr.util.network.get_local_ip"></a>

#### get\_local\_ip

```python
def get_local_ip()
```

Rewrite this stub, it is used in code not checked in yet

<a id="cmr.util.network.value_to_param"></a>

#### value\_to\_param

```python
def value_to_param(key, value)
```

Convert a key value pair into a URL parameter pair

<a id="cmr.util.network.expand_parameter_to_parameters"></a>

#### expand\_parameter\_to\_parameters

```python
def expand_parameter_to_parameters(key, parameter)
```

Convert a list of values into a list of URL parameters

<a id="cmr.util.network.expand_query_to_parameters"></a>

#### expand\_query\_to\_parameters

```python
def expand_query_to_parameters(query=None)
```

Convert a dictionary to URL parameters

<a id="cmr.util.network.apply_headers_to_request"></a>

#### apply\_headers\_to\_request

```python
def apply_headers_to_request(req, headers)
```

Apply a headers to a urllib request object

<a id="cmr.util.network.transform_results"></a>

#### transform\_results

```python
def transform_results(results, keys_of_interest)
```

Take a list of results and convert them to a multi valued dictionary. The
real world use case is to take values from a list of collections and pass
them to a granule search.

[{key1:value1},{key1:value2},...] -> {"key1": [value1,value2]} ->
    &key1=value1&key1=value2 ( via expand_query_to_parameters() )

<a id="cmr.util.network.config_to_header"></a>

#### config\_to\_header

```python
def config_to_header(config,
                     source_key,
                     headers,
                     destination_key=None,
                     default=None)
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

<a id="cmr.util.network.post"></a>

#### post

```python
def post(url, body, accept=None, headers=None)
```

Make a basic HTTP call to CMR using the POST action

**Arguments**:

- `url` _string_ - resource to get
- `body` _dictionary_ - parameters to send, or string if raw text to be sent
- `accept` _string_ - encoding of the returned data, some form of json is expected
- `client_id` _string_ - name of the client making the (not python or curl)
- `headers` _dictionary_ - HTTP headers to apply

<a id="cmr.util.network.get"></a>

#### get

```python
def get(url, accept=None, headers=None)
```

Make a basic HTTP call to CMR using the POST action

**Arguments**:

- `url` _string_ - resource to get
- `body` _dictionary_ - parameters to send, or string if raw text to be sent
- `accept` _string_ - encoding of the returned data, some form of json is expected
- `client_id` _string_ - name of the client making the (not python or curl)
- `headers` _dictionary_ - HTTP headers to apply

<a id="cmr.auth.token"></a>

# cmr.auth.token

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

<a id="cmr.auth.token.token_literal"></a>

#### token\_literal

```python
def token_literal(token_text: str)
```

Generates an token lambda file which always returns the same value, this is
used for testing, and also as an example of how to write token managers

**Arguments**:

- `token_text(string)` - the token which should always be returned by the lambda

**Returns**:

  A lambda function which takes a dictionary and returns a token

<a id="cmr.auth.token.token_config"></a>

#### token\_config

```python
def token_config(config: dict = None)
```

Pull a token from the configuration dictionary

**Arguments**:

- `config` - Responds to:
- `"cmr.token.value"` - value of token, defaults to 'None'

<a id="cmr.auth.token.token_file"></a>

#### token\_file

```python
def token_file(config: dict = None)
```

Load a token from a local user file assumed to be ~/.cmr_token

**Arguments**:

- `config` - Responds to:
- `"cmr.token.file"` - location of token file, defaults to ~/.cmr_token
  for production, followed by a dot and the environment name if
  specified.
- `"env"` - if not production, appended to the end of ~/.cmr_token with a dot
  Returns
  token from file

<a id="cmr.auth.token.token_manager"></a>

#### token\_manager

```python
def token_manager(config: dict = None)
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

<a id="cmr.auth.token.read_tokens"></a>

#### read\_tokens

```python
def read_tokens(edl_user, token_lambdas=None, config: dict = None)
```

Read and return the EDL tokens for a given user. Using this function makes
the assumption that your storing the EDL password in one of the token lambda
handlers and not tokens themself. This can be overwritten in the config file
if you plan to store both tokens and password.

**Arguments**:

- `edl_user` - EDL User name
- `token_lambda` - a token lambda or a list of functions
- `config` - config dictionary to base new dictionary off of

**Returns**:

  a dictionary like the following:
- `{"hits"` - 1,
- `"items"` - [{"access_token": "EDL-UToken-Content",
- `"expiration_date"` - "10/31/2121"}]}

<a id="cmr.auth.token.create_token"></a>

#### create\_token

```python
def create_token(edl_user, token_lambdas=None, config: dict = None)
```

Create and return a EDL token for a given user. Using this function makes
the assumption that your storing the EDL password in one of the token lambda
handlers and not tokens themself. This can be overwritten in the config file
if you plan to store both tokens and password.

**Arguments**:

- `edl_user` - EDL User name
- `token_lambda` - a token lambda or a list of functions
- `config` - config dictionary to base new dictionary off of

**Returns**:

  a dictionary like the following:
- `{"access_token"` - "EDL-UToken-Content",
  "token_type":"Bearer",
- `"expiration_date"` - "10/31/2121"}

<a id="cmr.auth.token.delete_token"></a>

#### delete\_token

```python
def delete_token(access_token,
                 edl_user,
                 token_lambdas=None,
                 config: dict = None)
```

Delete a taken from EDL
Return None if failed, otherwise EDL response

<a id="cmr.auth.token.fetch_token"></a>

#### fetch\_token

```python
def fetch_token(edl_user, token_lambdas=None, config: dict = None)
```

Talk to EDL and pull out a token for use in CMR calls. To lookup tokens, an
EDL User name and password will be sent over the network.
Return: None or Access token

<a id="cmr.auth.token.fetch_bearer_token_with_password"></a>

#### fetch\_bearer\_token\_with\_password

```python
def fetch_bearer_token_with_password(edl_user,
                                     edl_password,
                                     config: dict = None)
```

This function is the fastest way to use this API, this call will run all
other functions needed to either get or generate a token on the users behalf.

**Arguments**:

- `edl_user` - user name in the Earth Data Login System
- `edl_password` - password in the Earth Data Login system
- `config` - configuration dictionary

**Returns**:

- `Success` - config dict with 'authorization' key added
- `Error` - {'error': 'invalid_credentials', 'error_description':
  'Invalid user credentials', 'code': 401, 'reason': 'Unauthorized'}

<a id="cmr.auth.token.fetch_bearer_token"></a>

#### fetch\_bearer\_token

```python
def fetch_bearer_token(edl_user, token_lambdas=None, config: dict = None)
```

This function is the similar to fetch_bearer_token_with_password() but takes
lambda lookup functions instead of a fixed password. This call will run all
other functions needed to either get or generate a token on the users behalf.

**Arguments**:

- `edl_user` - user name in the Earth Data Login System
- `token_lambda` - a token lambda or a list of functions
- `config` - configuration dictionary

**Returns**:

- `Success` - config dict with 'authorization' key added
- `Error` - {'error': 'invalid_credentials', 'error_description':
  'Invalid user credentials', 'code': 401, 'reason': 'Unauthorized'}

<a id="cmr.auth.token.use_bearer_token"></a>

#### use\_bearer\_token

```python
def use_bearer_token(token_lambdas=None, config: dict = None)
```

Create a new config dictionary, optionally based on a supplied one, and add
the bearer token to the config object abstracting away as many details as
possible.

**Arguments**:

- `token_lambda` - a token lambda or a list of functions
- `config` - config dictionary to base new dictionary off of

**Returns**:

  new config dictionary with Bearer token assigned as an 'authorization'

<a id="cmr.auth.token.bearer"></a>

#### bearer

```python
def bearer(token_lambdas=None, config: dict = None)
```

Loops through the list of lambdas till a token is found. These lamdba functions
return an EDL token which can be passed to Earthdata software to authenticate
the user. To get a token, go to https://sit.urs.earthdata.nasa.gov/user_tokens
Token is returned as a Bearer String

**Arguments**:

- `token_lambda` - a token lambda or a list of functions
- `config` - Responds to no values

**Returns**:

  the EDL Bearer Token from the token lambda

<a id="cmr.auth.token.token"></a>

#### token

```python
def token(token_lambdas=None, config: dict = None)
```

Loops through the list of lambdas till a token is found. These lamdba functions
return an EDL token which can be passed to Earthdata software to authenticate
the user. To get a token, go to https://sit.urs.earthdata.nasa.gov/user_tokens

**Arguments**:

- `token_lambda` - a token lambda or a list of functions
- `config` - Responds to no values

**Returns**:

  the EDL Token from the token lambda

<a id="cmr.auth.token.help_text"></a>

#### help\_text

```python
def help_text(prefix: str = '') -> str
```

Built in help - prints out the public function names for the token API

**Arguments**:

- `filter` - filters out functions beginning with this text, defaults to all

**Returns**:

  text ready to be passed to print()

<a id="cmr.auth"></a>

# cmr.auth

<a id="cmr.search"></a>

# cmr.search

<a id="cmr.search.granule"></a>

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

<a id="cmr.search.granule.all_fields"></a>

#### all\_fields

```python
def all_fields(item)
```

Makes no change to the item, passes through. Used primarily as an example
and for testing the filter workflow

<a id="cmr.search.granule.meta_fields"></a>

#### meta\_fields

```python
def meta_fields(item)
```

Return only the the meta objects

<a id="cmr.search.granule.umm_fields"></a>

#### umm\_fields

```python
def umm_fields(item)
```

Return only the UMM part of the data

<a id="cmr.search.granule.concept_id_fields"></a>

#### concept\_id\_fields

```python
def concept_id_fields(item)
```

Extract only fields that are used to identify a record

<a id="cmr.search.granule.drop_fields"></a>

#### drop\_fields

```python
def drop_fields(key)
```

Drop a key from a dictionary

<a id="cmr.search.granule.granule_core_fields"></a>

#### granule\_core\_fields

```python
def granule_core_fields(item)
```

Extract only fields that are used to identify a record

<a id="cmr.search.granule.apply_filters"></a>

#### apply\_filters

```python
def apply_filters(filters, items)
```

Apply all the filters on the downloaded data

**Arguments**:

- `filters(list)` - a list of filter lambdas which taken in a row and return and row
- `items(list)` - list of records from CMR

**Returns**:

  Filtered data

<a id="cmr.search.granule.search"></a>

#### search

```python
def search(query, filters=None, limit=None, config: dict = None)
```

Search and return all records

**Arguments**:

- `query` _dictionary_ - required, CMR search parameters
- `filters` _list_ - column filter lambdas
- `limit` _int_ - number from 1 to 100000
- `config` _dictionary_ - configuration settings

**Returns**:

  JSON results from CMR

<a id="cmr.search.granule.sample_by_collections"></a>

#### sample\_by\_collections

```python
def sample_by_collections(collection_query,
                          filters=None,
                          limits=None,
                          config: dict = None)
```

Perform a compound search looking for granules based on the results of a
collection search. First find a list of collections using a supplied collection
query, then take the resulting collection IDs and perform a granule search
with them. Granule samples are then returned from many of the collections.

**Arguments**:

  collection_query(dictionary) : a collection query
- `filters(list)` - a list of filter lambdas which taken in a row and return and row
- `limits` - an int, a list of 0 to 2 int values, or a dictionary, None values will be asasumed
- `list` - [granule limit, collection limit]
- `dictionary` - {'granule': None, 'collection': None}
- `config` _dictionary_ - configuration settings

<a id="cmr.search.granule.experimental_search_generator"></a>

#### experimental\_search\_generator

```python
def experimental_search_generator(query,
                                  filters=None,
                                  limit=None,
                                  config: dict = None)
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

<a id="cmr.search.granule.open_api"></a>

#### open\_api

```python
def open_api(section='#granule-search-by-parameters')
```

Ask python to open up the API in a new browser window

**Arguments**:

- `selection(string)` - HTML Anchor Tag, default is `granule`-search-by-parameters

<a id="cmr.search.granule.set_logging_to"></a>

#### set\_logging\_to

```python
def set_logging_to(level)
```

Set the logging level to the stated value. Any of the standard logging level
as stated in https://docs.python.org/3/howto/logging.html#when-to-use-logging
can be used here. These include: DEBUG, INFO, WARNING, ERROR, and CRITICAL

**Arguments**:

- `level` - a value like logging.INFO

<a id="cmr.search.granule.help_text"></a>

#### help\_text

```python
def help_text(contains: str = "")
```

Return help for the public functions in the Granule api

<a id="cmr.search.providers"></a>

# cmr.search.providers

A Library for requesting CMR Provider Names
date: 2022-03-09
since: 0.1

A provider search for CMR. Use the search() function to lookup all the providers.
search_by_id() can be used to return only providers matching a regular expression.

<a id="cmr.search.providers.search"></a>

#### search

```python
def search(config: dict = None)
```

Search for and return providers, optional filter them

**Arguments**:

  config - configurations

**Returns**:

  JSON list of providers on success, Map with 'errors' otherwise

<a id="cmr.search.providers.search_by_id"></a>

#### search\_by\_id

```python
def search_by_id(query: str, config: dict = None)
```

Search for providers and filter them down with a Regular expression

**Arguments**:

- `filter` - RegExp string to match provider names
- `config` - configurations

**Returns**:

  JSON list of providers on success, Map with 'errors' otherwise

<a id="cmr.search.providers.set_logging_to"></a>

#### set\_logging\_to

```python
def set_logging_to(level)
```

Set the logging level to the stated value. Any of the standard logging level
as stated in https://docs.python.org/3/howto/logging.html#when-to-use-logging
can be used here. These include: DEBUG, INFO, WARNING, ERROR, and CRITICAL

**Arguments**:

- `level` - a value like logging.INFO

<a id="cmr.search.providers.open_api"></a>

#### open\_api

```python
def open_api(section='#collection-search-by-parameters')
```

Ask python to open up the API in a new browser window

<a id="cmr.search.providers.help_text"></a>

#### help\_text

```python
def help_text(contains: str = "")
```

Built in help - prints out the public function names for the collection object for the token API

**Arguments**:

- `filter(string)` - filters out functions beginning with this text, defaults to all

<a id="cmr.search.common"></a>

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

<a id="cmr.search.common.all_fields"></a>

#### all\_fields

```python
def all_fields(item)
```

Makes no change to the item, passes through. Used primarily as an example
and for testing the filter workflow

<a id="cmr.search.common.meta_fields"></a>

#### meta\_fields

```python
def meta_fields(item)
```

Return only the the meta objects

<a id="cmr.search.common.umm_fields"></a>

#### umm\_fields

```python
def umm_fields(item)
```

Return only the UMM part of the data

<a id="cmr.search.common.concept_id_fields"></a>

#### concept\_id\_fields

```python
def concept_id_fields(item)
```

Extract only fields that are used to identify a record

<a id="cmr.search.common.drop_fields"></a>

#### drop\_fields

```python
def drop_fields(key)
```

Drop a key from a dictionary

<a id="cmr.search.common.cmr_basic_url"></a>

#### cmr\_basic\_url

```python
def cmr_basic_url(base: str,
                  query: dict = None,
                  config: dict = None,
                  endpoint: str = None)
```

Create a url for calling any CMR search end point, should not make any
assumption, beyond the search directory. Will auto set the environment based
on how config is set

**Arguments**:

- `base` - API base action within the endpoint
- `query` - dictionary url parameters
- `config` - configurations, responds to:
  * env - sit, uat, ops, prod, production, or blank for production
- `endpoint` - CMR endpoint/application, like search or ingest

<a id="cmr.search.common.create_page_state"></a>

#### create\_page\_state

```python
def create_page_state(page_size=10, page_num=1, took=0, limit=10)
```

Dictionary to hold page state for the recursive call

**Arguments**:

- `page_size` - number of hits per request, can be 1-2000, default to 10
- `page_num` - current page, can be 1-50, default to 1
- `took` - positive number, seconds of total processing
- `limit` - max records to return, 1-100000, default to 10

<a id="cmr.search.common.clear_scroll"></a>

#### clear\_scroll

```python
def clear_scroll(scroll_id, config: dict = None)
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

<a id="cmr.search.common.apply_filters"></a>

#### apply\_filters

```python
def apply_filters(filters, items)
```

Apply all filters to the collection of data, returning the results

**Arguments**:

- `filters(list)` - list of or a single lambda function to apply to items
- `items(list)` - list of objects to be processed

**Returns**:

  the results of the filters

<a id="cmr.search.common.search_by_page"></a>

#### search\_by\_page

```python
def search_by_page(base,
                   query=None,
                   filters=None,
                   page_state=None,
                   config: dict = None)
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

<a id="cmr.search.common.experimental_search_by_page_generator"></a>

#### experimental\_search\_by\_page\_generator

```python
def experimental_search_by_page_generator(base,
                                          query=None,
                                          filters=None,
                                          page_state=None,
                                          config: dict = None)
```

WARNING: This is an experimental function, do not use in an operational
system, this function will go away.

This function performs searches and returns data as a list generator. Errors
will go mostly to logs.

<a id="cmr.search.common.open_api"></a>

#### open\_api

```python
def open_api(section)
```

Ask python to open up the API in a new browser window - unsupported!

<a id="cmr.search.common.set_logging_to"></a>

#### set\_logging\_to

```python
def set_logging_to(level=logging.ERROR)
```

Set the logging level to one of the levels 'CRITICAL', 'ERROR', 'WARNING',
'INFO', 'DEBUG', or 'NOTSET'.

**Arguments**:

- `level` - a value like logging.INFO or a string like 'INFO'

<a id="cmr.search.common.help_text"></a>

#### help\_text

```python
def help_text(prefix, functions, filters)
```

Built in help - prints out the public function names for the token API

**Arguments**:

- `filter(string)` - filters out functions beginning with this text, defaults to all

<a id="cmr.search.collection"></a>

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

<a id="cmr.search.collection.all_fields"></a>

#### all\_fields

```python
def all_fields(item)
```

Makes no change to the item, passes through. Used primarily as an example
and for testing the filter workflow

<a id="cmr.search.collection.meta_fields"></a>

#### meta\_fields

```python
def meta_fields(item)
```

Return only the the meta objects

<a id="cmr.search.collection.umm_fields"></a>

#### umm\_fields

```python
def umm_fields(item)
```

Return only the UMM part of the data

<a id="cmr.search.collection.concept_id_fields"></a>

#### concept\_id\_fields

```python
def concept_id_fields(item)
```

Extract only fields that are used to identify a record

<a id="cmr.search.collection.drop_fields"></a>

#### drop\_fields

```python
def drop_fields(key)
```

Drop a key from a dictionary

<a id="cmr.search.collection.collection_core_fields"></a>

#### collection\_core\_fields

```python
def collection_core_fields(item)
```

Extract only fields that are used to identify a record

<a id="cmr.search.collection.collection_ids_for_granules_fields"></a>

#### collection\_ids\_for\_granules\_fields

```python
def collection_ids_for_granules_fields(item: object)
```

Extract only the fields that are of interest to doing a granule search

<a id="cmr.search.collection.apply_filters"></a>

#### apply\_filters

```python
def apply_filters(filters, items)
```

Apply all the filters on the downloaded data

**Arguments**:

- `filters(list)` - a list of filter lambdas which taken in a row and return and row
- `items(list)` - list of records from CMR

**Returns**:

  Filtered data

<a id="cmr.search.collection.search"></a>

#### search

```python
def search(query=None, filters=None, limit=None, config: dict = None)
```

Search and return all records

<a id="cmr.search.collection.set_logging_to"></a>

#### set\_logging\_to

```python
def set_logging_to(level)
```

Set the logging level to the stated value. Any of the standard logging level
as stated in https://docs.python.org/3/howto/logging.html#when-to-use-logging
can be used here. These include: DEBUG, INFO, WARNING, ERROR, and CRITICAL

**Arguments**:

- `level` - a value like logging.INFO

<a id="cmr.search.collection.open_api"></a>

#### open\_api

```python
def open_api(section='#collection-search-by-parameters')
```

Ask python to open up the API in a new browser window

<a id="cmr.search.collection.help_text"></a>

#### help\_text

```python
def help_text(contains: str = "")
```

Built in help - prints out the public function names for the collection object for the token API

**Arguments**:

- `filter(string)` - filters out functions beginning with this text, defaults to all

