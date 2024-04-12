from base64 import b64encode
from http.server import BaseHTTPRequestHandler
import http.client
import json
import os
import random
import redis
from urllib.parse import urlparse


class handler(BaseHTTPRequestHandler):
  def do_PUT(self):    

    redis_uri = os.environ['KV_URL']
    redis_config = urlparse(redis_uri)
    
    r = redis.Redis(
      host=redis_config.hostname, 
      port=redis_config.port,
      username=redis_config.username, 
      password=redis_config.password,
      ssl=True
    )
    
    token_value = os.environ['GITHUB_TOKEN']

    headers = {"Content-type": "application/json", "Authorization": "bearer " + token_value, "User-Agent": "python3"}

    conn = http.client.HTTPSConnection("api.github.com")
    conn.request('GET', '/user', headers=headers)

    try:
      whoami = conn.getresponse().read().decode()
      callme = json.loads(whoami)['login']
    except KeyError:
      # Author routinely runs out of GH tokens,
      # so handle that
      self.send_response(302)
      self.send_header('Location', 'https://www.sonypictures.com/movies/thenet')
      self.end_headers()
      return
          
    payload = { "query": "query { user(login: \"" + callme + "\") { following(first:100) { nodes { login following(first: 100) { edges { node { login }}}}}}}" }

    data = json.dumps(payload)

    conn.request('POST', '/graphql', data, headers)

    response = conn.getresponse()

    a = response.read().decode()

    mutuals = []

    b = json.loads(a)

    for x in b['data']['user']['following']['nodes']:
      for y in x['following']['edges']:
        if y['node']['login'] == callme:
          mutuals.append(x['login'])


        random_mutual = 'https://github.com/' + random.choice(mutuals)
    
  def do_GET(self):

    redis_uri = os.environ['KV_URL']
    redis_config = urlparse(redis_uri)
    
    r = redis.Redis(
      host=redis_config.hostname, 
      port=redis_config.port,
      username=redis_config.username, 
      password=redis_config.password,
      decode_responses=True,
      ssl=True
    )

    random_mutual = r.srandmember("mutuals")

    self.send_response(302)
    self.send_header('Location',random_mutual)
    self.end_headers()
    return
