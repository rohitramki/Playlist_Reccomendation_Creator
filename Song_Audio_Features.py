class Song_Audio_Features:
    def __init__(self, name=None, mean=0, variance=0, minValue=0, maxValue=0):
        self.name = name
        self.mean = mean
        self.variance = variance
        self.minValue = minValue
        self.maxValue = maxValue

    def getName(self):
        return self.name

    def getMean(self):
        return self.mean

    def getVariance(self):
        return self.variance

    def getMinValue(self):
        standard_deviation = self.variance ** (1/2)
        self.minValue = self.mean - standard_deviation
        if (self.minValue <= 0):
            self.minValue = 0.01
        return self.minValue

    def getMaxValue(self):
        standard_deviation = self.variance ** (1 / 2)
        self.maxValue = self.getMean() + standard_deviation
        if (self.maxValue >= 1):
            self.maxValue = 0.99
        return self.maxValue

    def setName(self, name):
        self.name = name

    def setMean(self, mean):
        self.mean = mean

    def setVariance(self, variance):
        self.variance = variance

    def clearValues(self):
        self.mean = 0
        self.maxValue = 0
        self.minValue = 0
        self.variance = 0

    def clearName(self):
        self.name = ""