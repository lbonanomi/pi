from base64 import b64encode
from http.server import BaseHTTPRequestHandler
import http.client
import json
import os
import random

token_value = os.environ['GITHUB_TOKEN']

payload = { "query": "query { user(login: \"lbonanomi\") { following(first:100) { nodes { login following(first: 100) { edges { node { login }}}}}}}" }

data = json.dumps(payload)

headers = {"Content-type": "application/json", "Authorization": "bearer " + token_value, "User-Agent": "python3"}


conn = http.client.HTTPSConnection("api.github.com")

conn.request('POST', '/graphql', data, headers)

response = conn.getresponse()


a = response.read().decode()

mutuals = []

b = json.loads(a)

for x in b['data']['user']['following']['nodes']:
        for y in x['following']['edges']:
                if y['node']['login'] == 'lbonanomi':
                        mutuals.append(x['login'])


random_mutual = 'https://github.com/' + random.choice(mutuals)

self.send_response(302)
self.send_header('Location',random_mutual)
self.end_headers()
return
