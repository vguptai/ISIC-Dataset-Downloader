# ISIC Melanoma Project Dataset Downloader

This python script can be used to download the [ISIC Melanoma Project Dataset](https://isic-archive.com/) using the [Girder Rest-API](https://isic-archive.com/api/v1) .

The basic steps that I have followed are:

Step 1) Get all the dataset ids present in the project and get all the image ids for these datasets. 

Fetch the metadata of the images (mainly the class to which the image belongs). The image ids and corresponding classes are pickled for the next step.

The following command does this.

```python
python downloadImageMetaData.py
```

Step 2) In this atep we download the images of the datasets. The cript reads the pickled files from the above step to get the imageIds and their class information to download and save the image in the correct location. In case the script fails, it can be run again. The already downloaded images will remain intact and will not be downloaded again.

```python
python downloadImages.py
```

It does take some time to download close to 12000 images ! So be patient :)
