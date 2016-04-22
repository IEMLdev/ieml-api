import requests

url = 'http://localhost:5000'

r = requests.post(url + '/api/validate_text', data='{"propositions" : [], "tags" : {} }')
print(r.text)