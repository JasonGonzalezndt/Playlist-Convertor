from flask import Flask, render_template, request, redirect, session
import requests
import urllib.parse
from waitress import serve
import string
import random
import base64

#setup variables for getting through the API endpoints
client_id = "CLIENT_ID"
client_secret = "CLIENT_SECRET"
redirect_uri = "http://127.0.0.1:5000/callback"
scope = "playlist-read-private playlist-read-collaborative user-follow-read playlist-modify-public playlist-modify-private user-read-private user-read-email"
token_url = "https://accounts.spotify.com/api/token"
base_api_url = 'https://api.spotify.com'
#At some point I need to set up the state variable so the site is safer. keywords some point
#state = ''.join(random.choice(string.ascii_uppercase + string.digits)for _ in range(16))

app = Flask(__name__)
app.secret_key= ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16)) #encoded secret key needed to authenticate for OAuth
encoded_client_headers = base64.b64encode((client_id + ':' + client_secret).encode('utf-8'))
string_decoded_client_headers = encoded_client_headers.decode('utf-8') #string decoded headers needed for OAuth

#initial home page that promopts the user to login through a button
@app.route("/")
def home():
    return render_template('login.html')

#callback URL after successful login. If this works use the 'code' returned to complete the OAuth access_token trade
@app.route('/callback')
def callback():
    code = request.args.get('code') #get the code from the URL
    
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
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        return redirect('playlist')
    else:
        return "Something went wrong please try again"
    
    
#actual login linked through clicking the button on the homepage
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

#using the helper function get_playlists to provide a list of your playlists, images, and links to more info in a boxed format
@app.route('/playlist')
def show_playlist():
    if 'access_token' not in session:
        return redirect('/login')
        
    playlists = get_playlists()
    return render_template('playlist.html', playlists=playlists)

#Use the playlist name that is clicked from the show_playlist template. Compare the name to find the right link and use that link to get more detailed playlist info like tracks
@app.route('/playlist/<playlist_name>')
def show_playlist_data(playlist_name):
    playlist_data = get_playlists()
    playlist_name = playlist_name
    for i in range(len(playlist_data)):
        if playlist_data[i].get('name') != playlist_name:
            continue
        else:
            playlist_link = playlist_data[i].get('href')
            detailed_playlist_info = get_playlist_tracks(playlist_link)
            track_data = detailed_playlist_info['items']
            track_data_array = [{'name': track['track']['name'], 'artist': track['track']['artists'][0]['name'], 'added_by': track['added_by']['id'], 'image': track['track']['album']['images'][-1]['url']} # forgive the list comprehension that's probably(?) difficult to read off the bat. EDIT - For sure no reason for this lmao but it's done and I don't want to put in the effort to adjust
                                 for track in track_data]                                        
    return render_template('trackdata.html', track_data_array=track_data_array)

#Helper function to refresh a token. This will later be added to all requests after checking if access_token is valid
def get_refresh_token():
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

#helper function to get the name, image, and href for all of the items in the playlist.json file.
def get_playlists():
    auth_header = {'Authorization' : 'Bearer ' + session['access_token']}
    playlist_request = requests.get(base_api_url + '/v1/me/playlists', headers=auth_header)

    if 'access_token' in session and playlist_request.status_code == 200:
        playlist_data = playlist_request.json()
        playlist_data = playlist_data['items']
        
        return [{'name': p.get('name'), 'image': p['images'][0]['url'], 'href': p['tracks']['href']}
                for p in playlist_data]       
    return []

def get_playlist_tracks(playlist_url): #get playlist track data. We will use this as a helper function to gather playlist names as well.
    auth_header = {'Authorization' : 'Bearer ' + session['access_token']}
    playlist_request = requests.get(playlist_url, headers=auth_header)
    playlist_request = playlist_request.json()

    return playlist_request 

#get track names. This will be used when getting a list of names to send to Apple's API
def get_track_names(playlist_url):
    auth_header = {'Authorization' : 'Bearer ' + session['access_token']}
    playlist_request = requests.get(playlist_url, headers=auth_header)
    playlist_request = playlist_request.json()
    track_names = [{'name': track['track']['name']} for track in playlist_request]

    return track_names

def get_user_id():
    auth_header = {'Authorization' : 'Bearer ' + session['access_token']}
    user_id_request = requests.get(base_api_url + '/me', headers=auth_header)
    user_id_request = user_id_request.json()
    user_id = user_id_request['id']
    print(user_id)
    return user_id


if __name__ == '__main__':
    app.run(debug=True)
