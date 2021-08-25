# Imports for the Playlist class
import time
import json
import requests
from Song import Song

class Playlist:
    # Instantiation for the Playlist class
    def __init__(self, client_secret, name, playlist_id):
        self.client_secret = client_secret
        self.name = name
        self.playlist_id = playlist_id
        self.songs = []

    def spotifyGETAPICall(self, url):
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.client_secret}"
            }
        )
        return response.json()

    # Method that allows Spotify Post API calls to be done
    def spotifyPOSTAPICall(self, url, playlistName=None, description=None):
        # If a new playlist is being created then a certain api call is done, otherwise a generic api call is called
        if playlistName is not None and description is not None:
            response = requests.post(
                url,
                json.dumps({
                    "name": playlistName,
                    "description": description
                }),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.client_secret}"
                }
            )
        else:
            response = requests.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.client_secret}"
                }
            )

    # Getter methods for the Playlist class
    def getName(self):
        return self.name

    def getSongs(self):
        return self.songs

    def getPlaylist_ID(self):
        return self.playlist_id

    # Calls the Spotify api for getting playlist songs and stores the songs in a list format and stores it in the
    # songs variable.
    def generateSongs(self):
        # By using the playlist_id variable, a spotify api call is made to get information about a playlist
        url = f"https://api.spotify.com/v1/playlists/{self.playlist_id}"
        response_json = self.spotifyGETAPICall(url)
        # Wait time to slow down api calls and avoid issues with Spotify API
        time.sleep(0.50)
        # Goes through the api call data and creates Song objects a put these Songs object into the songs variable as
        # a list
        for i in response_json['tracks']['items']:
            artistName = ""
            for j in i['track']['artists']:
                artistName = j['name']
                artist_ID = j['id']
                break
            playlist_Song = Song(self.client_secret, i['track']['name'], i['track']['id'], i['track']['uri'], artistName, artist_ID)
            playlist_Song.generateAudioAnalysis()
            self.songs.append(playlist_Song)
