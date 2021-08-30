# Song to Song Relationship Container
class STSRC:
    # STSRC instantiation
    def __init__(self, song):
        # Song you are comparing other songs to
        self.song = song
        # List of songs to compare to
        self.otherSongs = {}

    # returns a Song object
    def getSong(self):
        return self.song

    # Adds a Song ID to the otherSongs list
    def addSong(self, songID, number):
        self.otherSongs[songID] = number

    # Updates a songs number
    def updateNumber(self, songID, relationshipNumber):
        self.otherSongs[songID] += relationshipNumber

    # returns the closest songs to the the given song. The amount of songs returned is based on the number_Of_Songs
    # variable
    def produceLowestValues(self, number_Of_Songs):
        otherSongs_sorted = sorted(self.otherSongs.items(), key=lambda x: x[1])
        otherSongs_list = []
        for i in otherSongs_sorted:
            otherSongs_list.append(i[0])
        return otherSongs_list[:number_Of_Songs]

