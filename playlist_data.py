import json
import pprint

f = open('playlist_data.json')

data = json.load(f)


playlist_data = data['items']

def get_info():
    track_data = [{'name': p.get('name'), 'image': p['images'][0]['url'], 'href': p['tracks']['href']}
        for p in playlist_data]
    
    return track_data

print(get_info())