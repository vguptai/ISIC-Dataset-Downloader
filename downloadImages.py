# This script downloads the images and stores them in proper hierarchy
# Prerequisite - Please run the "downloadImageMetaData.py" script before this from the same directory.
from isicDatasetDownloader import *

initializeRequestSession()
downloadImages()