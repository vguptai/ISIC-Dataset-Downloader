import pickle

from networkUtil import *
from diskUtil import *
from config import *

#map containing the image id and the class
imageIdClassMap = {}
#map containing the dataset and the list of image ids in it
datasetImageIdMap = {}

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
    dataSetImageIdMapFileHandle = open(datasetImageIdMapPkl, 'wb')
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

def fetchImagesMetadata():
    initializeDataSetImageIdMap()
    allImageIds = []
    for dataSetId,imageIds in datasetImageIdMap.iteritems():
        allImageIds.extend(imageIds)
    fetchAndPickleClassesForImage(allImageIds)

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
    try:
        imageClass = getImageClass(imageId)
        createDirectory(dataSetId+"/"+imageClass)
        destinationPath = getImageDestinationPath(dataSetId,imageClass,imageId)
        imageDownloadUrl = imageDownloadBaseUrl + imageId + "/download"
        imageContent = getImageContent(imageDownloadUrl)
        if(imageContent is None):
            print "Download of Image:"+imageId+" failed..."
            return False
        else:
            saveImage(imageContent,destinationPath)
        print "Downloaded Image:"+imageId
        return True
    except Exception as e:
        print "Download of Image:"+imageId+" failed..."+str(e)
        return False

def initializeDataSetImageIdMap():
    global datasetImageIdMap
    if(len(datasetImageIdMap)==0):
        dataSetImageIdMapFileHandle = open(datasetImageIdMapPkl, 'rb')
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
        #if(dataSetId!="5627eefe9fc3c132be08d84c"):
        #    continue
        print "Downloading Images for Dataset:"+dataSetId
        totalImagesInDataSet = len(imageIds)
        imagesDownloadedSuccessFully = 0
        createDirectory(dataSetId)
        failedDownloads = open(dataSetId+"/"+dataSetId+"_failed.txt", 'w')
        failedDownloads.truncate()
        imageIndxProcessed = 0
        for imageId in imageIds:
            imageIndxProcessed = imageIndxProcessed + 1
            if(downloadImage(dataSetId,imageId)):
                imagesDownloadedSuccessFully = imagesDownloadedSuccessFully +1
            else:
                failedDownloads.write(imageId)
                failedDownloads.write("\n")
            print "Processing Image:"+str(imageIndxProcessed)+"/"+str(totalImagesInDataSet)
        failedDownloads.write(str(imagesDownloadedSuccessFully)+" images downloaded out of "+str(totalImagesInDataSet) +" for the dataset "+str(dataSetId))
        failedDownloads.close()
        print str(imagesDownloadedSuccessFully)+" images downloaded out of "+str(totalImagesInDataSet) +" for the dataset "+str(dataSetId)
        return
        print "Downloaded the images for the dataset:"+dataSetId
