import json
import requests
import time
from Song import Song
from Playlist import Playlist
from Song_Audio_Features import Song_Audio_Features
from tqdm import tqdm
from STSRC import STSRC

class SpotifyClient:
    def __init__(self, client_secret, name, user_id):
        self.client_secret = client_secret
        self.name = name
        self.user_id = user_id
        self.userPlaylist = None
        self.userNewPlaylist = None

    def getUserName(self):
        return self.name

    def getUserPlayList(self):
        return self.userPlaylist

    def getNewUserPlaylist(self):
        return self.userNewPlaylist

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
        newPlaylist_ID = []
        playlist_URIs = ""
        for i in self.userPlaylist.getSongs():
            playlist_ID.append(i.getSongID())
        for i in playlist_ID:
            url = f"https://api.spotify.com/v1/recommendations?limit=100&seed_tracks={i}"
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
                if (j['id'] not in playlist_ID) or (j['id'] not in newPlaylist_ID):
                    newPlaylist_ID.append(j['id'])
                    playlist_URIs += (j['uri'] + ",")
                    break
        for i in tqdm(range(0, len(self.userPlaylist.getSongs())), desc="Generating Playlist"):
            time.sleep(0.2)
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
        playlist_ID = []
        newPlaylist_ID = []
        playlist_URIs = ""
        duplicate_artists = []
        nonduplicate_artists = []

        for i in self.userPlaylist.getSongs():
            if (i.getArtistID() in nonduplicate_artists) and (i.getArtistID() not in duplicate_artists):
                duplicate_artists.append(i.getArtistID())
            elif (i.getArtistID not in duplicate_artists):
                nonduplicate_artists.append(i.getArtistID())

        for j in self.userPlaylist.getSongs():
            playlist_ID.append(j.getSongID())
            #STSRC = Song to Song Relationship Container
            currentSong = STSRC(str(j.getSongID()))
            acousticness = {}
            danceability = {}
            energy = {}
            instrumentalness = {}
            liveness = {}
            speechiness = {}
            valence = {}
            #for k in value:
            for k in self.userPlaylist.getSongs():
                acousticness[str(k.getSongID())] = k.getAcousticness()
                danceability[str(k.getSongID())] = k.getDanceability()
                energy[str(k.getSongID())] = k.getEnergy()
                instrumentalness[str(k.getSongID())] = k.getInstrumentalness()
                liveness[str(k.getSongID())] = k.getLiveness()
                speechiness[str(k.getSongID())] = k.getSpeechiness()
                valence[str(k.getSongID())] = k.getValence()

            acousticness_sorted = list(sorted(acousticness.items(), key=lambda x: x[1]))
            acousticness_list = []
            for k in acousticness_sorted:
                acousticness_list.append(k[0])
            acousticness_index = acousticness_list.index(str(j.getSongID()))
            for k in range(1, (len(acousticness_list)-acousticness_index)):
                currentSong.addSong(str(acousticness_list[acousticness_index+k]), k)
            for k in range(acousticness_index):
                currentSong.addSong(str(acousticness_list[k]), k+1)

            danceability_sorted = list(sorted(danceability.items(), key=lambda x: x[1]))
            danceability_list = []
            for k in danceability_sorted:
                danceability_list.append(k[0])
            danceability_index = danceability_list.index(str(j.getSongID()))
            for k in range(1, (len(danceability_list) - danceability_index)):
                currentSong.updateNumber(str(danceability_list[danceability_index + k]), k)
            for k in range(danceability_index):
                currentSong.updateNumber(str(danceability_list[k]), k+1)

            energy_sorted = list(sorted(energy.items(), key=lambda x: x[1]))
            energy_list = []
            for k in energy_sorted:
                energy_list.append(k[0])
            energy_index = energy_list.index(str(j.getSongID()))
            for k in range(1, (len(energy_list) - energy_index)):
                currentSong.updateNumber(str(energy_list[energy_index + k]), k)
            for k in range(energy_index):
                currentSong.updateNumber(str(energy_list[k]), k+1)

            instrumentalness_sorted = list(sorted(instrumentalness.items(), key=lambda x: x[1]))
            instrumentalness_list = []
            for k in instrumentalness_sorted:
                instrumentalness_list.append(k[0])
            instrumentalness_index = instrumentalness_list.index(str(j.getSongID()))
            for k in range(1, (len(instrumentalness_list) - instrumentalness_index)):
                currentSong.updateNumber(str(instrumentalness_list[instrumentalness_index + k]), k)
            for k in range(instrumentalness_index):
                currentSong.updateNumber(str(instrumentalness_list[k]), k+1)

            liveness_sorted = list(sorted(liveness.items(), key=lambda x: x[1]))
            liveness_list = []
            for k in liveness_sorted:
                liveness_list.append(k[0])
            liveness_index = liveness_list.index(str(j.getSongID()))
            for k in range(1, (len(liveness_list) - liveness_index)):
                currentSong.updateNumber(str(liveness_list[liveness_index + k]), k)
            for k in range(liveness_index):
                currentSong.updateNumber(str(liveness_list[k]), k+1)

            speechiness_sorted = list(sorted(speechiness.items(), key=lambda x: x[1]))
            speechiness_list = []
            for k in speechiness_sorted:
                speechiness_list.append(k[0])
            speechiness_index = speechiness_list.index(str(j.getSongID()))
            for k in range(1, (len(speechiness_list) - speechiness_index)):
                currentSong.updateNumber(str(speechiness_list[speechiness_index + k]), k)
            for k in range(speechiness_index):
                currentSong.updateNumber(str(speechiness_list[k]), k+1)

            valence_sorted = list(sorted(valence.items(), key=lambda x: x[1]))
            valence_list = []
            for k in valence_sorted:
                valence_list.append(k[0])
            valence_index = valence_list.index(str(j.getSongID()))
            for k in range(1, (len(valence_list) - valence_index)):
                currentSong.updateNumber(str(valence_list[valence_index + k]), k)
            for k in range(valence_index):
                currentSong.updateNumber(str(valence_list[k]), k+1)

            lowestValues = -1
            if j.getArtistID() in duplicate_artists:
                lowestValues = currentSong.produceLowestValues(3)
            else:
                lowestValues = currentSong.produceLowestValues(4)

            seed_tracks = ""
            for k in lowestValues:
                seed_tracks += str(k) + ","
            seed_tracks = seed_tracks[:len(seed_tracks) - 1]
            if len(lowestValues) == 4:
                url = f"https://api.spotify.com/v1/recommendations?limit=100&seed_tracks={seed_tracks}&" \
                      f"target_acousticness={j.getAcousticness()}&target_danceability={j.getDanceability()}" \
                      f"&target_energy={j.getEnergy()}&target_instrumentalness={j.getInstrumentalness()}" \
                      f"&target_liveness={j.getLiveness()}&target_speechiness={j.getSpeechiness()}&target_valence={j.getValence()}"
            else:
                url = f"https://api.spotify.com/v1/recommendations?limit=100&seed_artists={j.getArtistID()}&seed_tracks={seed_tracks}&" \
                      f"target_acousticness={j.getAcousticness()}&target_danceability={j.getDanceability()}" \
                      f"&target_energy={j.getEnergy()}&target_instrumentalness={j.getInstrumentalness()}" \
                      f"&target_liveness={j.getLiveness()}&target_speechiness={j.getSpeechiness()}&target_valence={j.getValence()}"
            response = requests.get(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.client_secret}"
                }
            )
            response_json = response.json()
            time.sleep(0.2)

            for k in response_json['tracks']:
                if (k['id'] not in playlist_ID) or (k['id'] not in newPlaylist_ID):
                    newPlaylist_ID.append(k['id'])
                    playlist_URIs += (k['uri'] + ",")
                    break

        for i in tqdm(range(0, len(self.userPlaylist.getSongs())), desc="Generating Playlist"):
            time.sleep(0.2)

        playlist_URIs = playlist_URIs[:len(playlist_URIs) - 1]
        url = f"https://api.spotify.com/v1/playlists/{self.userNewPlaylist.getPlaylist_ID()}/tracks?uris={playlist_URIs}"
        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.client_secret}"
            }
        )