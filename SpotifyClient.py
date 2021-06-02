import json
import requests
import time
from Song import Song
from Playlist import Playlist
from Song_Audio_Features import Song_Audio_Features


class SpotifyClient:
    def __init__(self, client_secret, name, user_id):
        self.client_secret = client_secret
        self.name = name
        self.user_id = user_id
        self.userPlaylist = None
        self.userNewPlaylist = None

    def getUserName(self):
        return self.name

    def getuserPlayList(self):
        return self.userPlaylist

    def setPlaylist(self, userInput, option=0):
        url = f"https://api.spotify.com/v1/users/{self.user_id}/playlists"
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.client_secret}"
            }
        )
        response_json = response.json()
        time.sleep(0.50)
        userInput = userInput.lower()
        for i in response_json['items']:
            if (i['name'].lower() == userInput):
                if (option == 0):
                    self.userPlaylist = Playlist(self.client_secret, i['name'], i['id'])
                    self.userPlaylist.generateSongs()
                    return True
                elif (option == 1):
                    self.userNewPlaylist = Playlist(self.client_secret, i['name'], i['id'])
                    return True
        return False

    def searchPlaylist(self, userInput):
        url = f"https://api.spotify.com/v1/users/{self.user_id}/playlists"
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.client_secret}"
            }
        )
        time.sleep(0.5)
        response_json = response.json()
        userInput = userInput.lower()
        for i in response_json['items']:
            if (i['name'].lower() == userInput):
                playlist = Playlist(self.client_secret, i['name'], i['id'])
                playlist.generateSongs()
                return playlist
        return None

    def generateNewPlaylist(self, newPlaylistName):
        url = f"https://api.spotify.com/v1/users/{self.user_id}/playlists"
        response = requests.post(
            url,
            json.dumps({
                "name": newPlaylistName,
                "description": "Recommended songs"
            }),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.client_secret}"
            }
        )
        self.setPlaylist(newPlaylistName, 1)

    # SBR = Spotify Based Recommending
    def populateNewPlaylist_SBR(self):
        playlist_ID = []
        playlist_URIs = ""
        for i in self.userPlaylist.getSongs():
            playlist_ID.append(i.getSongID())
        for i in playlist_ID:
            url = f"https://api.spotify.com/v1/recommendations?seed_tracks={i}"
            response = requests.get(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.client_secret}"
                }
            )
            response_json = response.json()
            time.sleep(0.2)
            for j in response_json['tracks']:
                playlist_URIs += (j['uri'] + ",")
                break

        playlist_URIs = playlist_URIs[:len(playlist_URIs) - 1]
        url = f"https://api.spotify.com/v1/playlists/{self.userNewPlaylist.getPlaylist_ID()}/tracks?uris={playlist_URIs}"
        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.client_secret}"
            }
        )

    # ABR = Attribute Based Recommending
    def populateNewPlaylist_ABR(self):
        artist_dict = {}
        order_dict = {}
        playlist_URIs = ""
        for i in self.userPlaylist.getSongs():
            if (i.getArtistID() in artist_dict.keys()):
                artist_dict[i.getArtistID()].append(i)
            else:
                artist_dict[i.getArtistID()] = []
                artist_dict[i.getArtistID()].append(i)
        for key, value in artist_dict.items():
            if (str(len(value)) in order_dict.keys()):
                order_dict[str(len(value))].append(key)
            else:
                order_dict[str(len(value))] = []
                order_dict[str(len(value))].append(key)
        song_counter = 1
        for key, value in order_dict.items():
            acousticness = Song_Audio_Features("acousticness")
            danceability = Song_Audio_Features("danceability")
            energy = Song_Audio_Features("energy")
            instrumentalness = Song_Audio_Features("instrumental")
            liveness = Song_Audio_Features("liveness")
            speechiness = Song_Audio_Features("speechiness")
            valence = Song_Audio_Features("valence")
            song_total = 0
            for i in value:
                for j in artist_dict.get(i):
                    acousticness.setMean(acousticness.getMean() + j.getAcousticness())
                    danceability.setMean(danceability.getMean() + j.getDanceability())
                    energy.setMean(energy.getMean() + j.getEnergy())
                    instrumentalness.setMean(instrumentalness.getMean() + j.getInstrumentalness())
                    liveness.setMean(liveness.getMean() + j.getLiveness())
                    speechiness.setMean(speechiness.getMean() + j.getSpeechiness())
                    valence.setMean(valence.getMean() + j.getValence())
                    song_total += 1
            acousticness.setMean(acousticness.getMean() / song_total)
            danceability.setMean(danceability.getMean() / song_total)
            energy.setMean(energy.getMean() / song_total)
            instrumentalness.setMean(instrumentalness.getMean() / song_total)
            liveness.setMean(liveness.getMean() / song_total)
            speechiness.setMean(speechiness.getMean() / song_total)
            valence.setMean(valence.getMean() / song_total)
            song_total = 0
            for i in value:
                for j in artist_dict.get(i):
                    acousticness.setVariance(acousticness.getVariance() + ((j.getAcousticness() - acousticness.getMean()) ** 2))
                    danceability.setVariance(danceability.getVariance() + ((j.getDanceability() - danceability.getMean()) ** 2))
                    energy.setVariance(energy.getVariance() + ((j.getEnergy() - energy.getMean()) ** 2))
                    instrumentalness.setVariance(instrumentalness.getVariance() + ((j.getInstrumentalness() - instrumentalness.getMean()) ** 2))
                    liveness.setVariance(liveness.getVariance() + ((j.getLiveness() - liveness.getMean()) ** 2))
                    speechiness.setVariance(speechiness.getVariance() + ((j.getSpeechiness() - speechiness.getMean()) ** 2))
                    valence.setVariance(valence.getVariance() + ((j.getValence() - valence.getMean()) ** 2))
                    song_total += 1
            acousticness.setVariance(acousticness.getVariance() / (song_total - 1))
            danceability.setVariance(danceability.getVariance() / (song_total - 1))
            energy.setVariance(energy.getVariance() / (song_total - 1))
            instrumentalness.setVariance(instrumentalness.getVariance() / (song_total - 1))
            liveness.setVariance(liveness.getVariance() / (song_total - 1))
            speechiness.setVariance(speechiness.getVariance() / (song_total - 1))
            valence.setVariance(valence.getVariance() / (song_total - 1))

            variance_List = [acousticness, danceability, energy, instrumentalness, liveness, speechiness, valence]
            limit = int(key) * len(value)
            song_counter += limit
            url_extension = f"limit={limit}&seed_artists="
            artist_ID_Concatenation = ""
            for i in value:
                url_extension += str(i) + ","
            url_extension = url_extension[:len(artist_ID_Concatenation) - 1]
            url_extension += "&"

            for i in variance_List:
                if (i.getVariance() < 0.04):
                    url_extension += "target_" + i.getName() + "=" + str(i.getMean()) + "&"
                else:
                    url_extension += "min_" + i.getName() + "=" + str(i.getMinValue()) + "&max_" + i.getName() + "=" + str(i.getMaxValue()) + "&"
            url_extension = url_extension[:len(url_extension) - 1]
            url = f"https://api.spotify.com/v1/recommendations?{url_extension}"
            response = requests.get(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.client_secret}"
                }
            )
            response_json = response.json()
            time.sleep(0.50)
            for i in response_json['tracks']:
                playlist_URIs += (i['uri'] + ",")
        playlist_URIs = playlist_URIs[:len(playlist_URIs) - 1]
        url = f"https://api.spotify.com/v1/playlists/{self.userNewPlaylist.getPlaylist_ID()}/tracks?uris={playlist_URIs}"
        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.client_secret}"
            }
        )

