#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on November 23 2015
@authors: Stefanie Dietrich
@email: thilo.figge@leibniz-hki.de

Copyright by Stefanie Dietrich

Research Group Applied Systems Biology - Head: Prof. Dr. Marc Thilo Figge
https://www.leibniz-hki.de/en/applied-systems-biology.html
HKI-Center for Systems Biology of Infection
Leibniz Institute for Natural Product Research and Infection Biology -
Hans Knöll Insitute (HKI)
Adolf-Reichwein-Straße 23, 07745 Jena, Germany

License: BSD-3-Clause, see ./LICENSE or
https://opensource.org/licenses/BSD-3-Clause for full details
'''
import numpy as np
import cv2

class Droplet():
    '''
        The class Droplet collects all important characteristics of a microfluidic
        droplet.
    '''

    def __init__(self, imagenumber, cnt, cutTop):
        '''
        Initiate the class

        Parameters
        ----------
        imagenumber : integer
            The number of the image containing the droplet
        cnt : OpenCV vector
            The outer contour of the droplet
        cutTop : integer
            The number of pixels to be cut from the top and bottom to avoid
            channel edges to be disturbing analysis.

        Returns
        -------
        None.

        '''

        self.imageNumber = imagenumber
        self.contour = cnt

        mom = cv2.moments(cnt)
        self.positionX = np.around(mom['m10']/mom['m00']).astype(np.uint16)
        self.positionY = np.around(mom['m01']/mom['m00']).astype(np.uint16)+cutTop

        self.area = cv2.contourArea(cnt)

        radii = np.zeros(len(cnt))
        for j in range(len(cnt)):
            radii[j] = np.sqrt((self.positionX-cnt[j][0][0])**2 + ((self.positionY-cutTop)-cnt[j][0][1])**2)
        self.rMean = np.mean(radii)
        self.rMed = np.median(radii)
        self.rStd = np.std(radii)
        self.rMin = radii.min()
        self.rMax = radii.max()

        axis = cv2.fitEllipse(cnt)[1]
        self.majorAxis = maj_axis = max(axis)
        self.minorAxis = min_axis = min(axis)

        self.beads = []
        self.quality = []

    def roundness(self):
        '''
        Calculation of the droplet roundness, also known as circularity.

        Returns
        -------
        rdns : float
            The roundness of the droplet in the range of 0 to 1, where 1 is a
            perfect circle.

        '''
        rdns = (4*self.area)/(np.pi*(self.majorAxis**2))
        return rdns

    def isoperimetricQuotient(self):
        '''
        Calculation of the isoperimetric quotient of the droplet
        (https://mathworld.wolfram.com/IsoperimetricQuotient.html)

        Returns
        -------
        ispmc : float
            The isoperimetric quotient in the range 0 to 1.

        '''
        perimeter = cv2.arcLength(self.contour, True)
        ispmc = (4*np.pi*self.area)/((perimeter)**2)
        return ispmc


    def eccentricity(self):
        '''
        Calculation of the eccentricity of the droplet.

        Returns
        -------
        ecty : float
            Eccentricity of the droplet in the range 1 to infinity, where 1 is
            a perfect circle and increases means that the droplet is more
            oval.

        '''
        ecty = self.minorAxis/self.majorAxis
        return ecty

    def volume(self, h, w, px):
        '''
        Volume calculation of the droplet.

        Parameters
        ----------
        h : float
            Height of the microfluidic channel in micrometers.
        w : float
            Width of the microfluidic channel in micrometers.
        px : float
            Resolution of the image in micrometer per pixel.

        Returns
        -------
        v : float
            The volume of the droplet in picoliter.

        '''
        R = self.rMed*px
        r = h/2.
        if 2*R > h:                                 # volume using pancake
            v = (2*np.pi*r*(R-r)**2 + (np.pi**2)*(r**2)*((4*r)/(3*np.pi) + R - r))
        else:
            v = 4/3*np.pi*R**3                      # volume using sphere
        v = v/1000.                                 # umrechnung von microns^3 in pl
        return v

    def addBead(self, beadX, beadY, cutTop, qual):
        '''
        Adding a bead to the droplet.

        Parameters
        ----------
        beadX : float
            Postion of the bead in the image in the horizontal direction.
        beadY : float
            Postion of the bead in the image in the vertical direction.
        cutTop : integer
            Number of pixels that are cut from the top of the image.
        qual : string
            Certain quality of the bead to be stored, color fo example.

        Returns
        -------
        None.

        '''
        self.beads.append([beadX, beadY+cutTop])
        self.quality.append(qual)

    def checkDropletPosition(self, shape):
        '''
        Check that the entire droplet is in the image

        Parameters
        ----------
        shape : tuple
            Shape of the image in (height, width).

        Returns
        -------
        bool
            Returns True if the entire droplet is in the image, False otherwise.

        '''

        if self.positionX-self.rMed < 0 or self.positionX+self.rMed > shape[1]:
            return False

        return True
