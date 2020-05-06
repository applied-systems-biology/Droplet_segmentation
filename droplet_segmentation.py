#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on April 24 2016
@authors: C-M Svensson and Stefanie Dietrich
@email: carl-magnus.svensson@leibniz-hki.de or cmgsvensson@gmail.com

Copyright by Dr. Carl-Magnus Svensson and Stefanie Dietrich

Research Group Applied Systems Biology - Head: Prof. Dr. Marc Thilo Figge
https://www.leibniz-hki.de/en/applied-systems-biology.html
HKI-Center for Systems Biology of Infection
Leibniz Institute for Natural Product Research and Infection Biology -
Hans Knöll Insitute (HKI)
Adolf-Reichwein-Straße 23, 07745 Jena, Germany

License: BSD-3-Clause, see ./LICENSE or
https://opensource.org/licenses/BSD-3-Clause for full details
"""
import numpy as np
import cv2
from fileprocess import process_input, list_image_files
from functions import segmentDroplets, seperateBeadsFromBorder
from functions import seperateSingleBeads, edgeoff2
from droplets_class import Droplet

__version__ = '0.2'
###############################################################################################

def main():
    '''
    This script is reading images from a driectory and segmenting  microfluidic 
    droplets in the image. It is assumed that the images are brightfield
    microscopy images. This sicript is used for the droplet segementation in 
    the publication Svensson et al., (2019) Coding of experimental conditions 
    in microfluidic droplet assays using colored beads and machine learning 
    supported image analysis. Small	15(4), e1802384. If this code is used for 
    any academic publications, please cite this publication.

    Returns
    -------
    None.

    '''
    parameters = process_input()
    inputfolder = parameters['inputfolder']
    outputfolder = parameters['outputfolder']

    if inputfolder:
        print(str(inputfolder).replace('\\','/'))
        foldername = str.split(str(inputfolder).replace('\\','/'), '/')[-2]
        inputfiles = list_image_files(inputfolder)

        outfile = outputfolder/(foldername+'.csv')
        print(inputfiles[10])

        with open(outfile, 'w') as f:
            string = 'Img_num;Droplet_number;R_mean;R_med;R_std;R_max;R_min;Area;Major_axis;Minor_axis;center_x;center_y;time;Beads\n'
            f.write(string)


        ############################### Parameters #############################################

        # area of bead clusters with [1,2,3,4] beads. Learned from data using k-means clustering
        # as long, as the resolution doesn't change, this should hold true
        clumpsizes = np.array([238, 456, 660, 1000])

        # values for image cropping
        try:
            use_bg_subtraction = parameters['bg subtraction']
        except:
            print('Background subtraction is by default on')
            use_bg_subtraction = True
        try:
            cutTop = parameters['cutTop']
        except:
            print('The cut at the top of the image is set to the standard of 40 pixels')
            cutTop = 40
        try:
            cutBottom = parameters['cutbottom']
        except:
            print('The cut at the bottom of the image is set to the standard of 60 pixels')
            cutBottom = -60

        # values for accepted droplet and bead sizes (areas)
        # seperator = value for seperation of single beads and clusters
        try:
            dropMin = parameters['dropMin']
        except:
            print('Droplet minimal size is set to the default of 5000 pixels')
            dropMin = 5000
        try:
            dropMax = parameters['dropMax']
        except:
            print('Droplet maximal size is set to the default of 300000 pixels')
            dropMax = 300000
        try:
            offset = parameters['offset']
        except:
            print('Offset of the Laplacian image thresholding set to the default of 4')
            offset = 4
        beadMin = 140
        beadMax = 20000
        seperator = 300

        # should result images with drawn contours be saved
        # if so, every saveImagesNumber-th image will be saved
        saveImages = True
        saveImagesNumber = 1

        ############## Generate averaged background image for BG subtraction #################

        bg_rgb = cv2.imread(str(inputfiles[10]), 0)
        bg = np.zeros_like(bg_rgb)
        bg = bg.astype(np.uint64)
#
        try:
            n = parameters['n bg']
        except:
            print('Number of images for background substraction is set to the default number 5')    
            n = 5 # number of images for avgeraging
            
        if n > len(inputfiles):
            n = len(inputfiles)
#
        bg_stack = np.zeros((bg_rgb.shape[0], bg_rgb.shape[1], n))
        if use_bg_subtraction:
            im = 0
            while im < n:
                img_rgb = cv2.imread(str(inputfiles[im]))
                img = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
                try:
                    bg_stack[:, :, im] = img[:]
                    im += 1
                except StopIteration:
                    pass
            bg = np.median(bg_stack, axis=2)
            bg = bg[cutTop:cutBottom]
            bg = bg.astype(np.uint8)
            bg = 255 - bg


        ####################### Loop for single image segmentation ###########################
        img_rgb = cv2.imread(str(inputfiles[0]))
        img_rgb = img_rgb[cutTop:cutBottom, :, :]
        img1 = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

        img = img1.astype(np.uint16)
        if use_bg_subtraction:
            img = img + bg
        cv2.normalize(img, img, 0, 255, cv2.NORM_MINMAX)
        img = img.astype(np.uint8)

        for im in range(len(inputfiles)):
            ### Read image and subtract BG ###
            img_rgb = cv2.imread(str(inputfiles[im]))
            img_rgb = img_rgb[cutTop:cutBottom, :, :]
            img1 = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

            imgname = str.split(str.split(str(inputfiles[im]).replace('\\', '/'), '/')[-1], '.')[0]

            img = img1.astype(np.uint16)
            img2 = img[:]
            if use_bg_subtraction:
                img2 = img2 + bg
            cv2.normalize(img, img, 0, 255, cv2.NORM_MINMAX)
            img = img.astype(np.uint8)
            cv2.normalize(img2, img2, 0, 255, cv2.NORM_MINMAX)
            img2 = img2.astype(np.uint8)

            ### Segment droplets and bead clusters ###

            # thresh is the thresholded image after Laplacian of Gaussian
            # drop outer contains outer borders of droplets
            # drop_inner contains inner borders
            # beads contains beads inside droplets
            thresh, drop_outer, drop_inner, beads = segmentDroplets(img, beadMin,
                                                                    beadMax, dropMin,
                                                                    dropMax, offset)
            drop_inner, beads = seperateBeadsFromBorder(drop_inner, beads,
                                                        beadMin, imgname)

            contours, hierarchy = cv2.findContours(drop_inner.copy(),
                                                   cv2.RETR_CCOMP,
                                                   cv2.CHAIN_APPROX_SIMPLE)

            beads, clumps = seperateSingleBeads(beads, seperator)

            contours, hierarchy = cv2.findContours(clumps.copy(),
                                                   cv2.RETR_EXTERNAL,
                                                   cv2.CHAIN_APPROX_SIMPLE)
            for i, cnt in enumerate(contours):
                area = cv2.contourArea(cnt)
                if area > clumpsizes[0]:
                    cv2.drawContours(clumps, [cnt], -1, 1, -1)

            edgeoff2(drop_outer)

            contours, hierarchy = cv2.findContours(drop_outer.copy(),
                                                   cv2.RETR_CCOMP,
                                                   cv2.CHAIN_APPROX_SIMPLE)
            
            drop_array = []
            for i, cnt in enumerate(contours):
                if (cv2.contourArea(cnt) > dropMin and
                        (4*np.pi*cv2.contourArea(cnt))/((cv2.arcLength(cnt, True))**2) > 0.5):
                    drop = Droplet(imgname, cnt, cutTop)
                    if drop.checkDropletPosition(img.shape):
                        droptemp = np.zeros_like(img)
                        cv2.drawContours(droptemp, [cnt], -1, 1, -1)

                        drop_array.append(drop)
            ##################################### Output ##################################

            drawing = img_rgb.copy()
            i = 0

            for drop in drop_array:
                cv2.drawContours(drawing, [drop.contour], -1, (0, 0, 255), 1)
                i += 1


            if saveImages:
                if im%saveImagesNumber == 0:
                    cv2.imwrite(str(outputfolder/(imgname+'_contour.png')), drawing)

            if im%50 == 0:
                print("Image: ", im)


##############################################################################################
if __name__ == '__main__':
    main()
