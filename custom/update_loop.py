import requests


credentials = 'your_zendesk_email', 'your_zendesk_password'
zendesk = 'https://your_subdomain.zendesk.com'

posts = [1, 2, 3]                       # post ids
update = {'post': {'name': 'value'}}    # property to be updated

for post in posts:
    url = zendesk + '/api/v2/community/posts/{}.json'.format(post)
    response = requests.put(url, json=update, auth=credentials)
    if response.status_code != 200:
        print('Failed to update record with error {}'.format(response.status_code))
