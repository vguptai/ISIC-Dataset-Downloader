# This script downloads the image ids for all the datasets of ISCI along with the class for each image.
# The image list and image class mapping are stored in pickled files.
from isicDatasetDownloader import *

initializeRequestSession()
extractImageIdsOfAllDatasets()
fetchImagesMetadata()