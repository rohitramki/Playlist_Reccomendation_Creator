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
        # print(option)
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
        for i in self.userPlaylist.getSongs():
            for j in i.getArtistID():
                if (j in artist_dict.keys()):
                    artist_dict[j].append(i)
                else:
                    artist_dict[j] = []
                    artist_dict[j].append(i)
        print(artist_dict)
        for key, value in artist_dict.items():
            if (key in order_dict.keys()):
                order_dict[str(len(value))].append(key)
            else:
                order_dict[str(len(value))] = []
                order_dict[str(len(value))].append(key)
        print(order_dict)
        # genre_dict = {}
        # for i in self.userPlaylist.getSongs():
        #     for j in i.getGenre():
        #         if (len(j) != 0):
        #             if j in genre_dict.keys():
        #                 genre_dict[j].append(i)
        #             else:
        #                 genre_dict[j] = []
        #                 genre_dict[j].append(i)
        # print(genre_dict)
        # first_highest = [-1, "", []]
        # second_highest = [-1, "", []]
        # third_highest = [-1, "", []]
        # for key, value in genre_dict.items():
        #     print(first_highest[0])
        #     print(first_highest[1])
        #     print(second_highest[0])
        #     print(second_highest[1])
        #     print(third_highest[0])
        #     print(third_highest[1])
        #     if (first_highest[0] < len(value)):
        #         third_highest[0] = second_highest[0]
        #         third_highest[1] = second_highest[1]
        #         third_highest[2] = second_highest[2]
        #         second_highest[0] = first_highest[0]
        #         second_highest[1] = first_highest[1]
        #         second_highest[2] = first_highest[2]
        #         first_highest[0] = len(value)
        #         first_highest[1] = key.replace(' ', '-')
        #         first_highest[2] = value
        #     elif (second_highest[0] < len(value)):
        #         print("second")
        #         third_highest[0] = second_highest[0]
        #         third_highest[1] = second_highest[1]
        #         third_highest[2] = second_highest[2]
        #         second_highest[0] = len(value)
        #         second_highest[1] = key.replace(' ', '-')
        #         second_highest[2] = value
        #     elif (third_highest[0] < len(value)):
        #         print("third")
        #         third_highest[0] = len(value)
        #         third_highest[1] = key.replace(' ', '-')
        #         third_highest[2] = value
        # genre_dict.clear()
        # genre_dict = {
        #     first_highest[1]: first_highest[2],
        #     second_highest[1]: second_highest[2],
        #     third_highest[1]: third_highest[2]
        # }
        counter = 1
        for key, value in artist_dict.items():
            acousticness = Song_Audio_Features("acousticness")
            danceability = Song_Audio_Features("danceability")
            energy = Song_Audio_Features("energy")
            instrumentalness = Song_Audio_Features("instrumental")
            liveness = Song_Audio_Features("liveness")
            speechiness = Song_Audio_Features("speechiness")
            valence = Song_Audio_Features("valence")
            for i in value:
                acousticness.setMean(acousticness.getMean() + i.getAcousticness())
                danceability.setMean(danceability.getMean() + i.getDanceability())
                energy.setMean(energy.getMean() + i.getEnergy())
                instrumentalness.setMean(instrumentalness.getMean() + i.getInstrumentalness())
                liveness.setMean(liveness.getMean() + i.getLiveness())
                speechiness.setMean(speechiness.getMean() + i.getSpeechiness())
                valence.setMean(valence.getMean() + i.getValence())
            acousticness.setMean(acousticness.getMean() / len(value))
            danceability.setMean(danceability.getMean() / len(value))
            energy.setMean(energy.getMean() / len(value))
            instrumentalness.setMean(instrumentalness.getMean() / len(value))
            liveness.setMean(liveness.getMean() / len(value))
            speechiness.setMean(speechiness.getMean() / len(value))
            valence.setMean(valence.getMean() / len(value))
            for i in value:
                acousticness.setVariance(acousticness.getVariance() + ((i.getAcousticness() - acousticness.getMean()) ** 2))
                danceability.setVariance(danceability.getVariance() + ((i.getDanceability() - danceability.getMean()) ** 2))
                energy.setVariance(energy.getVariance() + ((i.getEnergy() - energy.getMean()) ** 2))
                instrumentalness.setVariance(instrumentalness.getVariance() + ((i.getInstrumentalness() - instrumentalness.getMean()) ** 2))
                liveness.setVariance(liveness.getVariance() + ((i.getLiveness() - liveness.getMean()) ** 2))
                speechiness.setVariance(speechiness.getVariance() + ((i.getSpeechiness() - speechiness.getMean()) ** 2))
                valence.setVariance(valence.getVariance() + ((i.getValence() - valence.getMean()) ** 2))
            acousticness.setVariance(acousticness.getVariance() / (len(value) - 1))
            danceability.setVariance(danceability.getVariance() / (len(value) - 1))
            energy.setVariance(energy.getVariance() / (len(value) - 1))
            instrumentalness.setVariance(instrumentalness.getVariance() / (len(value) - 1))
            liveness.setVariance(liveness.getVariance() / (len(value) - 1))
            speechiness.setVariance(speechiness.getVariance() / (len(value) - 1))
            valence.setVariance(valence.getVariance() / (len(value) - 1))

            variance_List = [acousticness, danceability, energy, instrumentalness, liveness, speechiness, valence]
            url_extension = ""
            # if counter == 1:
            #     limit = round((first_highest[0] / (first_highest[0] + second_highest[0] + third_highest[0])) * 10)
            #     url_extension = f"limit={limit}&seed_genres={first_highest[1]}&"
            # elif counter == 2:
            #     limit = round((second_highest[0] / (first_highest[0] + second_highest[0] + third_highest[0])) * 10)
            #     url_extension = f"limit={limit}&seed_genres={second_highest[1]}&"
            # elif counter == 3:
            #     limit = len(self.userPlaylist.getSongs()) - (round((first_highest[0] / (first_highest[0] + second_highest[0] + third_highest[0])) * 10) + round((second_highest[0] / (first_highest[0] + second_highest[0] + third_highest[0])) * 10))
            #     url_extension = f"limit={limit}&seed_genres={third_highest[1]}&"
            # for i in variance_List:
            #     if (i.getVariance() < 0.04):
            #         url_extension += "target_" + i.getName() + "=" + str(i.getMean()) + "&"
            #     else:
            #         url_extension += "min_" + i.getName() + "=" + str(i.getMinValue()) + "&max_" + i.getName() + "=" + str(i.getMaxValue()) + "&"
            # url_extension = url_extension[:len(url_extension) - 1]
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
            print(response_json)
            print()
            print()
            counter += 1

