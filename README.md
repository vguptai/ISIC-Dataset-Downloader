# ISIC-Dataset-Downloader

This python script can be used to download the ISIC dataset using the Girder Rest-API - https://isic-archive.com/api/v1

Step 1) Get all the dataset ids and the image ids and then fetch the metadata of the images (mainly the class) to which the image belongs. The image ids and classes are pickled for the next step.

python downloadImageMetaData.py

Step 2) Download and save the images. Reads the pickled files from the above step to get the imageIds and class information and downloads images. In case the script fails, it can be run again. The already downloaded images will remain intact and not downloaded again.

python downloadImages.py
