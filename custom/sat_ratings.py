import os
import requests

ticket_id = 2334547707
root = 'https://nadosolutions.zendesk.com/api/v2/'
url = os.path.join(root, 'satisfaction_ratings', f'{ticket_id}.json')
response = requests.get(url,  auth=('chucknado@outlook.com', 'falcon63'))
print(response.json())
