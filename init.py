import requests

client_id = "ClIENT_ID"
client_secret = "CLIENT_SECRET"

#Use the client id and client secret to request the access token needed to reach specific API end points. At one point we will use this for the OAuth2.0 method for a more semi-permanent authorization
def get_access_token(client_id, client_secret):
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = "grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}".format(client_id = client_id, client_secret = client_secret)
    request = requests.post(url, headers=headers, data=data)
    json_data = request.json()
    return json_data.get("access_token")

#get access token for all future requests.
access_token = get_access_token(client_id, client_secret) 
#Basic Authorization header that is needed for all requests
authorization_header = {"Authorization": "Bearer " + access_token}

#This function will encode the data we send to Spotify. This will be helpful when we start looking at artist data and using their search function API.
def encode_uri(filter_array):
    new_filtered_params = []
    for param in filter_array:
        param = param.lower()
        if param != filter_array[-1]:
            param = param + "%2C"
            new_filtered_params.append(param)
        else:
            new_filtered_params.append(param)
    return new_filtered_params
    


#Use access token to get artist specific data in a json format. We will use this to look for specific album and track info
def get_artist_data(access_token, authorization_header):
    weeknd_spotify_id = "1Xyo4u8uXC1ZmMpatF05PJ"
    artist_url_request = "https://api.spotify.com/v1/artists/"
    authorization_header = {"Authorization": "Bearer " + access_token}
    artist_api_request = requests.get(artist_url_request + weeknd_spotify_id, headers=authorization_header)
    return artist_api_request.json()

#use search params to filter albums,artist,genre,track, and year across the spotify database
def search_spotify_database(authorization_header):  
    search_query = input('Please enter your search query: ')
    search_query = search_query.split(" ")
    search_query = "+".join(search_query)

    filter_array = input("Please enter any filters you would like to add. Ex - Artist, Playlist, Album, or Track. Please seperate filter with a ',' ")
    filter_array = filter_array.split(",")
    filtered_params = encode_uri(filter_array)
    filtered_params = "".join(filtered_params)

    search_url = "https://api.spotify.com/v1/search?q=" + search_query + "&type="
    search_request = requests.get(search_url + filtered_params, headers=authorization_header)
    results_json = search_request.json()
    return results_json
