import json
import os
import requests
# Iterate over pages of graphql retrieving the search after cursor to do so
token = os.getenv('TOKEN')
# graphql-address e.g. 'https://graphql.sit.earthdata.nasa.gov/api'
endpoint = os.getenv('GRAPHQL_URL')
# Bearer may be needed before the token if you are using a personal token
headers = {"Authorization": f"{token}"}
cursor = ""
page_num = 0
query = """query ($params: CollectionsInput) {
  collections(params: $params) {
    cursor
    items {
      conceptId
    }
  }
}"""

variables = """{
  "params":{
    "limit":1,
    "cursor":"%s"
  }
}"""% (cursor)

response = requests.post(url=endpoint, json={"query": query, "variables": variables}, headers=headers)
first_result = response.json()
# Retrieve the first cursor value
cursor = first_result.get('data', {}).get('collections', {}).get('cursor')
print("Response status code: ", response.status_code)

if response.status_code == 200:
    arr = []
    while(cursor):
        # update variable by passing in the cursor with the updated value
        variables = """{
        "params":{
            "limit":1000,
            "cursor":"%s"
        }
        }"""% (cursor)
        print('current page', page_num)
        print('search_after cursor value', cursor)
        response = requests.post(url=endpoint, json={"query": query, "variables": variables}, headers=headers)
        result = response.json()
        collections = result.get('data', {}).get('collections', {}).get('items', [])
        cursor = result.get('data', {}).get('collections', {}).get('cursor')
        # print("Response in json: ", collections)
        for collection in collections:
            arr.append(collection.get('conceptId'))
        page_num = page_num + 1
  
    print('total number of pages', page_num)
    arr.sort()
    # Write the sorted concept-id list to a local folder
    with open("collectionConceptIdList.txt", "w") as txt_file:
        for collection in arr:
            txt_file.write(f"{collection}\n")