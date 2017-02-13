import pickle
import os

def createDirectory(dirName):
    if not os.path.exists(dirName):
        os.makedirs(dirName)

def fileExists(filePath):
    return os.path.isfile(filePath)

def saveImage(imageContent,destinationPath):
    f = open(destinationPath, 'wb')
    f.write(imageContent)
    f.close()