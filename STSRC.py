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
        otherSongs_sorted = sorted(self.otherSongs.items(), key=lambda x: x[1])
        otherSongs_list = list(otherSongs_sorted)
        return otherSongs_list[:number_Of_Songs]

