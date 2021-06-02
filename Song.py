import json
import requests
import time

class Song:
    def __init__(self, client_secret, name, song_id, song_uri, artist, artist_ID):
        self.name = name
        self.song_id = song_id
        self.artist = artist
        self.artist_ID = artist_ID
        self.client_secret = client_secret
        self.song_uri = song_uri
        self.danceabllity = None
        self.energy = None
        self.key = None
        self.loudness = None
        self.mode = None
        self.speechiness = None
        self.acousticness = None
        self.instrumentalness = None
        self.liveness = None
        self.valence = None
        self.tempo = None
        self.genre = None

    def __str__(self):
        return self.name + " - " + self.artist

    def __repr__(self):
        return self.name + " - " + self.artist

    def getAcousticness(self):
        return self.acousticness

    def getDanceability(self):
        return self.danceabllity

    def getEnergy(self):
        return self.energy

    def getInstrumentalness(self):
        return self.instrumentalness

    def getKey(self):
        return self.key

    def getLiveness(self):
        return self.liveness

    def getLoudness(self):
        return self.loudness

    def getMode(self):
        return self.mode

    def getSpeechiness(self):
        return self.speechiness

    def getTempo(self):
        return self.tempo

    def getValence(self):
        return self.valence

    def getURI(self):
        return self.song_uri

    def getSongName(self):
        return self.name

    def getSongID(self):
        return self.song_id

    def getSongArtist(self):
        return self.artist

    def getArtistID(self):
        return self.artist_ID

    def getGenre(self):
        return self.genre

    def generateAudioAnalysis(self):
        url = f"https://api.spotify.com/v1/audio-features/{self.song_id}"
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.client_secret}"
            }
        )
        time.sleep(0.50)
        response_json = response.json()
        self.danceabllity = response_json['danceability']
        self.energy = response_json['energy']
        self.key = response_json['key']
        self.loudness = response_json['loudness']
        self.mode = response_json['mode']
        self.speechiness = response_json['speechiness']
        self.acousticness = response_json['acousticness']
        self.instrumentalness = response_json['instrumentalness']
        self.liveness = response_json['liveness']
        self.valence = response_json['valence']
        self.tempo = response_json['tempo']

    def generateGenre(self):
        url = f"https://api.spotify.com/v1/artists/{self.artist_ID}"
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.client_secret}"
            }
        )
        time.sleep(0.3)
        response_json = response.json()
        self.genre = response_json['genres']
