# Song to Song Relationship Container
class STSRC:
    def __init__(self, song):
        self.song = song
        self.otherSongs = {}

    def getSong(self):
        return self.song

    def addSong(self, songID, number):
        self.otherSongs[songID] = number

    def updateNumber(self, songID, relationshipNumber):
        self.otherSongs[songID] += relationshipNumber

    def produceLowestValues(self, number_Of_Songs):
        print("Other song items: ")
        print(self.otherSongs.items())
        print("Other songs keys: ")
        print(self.otherSongs.keys())
        otherSongs_sorted = sorted(self.otherSongs.items(), key=lambda x: x[1])
        otherSongs_list = []
        for i in otherSongs_sorted:
            otherSongs_list.append(i[0])
        print("otherSongs_list songs: ")
        print(otherSongs_list[:number_Of_Songs])
        return otherSongs_list[:number_Of_Songs]

