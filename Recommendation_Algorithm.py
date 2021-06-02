import json
import requests
import time
from SpotifyClient import SpotifyClient
from tqdm import tqdm
client_secret = "BQBDAALoN7iccCT04fXKI9mvvWstieofFf6nPGEd6V7_2VMtAGjp-Yhf7JPd1NwUvT1C4JN04LB9L6gI1OXcBJiog3x1V3xGPdXUFxv_IfM5D31EZfaIKquGLOCBSwXQ27G0WPdsRFq8IKe7JvDLisOmbr_HcyVwFlKlIEbpepvOr89-LHoIql6OmMYeF-ieVEng37F-_cMYKEwbP2E2Jj2oBSfzKKTCaye3XYC8PGEnzirxZA"

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
