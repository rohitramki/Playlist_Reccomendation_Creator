# Imports for SpotifyClient class
import json
import requests
import time
from Playlist import Playlist
from tqdm import tqdm
from STSRC import STSRC

class SpotifyClient:
    # Instantiation of the SpotifyClient class
    def __init__(self, client_secret, name, user_id):
        self.client_secret = client_secret
        self.name = name
        self.user_id = user_id
        self.userPlaylist = None
        self.userNewPlaylist = None

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

    # Getter methods for the SpotifyClient class
    def getUserName(self):
        return self.name

    def getUserPlaylist(self):
        return self.userPlaylist

    def getNewUserPlaylist(self):
        return self.userNewPlaylist

    # Based on the user inputed playlist name, this function sets the userPlaylist variable to a Playlist object and
    # preforms the generateSongs function.
    def setPlaylist(self, userInput, option=0):
        # Spotify API call to get information about the user's playlists
        url = f"https://api.spotify.com/v1/users/{self.user_id}/playlists?limit=50"
        response_json = self.spotifyGETAPICall(url)
        # Wait time to slow down api calls and avoid issues with Spotify API
        time.sleep(0.30)
        # If the user inputed name is found (regardless of capitalization or trailing white spaces) within a list of
        # the user's Spotify playlists
        # If the option variable is 0, then the userPlaylist variable is set to a Playlist object, the generateSongs
        # function is executed, and true is returned. Otherwise false is returned
        # If the option variable is 1, then the userNewPlaylist variable is set to a new Playlist object, and true is
        # returned.
        userInput = userInput.lower()
        if userInput[len(userInput) - 1:] == " ":
            userInput = userInput[:len(userInput) - 1]
        for i in response_json['items']:
            if (i['name'].lower() == userInput) or (i['name'][len(i['name'])-1:] == " " and i['name'][:len(i['name'])-1] == userInput):
                if option == 0:
                    self.userPlaylist = Playlist(self.client_secret, i['name'], i['id'])
                    self.userPlaylist.generateSongs()
                    return True
                elif option == 1:
                    self.userNewPlaylist = Playlist(self.client_secret, i['name'], i['id'])
                    return True
        return False

    # Uses the Spotify API to create a blank playlist
    def generateNewPlaylist(self, newPlaylistName):
        # Spotify API call to create an empty playlist
        url = f"https://api.spotify.com/v1/users/{self.user_id}/playlists"
        self.spotifyPOSTAPICall(url, newPlaylistName, "Recommended songs")
        self.setPlaylist(newPlaylistName, 1)

    # SBR = Spotify Based Recommending
    def populateNewPlaylist_SBR(self):
        playlist_ID = []
        newPlaylist_ID = []
        playlist_URIs = ""
        # Obtains all of the song ids from the user's playlist
        for i in self.userPlaylist.getSongs():
            playlist_ID.append(i.getSongID())
        # iterates through each song in the user's playlist
        for i in playlist_ID:
            # Spotify API call to get recommendation songs
            url = f"https://api.spotify.com/v1/recommendations?limit=100&seed_tracks={i}"
            response_json = self.spotifyGETAPICall(url)
            # delays the program after the api call to ensure that too many calls aren't being made
            time.sleep(0.2)
            # Iterates through the song recommendations if the song isn't already in the user's playlist, or if the song
            # isn't already in the new playlist, the playlist URI is added to a string and the song id is added to an
            # array
            for j in response_json['tracks']:
                if (j['id'] not in playlist_ID) and (j['id'] not in newPlaylist_ID):
                    newPlaylist_ID.append(j['id'])
                    playlist_URIs += (j['uri'] + ",")
                    break
        # Uses the tqdm library to generate a progress bar (mainly for stylistic purposes)
        for i in tqdm(range(0, len(self.userPlaylist.getSongs())), desc="Generating Playlist"):
            time.sleep(0.2)
        # Removes the last character (an extra comma) from the playlist_URI string
        playlist_URIs = playlist_URIs[:len(playlist_URIs) - 1]
        # Spotify API POST call that adds all the recommended songs to the new playlist
        url = f"https://api.spotify.com/v1/playlists/{self.userNewPlaylist.getPlaylist_ID()}/tracks?uris={playlist_URIs}"
        self.spotifyPOSTAPICall(url)

    # ABR = Attribute Based Recommending
    def populateNewPlaylist_ABR(self):
        playlist_ID = []
        newPlaylist_ID = []
        playlist_URIs = ""
        duplicate_artists = []
        nonduplicate_artists = []

        # Iterates through each song of the user's playlist and records each song's ID, and segregates songs into songs
        # with artists that show up multiple times in a playlist and artists that show up only once in a playlist
        for i in self.userPlaylist.getSongs():
            # places the user's song's id into a list
            playlist_ID.append(i.getSongID())
            # if a artist is in the nonduplicate artist list and not in the duplicate artist list then the artist is put
            # into the duplicate artist list. Otherwise if the the artist is not already in the duplicate artist list,
            # then the artist is placed into the nonduplicate artist list.
            # The purpose is to find all the duplicate artists, the non-duplicate artist list is to make sure that
            # all the duplicate artist list is accurate and that all the duplicate artists are accounted for
            if (i.getArtistID() in nonduplicate_artists) and (i.getArtistID() not in duplicate_artists):
                duplicate_artists.append(i.getArtistID())
            elif (i.getArtistID not in duplicate_artists):
                nonduplicate_artists.append(i.getArtistID())

        for j in self.userPlaylist.getSongs():
            # STSRC = Song to Song Relationship Container
            currentSong = STSRC(str(j.getSongID()))
            acousticness = {}
            danceability = {}
            energy = {}
            instrumentalness = {}
            liveness = {}
            speechiness = {}
            valence = {}

            # Iterates through the user's playlist and sets all the music attributes to each song from the user's
            # playlist
            for k in self.userPlaylist.getSongs():
                acousticness[str(k.getSongID())] = k.getAcousticness()
                danceability[str(k.getSongID())] = k.getDanceability()
                energy[str(k.getSongID())] = k.getEnergy()
                instrumentalness[str(k.getSongID())] = k.getInstrumentalness()
                liveness[str(k.getSongID())] = k.getLiveness()
                speechiness[str(k.getSongID())] = k.getSpeechiness()
                valence[str(k.getSongID())] = k.getValence()

            # Sorts the acousticness values of all the songs from lowest to highest
            acousticness_sorted = list(sorted(acousticness.items(), key=lambda x: x[1]))
            acousticness_list = []
            # Puts all the song ids in lowest to highest order based on their acousticness values
            for k in acousticness_sorted:
                acousticness_list.append(k[0])
            # Finds the index of the current song in the sorted acousticness_list
            acousticness_index = acousticness_list.index(str(j.getSongID()))
            # iterates through the acousticness_list from one value higher than the acousticness_index till the end of
            # the accousticness_list and assigns the values based on how far from the iterated song is from the current
            # song that is being calculated
            for k in range(1, (len(acousticness_list) - acousticness_index)):
                currentSong.addSong(str(acousticness_list[acousticness_index + k]), k)
            # iterates through the first song to the song before the accousticness_index song the accousticness_list and
            # assigns the values based on how far from the iterated song is from the current song that is being
            # calculated
            for k in range(acousticness_index):
                currentSong.addSong(str(acousticness_list[k]), k + 1)

            # Same exact code from the accousticness attribute but instead for danceability
            danceability_sorted = list(sorted(danceability.items(), key=lambda x: x[1]))
            danceability_list = []
            for k in danceability_sorted:
                danceability_list.append(k[0])
            danceability_index = danceability_list.index(str(j.getSongID()))
            for k in range(1, (len(danceability_list) - danceability_index)):
                currentSong.updateNumber(str(danceability_list[danceability_index + k]), k)
            for k in range(danceability_index):
                currentSong.updateNumber(str(danceability_list[k]), k + 1)

            # Same exact code from the accousticness attribute but instead for energy
            energy_sorted = list(sorted(energy.items(), key=lambda x: x[1]))
            energy_list = []
            for k in energy_sorted:
                energy_list.append(k[0])
            energy_index = energy_list.index(str(j.getSongID()))
            for k in range(1, (len(energy_list) - energy_index)):
                currentSong.updateNumber(str(energy_list[energy_index + k]), k)
            for k in range(energy_index):
                currentSong.updateNumber(str(energy_list[k]), k + 1)

            # Same exact code from the accousticness attribute but instead for instrumentalness
            instrumentalness_sorted = list(sorted(instrumentalness.items(), key=lambda x: x[1]))
            instrumentalness_list = []
            for k in instrumentalness_sorted:
                instrumentalness_list.append(k[0])
            instrumentalness_index = instrumentalness_list.index(str(j.getSongID()))
            for k in range(1, (len(instrumentalness_list) - instrumentalness_index)):
                currentSong.updateNumber(str(instrumentalness_list[instrumentalness_index + k]), k)
            for k in range(instrumentalness_index):
                currentSong.updateNumber(str(instrumentalness_list[k]), k + 1)

            # Same exact code from the accousticness attribute but instead for liveness
            liveness_sorted = list(sorted(liveness.items(), key=lambda x: x[1]))
            liveness_list = []
            for k in liveness_sorted:
                liveness_list.append(k[0])
            liveness_index = liveness_list.index(str(j.getSongID()))
            for k in range(1, (len(liveness_list) - liveness_index)):
                currentSong.updateNumber(str(liveness_list[liveness_index + k]), k)
            for k in range(liveness_index):
                currentSong.updateNumber(str(liveness_list[k]), k + 1)

            # Same exact code from the accousticness attribute but instead for speechiness
            speechiness_sorted = list(sorted(speechiness.items(), key=lambda x: x[1]))
            speechiness_list = []
            for k in speechiness_sorted:
                speechiness_list.append(k[0])
            speechiness_index = speechiness_list.index(str(j.getSongID()))
            for k in range(1, (len(speechiness_list) - speechiness_index)):
                currentSong.updateNumber(str(speechiness_list[speechiness_index + k]), k)
            for k in range(speechiness_index):
                currentSong.updateNumber(str(speechiness_list[k]), k + 1)

            # Same exact code from the accousticness attribute but instead for valence
            valence_sorted = list(sorted(valence.items(), key=lambda x: x[1]))
            valence_list = []
            for k in valence_sorted:
                valence_list.append(k[0])
            valence_index = valence_list.index(str(j.getSongID()))
            for k in range(1, (len(valence_list) - valence_index)):
                currentSong.updateNumber(str(valence_list[valence_index + k]), k)
            for k in range(valence_index):
                currentSong.updateNumber(str(valence_list[k]), k + 1)

            # figures if the current song's artist is a duplicate artist or not and constructs a list of the closest
            # 3 songs (if the artist is a duplicate) or the closest 4 songs (if the artist is not a duplicate)
            lowestValues = -1
            if j.getArtistID() in duplicate_artists:
                lowestValues = currentSong.produceLowestValues(3)
            else:
                lowestValues = currentSong.produceLowestValues(4)

            # seed_tracks is a string that is all of the closest song's ids and adds a comma (line 272 removes the
            # trailing comma
            seed_tracks = ""
            for k in lowestValues:
                seed_tracks += str(k) + ","
            seed_tracks = seed_tracks[:len(seed_tracks) - 1]
            # constructs one of two different urls based on if lowestValues had 4 songs or 3 songs (depending on if the
            # current song has a duplicate artist or not
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
            # Preforms a Spotify API get call on the constructed url to get a list of the closest songs
            response_json = self.spotifyGETAPICall(url)
            # To prevent too many calls on the Spotify API
            time.sleep(0.2)

            # Filters through the API call data and finds the closest song to the current song that isn't already in the
            # new playlist or the old playlist
            # The URI of the new song is appended to a newPlaylist_ID list and is concatenated on a playlist_URIs string
            # with a comma
            for k in response_json['tracks']:
                if (k['id'] not in playlist_ID) and (k['id'] not in newPlaylist_ID):
                    newPlaylist_ID.append(k['id'])
                    playlist_URIs += (k['uri'] + ",")
                    break

        # Uses the tqdm library to generate a progress bar (mainly for stylistic purposes)
        for i in tqdm(range(0, len(self.userPlaylist.getSongs())), desc="Generating Playlist"):
            time.sleep(0.2)

        # trailing comma to the playlist_URIs string is removed
        playlist_URIs = playlist_URIs[:len(playlist_URIs) - 1]
        # url is produced and a POST call is made in order to add the new songs to the new playlist
        url = f"https://api.spotify.com/v1/playlists/{self.userNewPlaylist.getPlaylist_ID()}/tracks?uris={playlist_URIs}"
        self.spotifyPOSTAPICall(url)
