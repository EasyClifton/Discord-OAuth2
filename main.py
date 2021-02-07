from flask import Flask, request
import requests
import os
from tinydb import TinyDB, Query

app = Flask(__name__)

db = TinyDB('accessTokenDB.json')

@app.route('/')
def hello():
    print(f"All DB entries: {db.all()}")
    CODE = request.args.get("code")
    print(f"Exchanging code \"{CODE}\"")
    oauth2Response = exchange_code(CODE)
    print(f"Raw response data: {oauth2Response}")

    if "error" in oauth2Response:
      print(f"An error has occurred: Error: {oauth2Response['error']} Description: {oauth2Response['error_description']}")
      return f"An error has occurred: Error: {oauth2Response['error']} Description: {oauth2Response['error_description']}"
    
    else:
      print("Getting user ID...")
      userIDResponse = get_ID(oauth2Response["access_token"])
      print(f"Raw response data: {userIDResponse}")
      print(f"User ID: \"{userIDResponse['id']}\"")
      print("Recording user ID to access token match to DB...")
      db.insert({userIDResponse['id'] : oauth2Response['access_token']})
      print("User ID to access token match recorded successfully!")

      return f'Successfully Authorized!\nDebug: Code: {CODE}'

API_ENDPOINT = 'https://discord.com/api/v8'
CLIENT_ID = '677887351632035882'
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = 'https://discord-oauth2.easyclifton.repl.co/'

def exchange_code(code):
  data = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': REDIRECT_URI,
    'scope': 'identify guilds.join'
  }
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
  request = requests.post("%s/oauth2/token" % API_ENDPOINT, data = data, headers = headers)
  return request.json()

def get_ID(accessToken):
  headers = {
    'Authorization': f"Bearer {accessToken}"
  }
  request = requests.get("%s/users/@me" % API_ENDPOINT, headers = headers)
  return request.json()


app.run(host = '0.0.0.0', port = 8080)