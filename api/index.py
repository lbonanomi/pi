from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from requests.auth import HTTPBasicAuth
import random


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        token_value = os.environ['GITHUB_TOKEN']

        plain_user = HTTPBasicAuth('', token_value)

        mutuals = []

        payload = { "query": "query { user(login: \"lbonanomi\") { following(first:100) { nodes { login following(first: 100) { edges { node { login }}}}}}}" }

        data=json.dumps(payload)

        graphql = requests.post("https://api.github.com/graphql", data=data, auth=plain_user)

        for x in graphql.json()['data']['user']['following']['nodes']:
	        for y in x['following']['edges']:
		        if y['node']['login'] == 'lbonanomi':
			        mutuals.append(x['login'])

        random_mutual = 'https://github.com/' + random.choice(mutuals)
        
        self.send_response(302)
        self.send_header('Location',random_mutual)
        self.end_headers()
        return
