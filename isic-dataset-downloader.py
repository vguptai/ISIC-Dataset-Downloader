import requests
import json
import pickle
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import os

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

# URLS
dataSetUrl = "https://isic-archive.com:443/api/v1/dataset?limit=0&offset=0&sort=name&sortdir=1"
imageSetBaseUrl = "https://isic-archive.com:443/api/v1/image?limit=0&offset=0&sort=name&sortdir=1"
imageDownloadBaseUrl = "https://isic-archive.com:443/api/v1/image/"
imageDetailsDownloadBaseUrl = "https://isic-archive.com:443/api/v1/image/"

imageIdClassMapPkl = "imageIdClassMap.pkl"

#map containing the image id and the class
imageIdClassMap = {}
#map containing the dataset and the list of image ids in it
datasetImageIdMap = {}

requestSession = None

def initializeRequestSession():
    global requestSession
    requestSession = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[500, 502, 503, 504])
    requestSession.mount('http://', HTTPAdapter(max_retries=retries))
    requestSession.mount('https://', HTTPAdapter(max_retries=retries))

def getPostRequest(reqUrl,payLoad={}):
    return requestSession.post(reqUrl, data=payLoad)

def getGetRequest(reqUrl,payLoad={}):
    return requestSession.get(reqUrl, data=payLoad)

def getTheUrl(reqUrl,payLoad={}):
    try:
        req = getGetRequest(reqUrl,payLoad)
        return parseRequest(req)
    except Exception as e:
        print str(e)
        raise e

def postTheUrl(reqUrl,payLoad={}):
    try:
        req = getPostRequest(reqUrl,payLoad)
        return parseRequest(req)
    except Exception as e:
        print str(e)
        raise e

def parseRequest(req):
    try:
        data = json.loads(req.text)
        return data
    except Exception as e:
        raise e

def extractImageIdsFromUrl(imageSetUrl):
    imageIds = []
    imageListJson = getTheUrl(imageSetUrl)
    for imageJson in imageListJson:
        imageIds.append(imageJson["_id"])
    return imageIds

def extractDatasetList():
    dataSetIds = []
    dataSetListJson = getTheUrl(dataSetUrl)
    for dataSetJson in dataSetListJson:
        dataSetIds.append(dataSetJson["_id"])
    return dataSetIds

def extractImageIdsOfAllDatasets():
    print "Extracting DataSet List..."
    dataSetIds = extractDatasetList()
    print "DataSet Ids..."+str(dataSetIds)
    datasetImageMap = {}
    for dataSetId in dataSetIds:
        imageSetFullUrl = imageSetBaseUrl+"&datasetId="+dataSetId
        datasetImageMap[dataSetId] = extractImageIdsFromUrl(imageSetFullUrl)
    for dataSetId,imageIds in datasetImageMap.iteritems():
        print "DataSet Id:Number of Images "+str(dataSetId)+":"+str(len(imageIds))
    print "Pickling the dataset image map..."
    # Output Files
    dataSetImageIdMapFileHandle = open("dataSetImageIdMap.pkl", 'wb')
    dataSetImageIdMapFileHandle.truncate()
    pickle.dump(datasetImageMap, dataSetImageIdMapFileHandle)
    print "Pickling Done..."
    dataSetImageIdMapFileHandle.close()
    return datasetImageMap

def getImageClass(imageId):

    if(imageIdClassMap.has_key(imageId)):
        return imageIdClassMap.get(imageId)

    imageDetailsDownloadUrl = imageDetailsDownloadBaseUrl+imageId
    try:
        imageDetails = getTheUrl(imageDetailsDownloadUrl)
        imageClass = imageDetails["meta"]["clinical"]["benign_malignant"]
        if(imageClass is None):
            return "_Null_Class_"
        else:
            return imageClass
    except Exception as e:
        print "ERROR: while extracting the class for an image"+str(e)
        return "_Fetch_Error_"

#def checkIfImageAlreadyDownloaded(imageId):

