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
        artist_dict = {}
        order_dict = {}
        playlist_ID = []
        newPlaylist_ID = []
        playlist_URIs = ""
        iteration_counter = 1
        for i in self.userPlaylist.getSongs():
            playlist_ID.append(i.getSongID())
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
        for key, value in order_dict.items():
            for i in value:
                for j in artist_dict.get(i):
                    #STSRC = Song to Song Relationship Container
                    currentSong = STSRC(str(j.getSongID()))
                    acousticness = {}
                    danceability = {}
                    energy = {}
                    instrumentalness = {}
                    liveness = {}
                    speechiness = {}
                    valence = {}
                    for k in artist_dict.get(i):
                        acousticness[str(k.getSongID())] = k.getAcousticness()
                        danceability[str(k.getSongID())] = k.getDanceability()
                        energy[str(k.getSongID())] = k.getEnergy()
                        instrumentalness[str(k.getSongID())] = k.getInstrumentalness()
                        liveness[str(k.getSongID())] = k.getLiveness()
                        speechiness[str(k.getSongID())] = k.getSpeechiness()
                        valence[str(k.getSongID())] = k.getValence()

                    acousticness_sorted = sorted(acousticness.items(), key=lambda x: x[1])
                    acousticness_list = []
                    for k in acousticness_sorted:
                        acousticness_list.append(k[0])
                    acousticness_index = acousticness_list.index(str(j.getSongID()))
                    for k in range(1,(len(acousticness_list)-acousticness_index)):
                        currentSong.addSong(str(acousticness_list[acousticness_index+k]), k)
                    for k in range(1,acousticness_index):
                        currentSong.addSong(str(acousticness_list[k-1]), k)

                    danceability_sorted = sorted(danceability.items(), key=lambda x: x[1])
                    danceability_list = []
                    for k in danceability_sorted:
                        danceability_list.append(k[0])
                    danceability_index = danceability_list.index(str(j.getSongID()))
                    for k in range(1, (len(danceability_list) - danceability_index)):
                        currentSong.updateNumber(str(danceability_list[danceability_index + k]), k)
                    for k in range(1, danceability_index):
                        currentSong.updateNumber(str(danceability_list[k - 1]), k)

                    energy_sorted = sorted(energy.items(), key=lambda x: x[1])
                    energy_list = []
                    for k in energy_sorted:
                        energy_list.append(k[0])
                    energy_index = energy_list.index(str(j.getSongID()))
                    for k in range(1, (len(energy_list) - energy_index)):
                        currentSong.updateNumber(str(energy_list[energy_index + k]), k)
                    for k in range(1, energy_index):
                        currentSong.updateNumber(str(energy_list[k - 1]), k)

                    instrumentalness_sorted = sorted(instrumentalness.items(), key=lambda x: x[1])
                    instrumentalness_list = []
                    for k in instrumentalness_sorted:
                        instrumentalness_list.append(k[0])
                    instrumentalness_index = instrumentalness_list.index(str(j.getSongID()))
                    for k in range(1, (len(instrumentalness_list) - instrumentalness_index)):
                        currentSong.updateNumber(str(instrumentalness_list[instrumentalness_index + k]), k)
                    for k in range(1, instrumentalness_index):
                        currentSong.updateNumber(str(instrumentalness_list[k - 1]), k)

                    liveness_sorted = sorted(liveness.items(), key=lambda x: x[1])
                    liveness_list = []
                    for k in liveness_sorted:
                        liveness_list.append(k[0])
                    liveness_index = liveness_list.index(str(j.getSongID()))
                    for k in range(1, (len(liveness_list) - liveness_index)):
                        currentSong.updateNumber(str(liveness_list[liveness_index + k]), k)
                    for k in range(1, liveness_index):
                        currentSong.updateNumber(str(liveness_list[k - 1]), k)

                    speechiness_sorted = sorted(speechiness.items(), key=lambda x: x[1])
                    speechiness_list = []
                    for k in speechiness_sorted:
                        speechiness_list.append(k[0])
                    speechiness_index = speechiness_list.index(str(j.getSongID()))
                    for k in range(1, (len(speechiness_list) - speechiness_index)):
                        currentSong.updateNumber(str(speechiness_list[speechiness_index + k]), k)
                    for k in range(1, speechiness_index):
                        currentSong.updateNumber(str(speechiness_list[k - 1]), k)

                    valence_sorted = sorted(valence.items(), key=lambda x: x[1])
                    valence_list = []
                    for k in valence_sorted:
                        valence_list.append(k[0])
                    valence_index = valence_list.index(str(j.getSongID()))
                    for k in range(1, (len(valence_list) - valence_index)):
                        currentSong.updateNumber(str(valence_list[valence_index + k]), k)
                    for k in range(1, valence_index):
                        currentSong.updateNumber(str(valence_list[k - 1]), k)

                    if iteration_counter == 1:
                        lowestValues = currentSong.produceLowestValues(4)
                    else:
                        lowestValues = currentSong.produceLowestValues(3)

                    seed_tracks = ""
                    for k in lowestValues:
                        seed_tracks += str(k) + ","
                    seed_tracks = seed_tracks[:len(seed_tracks) - 1]

                    url = f"https://api.spotify.com/v1/recommendations?limit=100&seed_tracks={seed_tracks}&" \
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

                    print(url)
                    print()
                    print()
                    print()
                    print(response_json)
                    for k in response_json['tracks']:
                        if (k['id'] not in playlist_ID) or (k['id'] not in newPlaylist_ID):
                            newPlaylist_ID.append(k['id'])
                            playlist_URIs += (k['uri'] + ",")
                            break

            iteration_counter += 1

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