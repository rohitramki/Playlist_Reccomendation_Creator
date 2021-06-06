import json
import requests
import time
from SpotifyClient import SpotifyClient

client_id = "pjp1yehfstdvh1uu0ni3m9sak"
client_secret = "BQAipnwjiBFxwNu1cukUBS7RCIxhFbQsmEL5Cd3wrvmf5a_2SsBCr7I4ICxph4RSexAugQXCcpRMPy3pp_4pLcmELNeQt4-1UkMWwHpa5DJeA_QJ8Nsq4MaXknoTHeKAYX4qkFEnPFsyR6UaD8Hizu_lt5bEW5DH72veVk9OSX24hVI67EubQUoVG7Si7x3V2eetpNNMsDUU_XwqjaKp5w5So5gjXTj2QaDMLjumI8gRjmWglg"
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
        sc.populateNewPlaylist_SBR()
        print("'" + sc.getNewUserPlaylist().getName() + "' has successfully been generated!")
    elif (generationOptions == 2):
        sc.populateNewPlaylist_ABR()
        print("'" + sc.getNewUserPlaylist().getName() + "' has successfully been generated!")
        pass

    #except:
     #   print("Invalid or expired token")


    #for i in response_json['items']:
    #    print(i['id'])




if __name__ == "__main__":
    main()
