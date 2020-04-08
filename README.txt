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

----------------------------------------------------------------------------------
Requirements
----------------------------------------------------------------------------------
The code is tested with the following Python configuration:
Python 3.7.3
numpy 1.18.1 
OpenCV 4.2.0
scikit-image 0.16.2