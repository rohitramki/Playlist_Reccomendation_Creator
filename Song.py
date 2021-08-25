import json
import requests
import time


class Song:
    # Song object instantiation, sets up all the attributes, name, ids, uri, and client secret
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

    # Song Object print and string methods
    def __str__(self):
        return self.name + " - " + self.artist

    def __repr__(self):
        return self.name + " - " + self.artist

    # Method that allows Spotify Get API calls to be done
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

    # Getter methods for all the Song attributes
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

    # This method gets the attributes from a given song and stores the attributes within the Song object
    def generateAudioAnalysis(self):
        url = f"https://api.spotify.com/v1/audio-features/{self.song_id}"
        response_json = self.spotifyGETAPICall(url)
        # delays the program after the api call to ensure that too many calls aren't being made
        time.sleep(0.50)
        # Sets all of the music attributes to variables
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

    # Stores the genre of a given song
    def generateGenre(self):
        url = f"https://api.spotify.com/v1/artists/{self.artist_ID}"
        response_json = self.spotifyGETAPICall(url)
        # delays the program after the api call to ensure that too many calls aren't being made
        time.sleep(0.3)
        # Sets the genre variable to the value that the api call outputted
        self.genre = response_json['genres']
