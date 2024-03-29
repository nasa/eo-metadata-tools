# Document-it report
All the code 'document-it' tags are listed here by package
## `cmr`

## `API Version`

0.0.1

## `cmr.auth.token`

### `token_config()`

* `cmr.token.value` (defaults to `None`).

### `token_file()`


### `token_manager()`

* `token.manager.account` (defaults to `user`).
* `token.manager.service` (defaults to `cmr-lib-token`).
* `token.manager.app` (defaults to `/usr/bin/security`).

## `cmr.search.collection`

### `search()`

  * also from `cmr.search.common.search_by_page`
    * `max-time` (defaults to `300000`).
      * also from `cmr.search.common._make_search_request`
        * `accept` (defaults to `application/vnd.nasa.cmr.umm_results+json`).
          * also from `cmr.search.common._standard_headers_from_config`
            * `Authorization` (defaults to `None`). Notes: also known as a cmr or EDL token
            * `X-Request-id` (defaults to `None`).
            * `Client-Id` (defaults to `python_cmr_lib`).
            * `User-Agent` (defaults to `python_cmr_lib`).
          * also from `cmr.search.common._cmr_query_url`
              * also from `cmr.search.common.cmr_basic_url`
                * `env` (defaults to ``). Notes: uat, ops, prod, production, or blank for ops

## `cmr.search.common`

### `clear_scroll()`

  * also from `cmr.search.common._standard_headers_from_config`
    * `Authorization` (defaults to `None`). Notes: also known as a cmr or EDL token
    * `X-Request-id` (defaults to `None`).
    * `Client-Id` (defaults to `python_cmr_lib`).
    * `User-Agent` (defaults to `python_cmr_lib`).
  * also from `cmr.search.common.cmr_basic_url`
    * `env` (defaults to ``). Notes: uat, ops, prod, production, or blank for ops

### `cmr_basic_url()`

* `env` (defaults to ``). Notes: uat, ops, prod, production, or blank for ops

### `experimental_search_by_page_generator()`

  * also from `cmr.search.common._make_search_request`
    * `accept` (defaults to `application/vnd.nasa.cmr.umm_results+json`).
      * also from `cmr.search.common._standard_headers_from_config`
        * `Authorization` (defaults to `None`). Notes: also known as a cmr or EDL token
        * `X-Request-id` (defaults to `None`).
        * `Client-Id` (defaults to `python_cmr_lib`).
        * `User-Agent` (defaults to `python_cmr_lib`).
      * also from `cmr.search.common._cmr_query_url`
          * also from `cmr.search.common.cmr_basic_url`
            * `env` (defaults to ``). Notes: uat, ops, prod, production, or blank for ops

### `search_by_page()`

* `max-time` (defaults to `300000`).
  * also from `cmr.search.common._make_search_request`
    * `accept` (defaults to `application/vnd.nasa.cmr.umm_results+json`).
      * also from `cmr.search.common._standard_headers_from_config`
        * `Authorization` (defaults to `None`). Notes: also known as a cmr or EDL token
        * `X-Request-id` (defaults to `None`).
        * `Client-Id` (defaults to `python_cmr_lib`).
        * `User-Agent` (defaults to `python_cmr_lib`).
      * also from `cmr.search.common._cmr_query_url`
          * also from `cmr.search.common.cmr_basic_url`
            * `env` (defaults to ``). Notes: uat, ops, prod, production, or blank for ops

## `cmr.search.granule`

### `experimental_search_generator()`

  * also from `cmr.search.common.experimental_search_by_page_generator`
      * also from `cmr.search.common._make_search_request`
        * `accept` (defaults to `application/vnd.nasa.cmr.umm_results+json`).
          * also from `cmr.search.common._standard_headers_from_config`
            * `Authorization` (defaults to `None`). Notes: also known as a cmr or EDL token
            * `X-Request-id` (defaults to `None`).
            * `Client-Id` (defaults to `python_cmr_lib`).
            * `User-Agent` (defaults to `python_cmr_lib`).
          * also from `cmr.search.common._cmr_query_url`
              * also from `cmr.search.common.cmr_basic_url`
                * `env` (defaults to ``). Notes: uat, ops, prod, production, or blank for ops

### `search()`

  * also from `cmr.search.common.search_by_page`
    * `max-time` (defaults to `300000`).
      * also from `cmr.search.common._make_search_request`
        * `accept` (defaults to `application/vnd.nasa.cmr.umm_results+json`).
          * also from `cmr.search.common._standard_headers_from_config`
            * `Authorization` (defaults to `None`). Notes: also known as a cmr or EDL token
            * `X-Request-id` (defaults to `None`).
            * `Client-Id` (defaults to `python_cmr_lib`).
            * `User-Agent` (defaults to `python_cmr_lib`).
          * also from `cmr.search.common._cmr_query_url`
              * also from `cmr.search.common.cmr_basic_url`
                * `env` (defaults to ``). Notes: uat, ops, prod, production, or blank for ops

----
CMR Library - NASA - Copyright 2023-01-25
Created 2023-01-25 15:34:07
