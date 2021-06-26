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
            print(i)
        print()
        print()
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
        for i in tqdm(range(0, len(self.userPlaylist.getSongs())), desc="Generating Playlist"):
            time.sleep(0.2)

    # ABR = Attribute Based Recommending
    def populateNewPlaylist_ABR(self):
        artist_dict = {}
        order_dict = {}
        playlist_URI = ""
        iteration_counter = 1
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
                    acousticness_list = list(acousticness_sorted.keys())
                    acousticness_index = acousticness_list.index(str(j.getSongID()))
                    for k in range(1,(len(acousticness_list)-acousticness_index)):
                        currentSong.addSong(str(acousticness_list[acousticness_index+k]), k)
                    for k in range(1,acousticness_index):
                        currentSong.addSong(str(acousticness_list[k-1]), k)

                    danceability_sorted = sorted(danceability.items(), key=lambda x: x[1])
                    danceability_list = list(danceability_sorted.keys())
                    danceability_index = danceability_list.index(str(j.getSongID()))
                    for k in range(1, (len(danceability_list) - danceability_index)):
                        currentSong.updateNumber(str(danceability_list[danceability_index + k]), k)
                    for k in range(1, danceability_index):
                        currentSong.updateNumber(str(danceability_list[k - 1]), k)

                    energy_sorted = sorted(energy.items(), key=lambda x: x[1])
                    energy_list = list(energy_sorted.keys())
                    energy_index = energy_list.index(str(j.getSongID()))
                    for k in range(1, (len(energy_list) - energy_index)):
                        currentSong.updateNumber(str(energy_list[energy_index + k]), k)
                    for k in range(1, energy_index):
                        currentSong.updateNumber(str(energy_list[k - 1]), k)

                    instrumentalness_sorted = sorted(instrumentalness.items(), key=lambda x: x[1])
                    instrumentalness_list = list(instrumentalness_sorted.keys())
                    instrumentalness_index = instrumentalness_list.index(str(j.getSongID()))
                    for k in range(1, (len(instrumentalness_list) - instrumentalness_index)):
                        currentSong.updateNumber(str(instrumentalness_list[instrumentalness_index + k]), k)
                    for k in range(1, instrumentalness_index):
                        currentSong.updateNumber(str(instrumentalness_list[k - 1]), k)

                    liveness_sorted = sorted(liveness.items(), key=lambda x: x[1])
                    liveness_list = list(liveness_sorted.keys())
                    liveness_index = liveness_list.index(str(j.getSongID()))
                    for k in range(1, (len(liveness_list) - liveness_index)):
                        currentSong.updateNumber(str(liveness_list[liveness_index + k]), k)
                    for k in range(1, liveness_index):
                        currentSong.updateNumber(str(liveness_list[k - 1]), k)

                    speechiness_sorted = sorted(speechiness.items(), key=lambda x: x[1])
                    speechiness_list = list(speechiness_sorted.keys())
                    speechiness_index = speechiness_list.index(str(j.getSongID()))
                    for k in range(1, (len(speechiness_list) - speechiness_index)):
                        currentSong.updateNumber(str(speechiness_list[speechiness_index + k]), k)
                    for k in range(1, speechiness_index):
                        currentSong.updateNumber(str(speechiness_list[k - 1]), k)

                    valence_sorted = sorted(valence.items(), key=lambda x: x[1])
                    valence_list = list(valence_sorted.keys())
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


                    url = f"https://api.spotify.com/v1/recommendations?limit=100&seed_tracks={seed_tracks}&"
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



            iteration_counter += 1
            # acousticness = Song_Audio_Features("acousticness")
            # danceability = Song_Audio_Features("danceability")
            # energy = Song_Audio_Features("energy")
            # instrumentalness = Song_Audio_Features("instrumental")
            # liveness = Song_Audio_Features("liveness")
            # speechiness = Song_Audio_Features("speechiness")
            # valence = Song_Audio_Features("valence")
            # song_total = 0
            # for i in value:
            #     for j in artist_dict.get(i):
            #         acousticness.setMean(acousticness.getMean() + j.getAcousticness())
            #         danceability.setMean(danceability.getMean() + j.getDanceability())
            #         energy.setMean(energy.getMean() + j.getEnergy())
            #         instrumentalness.setMean(instrumentalness.getMean() + j.getInstrumentalness())
            #         liveness.setMean(liveness.getMean() + j.getLiveness())
            #         speechiness.setMean(speechiness.getMean() + j.getSpeechiness())
            #         valence.setMean(valence.getMean() + j.getValence())
            #         song_total += 1
            # acousticness.setMean(acousticness.getMean() / song_total)
            # danceability.setMean(danceability.getMean() / song_total)
            # energy.setMean(energy.getMean() / song_total)
            # instrumentalness.setMean(instrumentalness.getMean() / song_total)
            # liveness.setMean(liveness.getMean() / song_total)
            # speechiness.setMean(speechiness.getMean() / song_total)
            # valence.setMean(valence.getMean() / song_total)
            # song_total = 0
            # for i in value:
            #     for j in artist_dict.get(i):
            #         acousticness.setVariance(acousticness.getVariance() + ((j.getAcousticness() - acousticness.getMean()) ** 2))
            #         danceability.setVariance(danceability.getVariance() + ((j.getDanceability() - danceability.getMean()) ** 2))
            #         energy.setVariance(energy.getVariance() + ((j.getEnergy() - energy.getMean()) ** 2))
            #         instrumentalness.setVariance(instrumentalness.getVariance() + ((j.getInstrumentalness() - instrumentalness.getMean()) ** 2))
            #         liveness.setVariance(liveness.getVariance() + ((j.getLiveness() - liveness.getMean()) ** 2))
            #         speechiness.setVariance(speechiness.getVariance() + ((j.getSpeechiness() - speechiness.getMean()) ** 2))
            #         valence.setVariance(valence.getVariance() + ((j.getValence() - valence.getMean()) ** 2))
            #         song_total += 1
            # acousticness.setVariance(acousticness.getVariance() / (song_total - 1))
            # danceability.setVariance(danceability.getVariance() / (song_total - 1))
            # energy.setVariance(energy.getVariance() / (song_total - 1))
            # instrumentalness.setVariance(instrumentalness.getVariance() / (song_total - 1))
            # liveness.setVariance(liveness.getVariance() / (song_total - 1))
            # speechiness.setVariance(speechiness.getVariance() / (song_total - 1))
            # valence.setVariance(valence.getVariance() / (song_total - 1))
            #
            # variance_List = [acousticness, danceability, energy, instrumentalness, liveness, speechiness, valence]
            #
            # artist_url_extension = ""
            # artist_extension_list = []
            # counter = 0
            # for i in value:
            #     if counter == 5:
            #         artist_url_extension = artist_url_extension[:len(artist_url_extension) - 1]
            #         artist_url_extension += "&"
            #         artist_extension_list.append(artist_url_extension)
            #         counter = 0
            #         artist_url_extension = ""
            #     else:
            #         artist_url_extension += str(i) + ","
            #         counter += 1
            # if counter != 0:
            #     artist_extension_list.append(artist_url_extension)
            # artist_extension_list[-1] = artist_extension_list[-1][:len(artist_extension_list[-1]) - 1]
            # artist_extension_list[-1] += "&"
            #
            # attribute_url_extension = ""
            # for i in variance_List:
            #     if (i.getVariance() < 0.04):
            #         attribute_url_extension += "target_" + i.getName() + "=" + str(i.getMean()) + "&"
            #     else:
            #         attribute_url_extension += "min_" + i.getName() + "=" + str(i.getMinValue()) + "&max_" + i.getName() + "=" + str(i.getMaxValue()) + "&"
            # attribute_url_extension = attribute_url_extension[:len(attribute_url_extension) - 1]
            #
            # limit = int(key) * len(value)
            # limit_counter = 0
            # for i in artist_extension_list:
            #     print(i)
            #     if i == artist_extension_list[-1]:
            #         current_limit = limit - limit_counter
            #     else:
            #         current_limit = int(limit/len(artist_extension_list))
            #         limit_counter += current_limit
            #         if current_limit == 0:
            #             current_limit = limit
            #     url_extension = f"limit={current_limit}&seed_artists="
                # url_extension += i + attribute_url_extension
                # url = f"https://api.spotify.com/v1/recommendations?{url_extension}"
                # print(current_limit)
                # print(url)
            #     response = requests.get(
            #         url,
            #         headers={
            #             "Content-Type": "application/json",
            #             "Authorization": f"Bearer {self.client_secret}"
            #         }
            #     )
            #     response_json = response.json()
            #     #print(response_json)
            #     time.sleep(0.5)
            #     for i in response_json['tracks']:
            #         playlist_URI += (i['uri'] + ",")
            #     url_extension = f"limit={limit}&seed_artists="
            #
            # playlist_URI = playlist_URI[:len(playlist_URI) - 1]
            # url = f"https://api.spotify.com/v1/playlists/{self.userNewPlaylist.getPlaylist_ID()}/tracks?uris={playlist_URI}"
            # response = requests.post(
            #     url,
            #     headers={
            #         "Content-Type": "application/json",
            #         "Authorization": f"Bearer {self.client_secret}"
            #     }
            # )
        for i in tqdm(range(0, len(self.userPlaylist.getSongs())), desc="Generating Playlist"):
            time.sleep(0.2)
