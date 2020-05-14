This script is reading images from a driectory and segmenting  microfluidic droplets in the image. It is assumed that the images are brightfield
microscopy images. This sicript is used for the droplet segementation in the publication Svensson et al., (2019) Coding of experimental conditions 
in microfluidic droplet assays using colored beads and machine learning supported image analysis. Small	15(4), e1802384. If this code is used for 
any academic publications, please cite this publication.

----------------------------------------------------------------------------------
Useage
----------------------------------------------------------------------------------
The script is used by running
>python droplet_segmentation.py /input_directory /output_directory
in a terminal. If you for example want to run the test data images and save them in a folder called Results in the same directory as the code, you
run:
> python .\droplet_segmentation.py ./test_data/ ./Results/

Since version 0.2 of this code it is also possible to pass a JSON file with data locations and parameters. The format of the usage it then:
> python .\droplet_segmentation.py parameter_file.json
The JSON-file is required to containg the following two parameters:
'inputfolder' : Directory where the images to be segmented are placed.
'outputfolder' : Directory where the results should be saved.

The following parameters are optional:
'dropMin' : The minimum size of a droplet in pixels. Default value is 5000 pixels.
'dropMax' : The maximum size of a droplet in pixels. Default value is 300000 pixels.
'cutTop' : The number of pixels that are cut from the top of the image to avoid segemntation of non-relevant structures. Default value is 40 pixels.
'cutBottom' : The number of pixels that are cut from the bottom of the image to avoid segemntation of non-relevant structures. Default value is -60 pixels.
'bg subtraction' : Boolean value that indicates if background subtraction is used before droplet segmentation. Default value is True.
'n bg' : Number of images that are used to calculate the background image. Default value is 5.
'offset' : Threshold offset when creating the binary image after edge detection. This is included to avoid to many minor edges to be included. Default value is 4.
'save masks' : Boolean deciding if the masks will be saved as part of the run. False by default.
'save images' : Boolean deciding if the images with the segmentation outline should be saved. Very useful for for debuging, True by default.
'save every x image' : Determines that every xth image with segmentation should be saved. Higher numbers speed up the run and saves disk space. Default value is 10.

For the parameters that are missing from the JSON file the default values will be automatically used and a message will be shown.

----------------------------------------------------------------------------------
Requirements
----------------------------------------------------------------------------------
The code is tested with the following Python configuration:
Python 3.7.3
numpy 1.18.1 
OpenCV 4.2.0
scikit-image 0.16.2
json 2.0.9