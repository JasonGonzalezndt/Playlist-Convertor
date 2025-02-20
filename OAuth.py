from flask import Flask, render_template, request, redirect, session
import requests
import urllib.parse
from waitress import serve
import string
import random
import base64
import pprint
import json

client_id = "31f021cb56984c9b8103e5046b8dc836"
client_secret = "733f3230209c4b84bd1c380e78e51fdd"
redirect_uri = "http://127.0.0.1:5000/callback"
scope = "playlist-read-private playlist-read-collaborative user-follow-read"
token_url = "https://accounts.spotify.com/api/token"
base_api_url = 'https://api.spotify.com'
#state = ''.join(random.choice(string.ascii_uppercase + string.digits)for _ in range(16))
app = Flask(__name__)
app.secret_key= ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
encoded_client_headers = base64.b64encode((client_id + ':' + client_secret).encode('utf-8'))
string_decoded_client_headers = encoded_client_headers.decode('utf-8')

@app.route("/")
def home():
    return render_template('login.html')

@app.route('/callback')
def callback():
    code = request.args.get('code')
    
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + string_decoded_client_headers
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }
    if code:
        token_data = requests.post(token_url, headers=headers, data=data)
        if token_data.status_code != 200:
            return "Authorization failed please try again"
        token_info = token_data.json()
        print(token_info)
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        return redirect('playlist')
    else:
        return "Something went wrong please try again"
    
    

@app.route("/login")
def login_page():
    auth_url = 'https://accounts.spotify.com/authorize'

    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': scope,
        'show_dialog': 'true',
    }
    params = urllib.parse.urlencode(params)
    full_url = f"{auth_url}?{params}"
    return redirect(full_url)


@app.route('/playlist')
def show_playlist():

    auth_header = {'Authorization' : 'Bearer ' + session['access_token']}
    playlist_request = requests.get(base_api_url + '/v1/me/playlists', headers=auth_header)

    if 'access_token' in session and playlist_request.status_code == 200:
        playlist_data = playlist_request.json()
        playlist_data = playlist_data['items']
        
        #for i in range(len(playlist_data)):
            #print(playlist_data[i].get('name'))
        playlist_name_one = playlist_data[0].get('name')
        return f'Your most recent playlist is {playlist_name_one}'
    else:
        return 'We encountered an issue please try again.'


#function to refresh the token after 1 hour

def refresh_token():
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': session['refresh_token']
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    refresh_data = requests.post(token_url, headers=headers, data=data)
    if refresh_data.status_code == 200:
        refresh_data = refresh_data.json()
        if session['access_token'] != refresh_data['access_token']:
            session['access_token'] = refresh_data['access_token']
            if refresh_data['refresh_token']:
                session['refresh_token'] = refresh_data['refresh_token']
            

if __name__ == '__main__':
    app.run(debug=True)