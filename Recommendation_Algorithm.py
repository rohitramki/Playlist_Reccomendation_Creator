import json
import requests
import time
from SpotifyClient import SpotifyClient
client_id = "pjp1yehfstdvh1uu0ni3m9sak"
client_secret = "BQBGS9lpthYFxWc6ArsNtOpSEhFFy6vuWyFjvJKqiBzj8R-UXHUebnZbr6PyutGciwk1XE3jb1fHGEr9eqdkGC1vUcRchyJL8B6rkKiTtbKe1wCdULZ9ciSF34Jy1hPZWc3VyDvjRFuqW-PYYdJINzP4_zK470Qc1s_uhwvfGn_5iY4oGM7P96-nDHubv__pvMgCmAUHZr-1qc-dx9mToAQd5JJc18EiZSHh3v2bW2Nq-Rz_fQ"

playlist_id = "2muKAmURcXAGdYLZBoVz7p"

def main():
    #importlib.import_module("SpotifyClient")
    #c_ID = input("Please enter the Client ID: ")
    #authorization_Token = input("Please enter an Authorization Token: ")


    #url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    #url = f"https://api.spotify.com/v1/users/{client_id}/playlists"

    #try:
    url = "https://api.spotify.com/v1/me"
    response = requests.get(
        url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {client_secret}"
        }
    )
    response_json = response.json()
    sc = SpotifyClient(client_secret, response_json['display_name'], response_json['id'])
    print("Hey " + sc.getUserName() + ",")
    checker = False
    while(checker == False):
        playListName = input("What playlist would you like to generate from? ")
        checker = sc.setPlaylist(playListName)
        if (checker == False):
            print("Invalid Playlist name")
    newPlaylistName = input("Please enter a name for the new playlist: ")
    sc.generateNewPlaylist(newPlaylistName)
    generationOptions = 0
    while (generationOptions != 1) and (generationOptions != 2):
        print("Press 1 to generate a playlist based on Spotify's Recommendation System")
        print("Press 2 to generate a playlist based on your music's attributes")
        generationOptions = int(input("Input: "))
        if (generationOptions != 1) and (generationOptions != 2):
            print("Invalid Input")
    if (generationOptions == 1):
        print("Generating Playlist...")
        sc.populateNewPlaylist_SBR()
        print("Generation Complete")
    elif (generationOptions == 2):
        print("Generating Playlist...")
        sc.populateNewPlaylist_ABR()
        print("Generation Complete")
        pass

    #except:
     #   print("Invalid or expired token")


    #for i in response_json['items']:
    #    print(i['id'])




if __name__ == "__main__":
    main()
