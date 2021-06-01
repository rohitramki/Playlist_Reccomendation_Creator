import time
import json
import requests
from Song import Song

class Playlist:
    def __init__(self, client_secret, name, playlist_id):
        self.client_secret = client_secret
        self.name = name
        self.playlist_id = playlist_id
        self.songs = []

    def getSongs(self):
        return self.songs

    def getPlaylist_ID(self):
        return self.playlist_id

    def generateSongs(self):
        url = f"https://api.spotify.com/v1/playlists/{self.playlist_id}"
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.client_secret}"
            }
        )
        response_json = response.json()
        time.sleep(0.50)
        for i in response_json['tracks']['items']:
            artistName = ""
            for j in i['track']['artists']:
                artistName = j['name']
                artist_ID = j['id']
                break
            self.songs.append(Song(self.client_secret, i['track']['name'], i['track']['id'], i['track']['uri'], artistName, artist_ID))
        #print(len(self.songs))







