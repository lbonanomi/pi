from base64 import b64encode
from http.server import BaseHTTPRequestHandler
import http.client
import json
import os
import random
import redis
from urllib.parse import urlparse


class handler(BaseHTTPRequestHandler):
  def whoami(self, token):
    
    headers = {"Content-type": "application/json", "Authorization": "bearer " + token, "User-Agent": "python3"}

    try:
      conn = http.client.HTTPSConnection("api.github.com")
      conn.request('GET', '/user', headers=headers)

      whoami_resp = conn.getresponse().read().decode()
      callme = json.loads(whoami_resp)['login']
    except Exception as e:
      #print("TOKEN:", token[6:], "ERROR:", e, "WUT", json.loads(whoami_resp))
      
      self.send_response(502)
      self.send_header('Content-type','text/plain')
      self.end_headers()
      self.wfile.write("Could not determine calling-user\n".encode('utf-8'))
      return
      
    return callme
    
  def find_comrades(self, token, redis_config, callme):
    headers = {"Content-type": "application/json", "Authorization": "bearer " + token, "User-Agent": "python3"}
    
    mutuals = []

    r = redis.Redis(
      host=redis_config.hostname, 
      port=redis_config.port,
      username=redis_config.username, 
      password=redis_config.password,
      decode_responses=True,
      ssl=True
    )
    
    payload = { "query": "query { user(login: \"" + callme + "\") { following(first:100) { nodes { login following(first: 100) { edges { node { login }}}}}}}" }

    data = json.dumps(payload)

    conn = http.client.HTTPSConnection("api.github.com")
    
    conn.request('POST', '/graphql', data, headers)

    response = conn.getresponse()

    a = response.read().decode()
    b = json.loads(a)

    for x in b['data']['user']['following']['nodes']:
      for y in x['following']['edges']:
        if y['node']['login'] == callme:
          mutuals.append(x['login'])
          r.sadd("mutuals", x['login'])


  def do_PUT(self):
    try:
      redis_uri = os.environ['KV_URL']
      redis_config = urlparse(redis_uri)
    except Exception:
      self.send_response(501)
      self.send_header('Content-type','text/plain')
      self.end_headers()
      self.wfile.write('Could not find Redis.'.encode('utf-8'))
      return
    
    r = redis.Redis(
      host=redis_config.hostname, 
      port=redis_config.port,
      username=redis_config.username, 
      password=redis_config.password,
      decode_responses=True,
      ssl=True
    )

    # Get username of whoever registered the GH token with Vercel
    # into the variable "callme"
    token_value = os.environ['GITHUB_TOKEN']

    callme = self.whoami(token_value)
    comrades = self.find_comrades(token_value, redis_config, callme)    

  
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

    random_mutual = 'https://github.com/' + r.srandmember("mutuals")

    self.send_response(302)
    self.send_header('Location',random_mutual)
    self.end_headers()
    return
