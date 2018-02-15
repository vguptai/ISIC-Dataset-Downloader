import requests
import json
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

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
        print(str(e))
        raise e

def postTheUrl(reqUrl,payLoad={}):
    try:
        req = getPostRequest(reqUrl,payLoad)
        return parseRequest(req)
    except Exception as e:
        print(str(e))
        raise e

def parseRequest(req):
    try:
        data = json.loads(req.text)
        return data
    except Exception as e:
        raise e

def getImageContent(imageDownloadUrl):
    return requestSession.get(imageDownloadUrl).content
