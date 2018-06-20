from urllib.parse import urlencode

import requests


endpoint = 'https://en.wikipedia.org/w/api.php?'
search_str = 'Einstein'
parameters = {
    'action': 'query',
    'list': 'search',
    'srsearch': search_str,
    'srlimit': 3,
    'format': 'json'
}
url = endpoint + urlencode(parameters)
headers = {'user-agent': 'my-app/0.0.1'}
response = requests.get(url, headers=headers)
print(response.json())
