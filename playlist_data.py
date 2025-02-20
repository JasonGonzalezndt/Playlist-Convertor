import json
import pprint

f = open('playlist_data.json')

data = json.load(f)


playlist_data = data['items']

for i in range(len(playlist_data)):
    print(playlist_data[i].get('name'))
