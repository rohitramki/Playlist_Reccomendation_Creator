# Import packages and other python files
import json
import requests
import time
from SpotifyClient import SpotifyClient

# This variable contains the client secret which is used for every Spotify api. In order to run this program, you must
# get a new client secret which can be accessed using this link:
# https://developer.spotify.com/console/get-playlist/?playlist_id=59ZbFPES4DQwEjBpWHzrtC&user_id=spotify
client_secret = "BQCbUE4gTs1qGGYjdf3jUdK3zDHlZHVgxluFvRVWmUA3r1EaCHBmzbprn-s5Uw_-Tkgi4QLVeRR0uOsK_y323zIl44G5ZAhvtKJd0zS78iVQ_Sk3yEKtCvD80n78XR3R5cnEOZwsOFYIXTb1XZvQW2pkZWvl6aXhnY4wHoKKtsG8AHAS9h_74VAkhPfOkkCHPw1tdV0_IrTv0g9Yh5qTSPd0jPZbgi3beZUv0NMonRSvLqNQ1DY22FGgkHiL84V59oPhU3sN80df0Niu8RKWnCMyC-ISThrJgDly0U6Q"

def main():
    try:
        # Spotify API call to get the user's name and client id
        url = "https://api.spotify.com/v1/me"
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {client_secret}"
            }
        )
        # stores the json response into a list and uses the information to instantiate a SpotifyClient object
        response_json = response.json()
        sc = SpotifyClient(client_secret, response_json['display_name'], response_json['id'])
        print("Hey " + sc.getUserName() + ",")
        # Asks user for a playlist to generate from, and will continue to ask until a valid playlist is inputted
        checker = False
        while (checker == False):
            playListName = input("What playlist would you like to generate from? ")
            checker = sc.setPlaylist(playListName)
            if (checker == False):
                print("Invalid Playlist name")
        # Records the new playlist name and the sc variable calls the generateNewPlaylist function in order to
        # create a new empty playlist
        newPlaylistName = input("Please enter a name for the new playlist: ")
        sc.generateNewPlaylist(newPlaylistName)
        # Asks the user to either generate based on the Spotify's Recommendation algorithm or based on an each song's
        # attributes by pressing either 1 or 2 respectively. If another number is inputed then then the question is
        # asked again
        generationOptions = 0
        while (generationOptions != 1) and (generationOptions != 2):
            print("Press 1 to generate a playlist based on Spotify's Recommendation System")
            print("Press 2 to generate a playlist based on your music's attributes")
            generationOptions = int(input("Input: "))
            if (generationOptions != 1) and (generationOptions != 2):
                print("Invalid Input")
        if (generationOptions == 1):
            sc.populateNewPlaylist_SBR()
            print("'" + sc.getNewUserPlaylist().getName() + "' has successfully been generated!")
        elif (generationOptions == 2):
            sc.populateNewPlaylist_ABR()
            print("'" + sc.getNewUserPlaylist().getName() + "' has successfully been generated!")
            pass
    except:
        print("Invalid or expired token")


if __name__ == "__main__":
    main()