def fetchAndPickleClassesForImage(imageIds):
    print "Fetching Classes For ImageIds..."
    classFetchesLogFile = open("classes_fetching_logs.txt", 'w')
    classFetchesLogFile.truncate()
    count = 0
    totalCount = len(imageIds)
    for imageId in imageIds:
        count = count + 1
        print str(count)+"/"+str(totalCount)
        imageClass = getImageClass(imageId)
        imageIdClassMap[imageId] = imageClass
        classFetchesLogFile.write("Fetched Class:"+imageClass+" for ImageId:"+imageId)
        classFetchesLogFile.write("\n")
    classFetchesLogFile.close()
    print "Pickling Classes For ImageIds..."
    imageIdClassMapFileHandle = open(imageIdClassMapPkl, 'wb')
    imageIdClassMapFileHandle.truncate()
    pickle.dump(imageIdClassMap, imageIdClassMapFileHandle)
    print "Pickled Classes  For ImageIds..."

def findClassesOfTheImages():
    initializeDataSetImageIdMap()
    allImageIds = []
    for dataSetId,imageIds in datasetImageIdMap.iteritems():
        allImageIds.extend(imageIds)
    fetchAndPickleClassesForImage(allImageIds)

def createDirectory(dirName):
    if not os.path.exists(dirName):
        os.makedirs(dirName)

def fileExists(filePath):
    return os.path.isfile(filePath)

def getImageDestinationPath(dataSetId,imageClass,imageId):
    return dataSetId+"/"+imageClass+"/" + imageId + ".jpg"

def imageAlreadyDownloaded(dataSetId,imageId):
    imageClass = getImageClass(imageId)
    destinationPath = getImageDestinationPath(dataSetId,imageClass, imageId)
    if (fileExists(destinationPath)):
        print "Image already present, so not downloading it again:" + imageId
        return True
    return False

def downloadImage(dataSetId,imageId):

    if(imageAlreadyDownloaded(dataSetId,imageId)):
        return True

    print "Downloading Image:"+imageId
    imageDownloadUrl = imageDownloadBaseUrl+imageId+"/download"

    try:
        imageClass = getImageClass(imageId)
        createDirectory(dataSetId+"/"+imageClass)
        destinationPath = getImageDestinationPath(dataSetId,imageClass,imageId)
        f = open(destinationPath, 'wb')
        imageContent = requestSession.get(imageDownloadUrl).content
        if(imageContent is None):
            print "Download of Image:"+imageId+" failed..."
            return False
        f.write(imageContent)
        f.close()
        print "Downloaded Image:"+imageId
        return True
    except Exception as e:
        print "Download of Image:"+imageId+" failed..."
        return False

def initializeDataSetImageIdMap():
    global datasetImageIdMap
    if(len(datasetImageIdMap)==0):
        dataSetImageIdMapFileHandle = open("dataSetImageIdMap.pkl", 'rb')
        datasetImageIdMap = pickle.load(dataSetImageIdMapFileHandle)

def initializeImageIdClassMap():
    global imageIdClassMap
    if(len(imageIdClassMap)==0):
        imageIdClassMapFileHandle = open(imageIdClassMapPkl,'rb')
        imageIdClassMap = pickle.load(imageIdClassMapFileHandle)

def downloadImages():

    initializeDataSetImageIdMap()
    initializeImageIdClassMap()

    for dataSetId,imageIds in datasetImageIdMap.iteritems():
        if(dataSetId!="54ea816fbae47871b5e00c80"):
            continue
        print "Downloading Images for Dataset:"+dataSetId
        totalImagesInDataSet = len(imageIds)
        imagesDownloadedSuccessFully = 0
        failedDownloads = open(dataSetId+"_failed.txt", 'w')
        for imageId in imageIds:
            if(downloadImage(dataSetId,imageId)):
                imagesDownloadedSuccessFully = imagesDownloadedSuccessFully +1
            else:
                failedDownloads.write(imageId)
                failedDownloads.write("\n")
        failedDownloads.close()
        print str(imagesDownloadedSuccessFully)+" images downloaded out of "+str(totalImagesInDataSet) +" for the dataset "+str(dataSetId)
        return
        print "Downloaded the images for the dataset:"+dataSetId

initializeRequestSession()
#extractImageIdsOfAllDatasets()
#findClassesOfTheImages()
downloadImages()
