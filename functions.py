#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on April 1 11:01:46 2020
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
from skimage.draw import polygon
import cv2

def normalize(img):
    '''
    Normalizes the image range between 0 and 1

    Parameters
    ----------
    img : array_like
        The input image.

    Returns
    -------
    img : array_like
        The normalized output image.

    '''

    img = img-img.min()+0.000001
    img = img*1./img.max()
    return img

def draw_mask(shape, x):
    '''
    Draw a mask where the inside of a polygon is foreground.

    Parameters
    ----------
    shape : array like
        The shape of the output mask
    x : array like
        A list of points that are the corner points of the polygon.

    Returns
    -------
    mask : numpy matrix
        A binary mask that masks out anything outside the polygon.

    '''
    mask = np.zeros(shape, dtype=np.uint8)
    rr, cc = polygon(np.array(x[:, 0]), np.array(x[:, 1]))
    mask[rr, cc] = 255

    return mask

def edgeoff2(img):
    '''
    Buffer the edges of an image.

    Parameters
    ----------
    img : array like
        The input image.

    Returns
    -------
    img : array like
        The buffered image.

    '''
    img[:, 0] = 1
    img[:, -1] = 1
    img[0, :] = 1
    img[-1, :] = 1
    mask = np.zeros((img.shape[0]+2, img.shape[1]+2))
    mask[1:-1, 1:-1] = np.where(img, 0, 2)
    rect = cv2.floodFill(img, mask.astype(np.uint8), (0, 0), 0)

    return img

def equalize(img, n):
    '''
    Equalize the intensity histogram of an image

    Parameters
    ----------
    img : array_like
        Original image that is to have its histogram equalized.
    n : float
        The percentlies that should be considered min and max (1-n) between
        which the histogram should be equalized.

    Returns
    -------
    TYPE : array_like
        Input image with equalized intensity histogram.

    '''
    t1 = np.percentile(img, n)
    t2 = np.percentile(img, 100-n)
    img = np.where(img < t1, t1, img)
    img = np.where(img > t2, t2, img)

    return normalize(img)

################################# Segmentation functions ####################################

def segmentDroplets(img, beadMin=100, beadMax=2000, dropMin=15000, dropMax=300000):
    '''
    Finds and segments microfluidic droplets from brightfield microscopy images.

    Parameters
    ----------
    img : array_like
        An image conataining one or more microfluidic droplets.
    beadMin : float, optional
        The minimum area, in pixels for an object to possibly be a bead.
        The default is 100.
    beadMax : float, optional
         The maximum area, in pixels for an object to possibly be a bead.
         The default is 2000.
    dropMin : TYPE, optional
         The minimum area, in pixels for an object to possibly be a droplet.
         The default is 15000.
    dropMax : TYPE, optional
        The maximum area, in pixels for an object to possibly be a droplet.
        The default is 300000.

    Returns
    -------
    thresh : integer
        Threshold for the the lapacian image.
    droplets_outer : array_like
        The outer boundary of the droplet.
    droplets_inner : array_like
        The inner boundary of the droplet.
    beads : array_like
        Boundaries of the beads.

    '''
    blur = cv2.GaussianBlur(img, (5, 5), 2)
    lapl = cv2.Laplacian(blur, cv2.CV_64F)
    m = abs(lapl.min())
    lapl = (lapl+m).astype(np.uint8)
    m = (255*m)/(lapl.max())
    cv2.normalize(lapl, lapl, 0, 255, cv2.NORM_MINMAX)

    lapl = cv2.GaussianBlur(lapl, (3, 3), 1)
    ret, thresh = cv2.threshold(lapl, m+4, 1, 0)

    contours, hierarchy = cv2.findContours(thresh.copy(),
                                           cv2.RETR_CCOMP,
                                           cv2.CHAIN_APPROX_SIMPLE)

    for i, cnt in enumerate(contours):
        if cv2.contourArea(cnt) < beadMin:
            cv2.drawContours(thresh, [cnt], -1, 0, -1)

    thresh = cv2.morphologyEx(thresh,
                              cv2.MORPH_CLOSE,
                              cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                                        (3, 3)))

    contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    droplets_outer = np.zeros_like(thresh)
    droplets_inner = np.zeros_like(thresh)
    beads = np.zeros_like(thresh)

    ### Beads and Droplets ###
    # find beads according to their size and Position inside another contour
    # find droplet contours according to size and hierarchy
    # if droplet border broken, convex hull helps identifying droplets still
    for i, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        hull = cv2.convexHull(cnt)
        conv = cv2.contourArea(hull)

        ### Beads ###
        if (beadMin < area < beadMax and
                conv < beadMax and
                area < dropMin):
            if hierarchy[0, i, 3] == -1:
                cv2.drawContours(beads, [cnt], -1, 1, -1)
        elif area > dropMin and (4*np.pi*area)/((cv2.arcLength(cnt, True))**2) < 0.5:
            if hierarchy[0, i, 3] == -1:
                cv2.drawContours(beads, [cnt], -1, 1, -1)

        ### Droplets ###
        if dropMax > area >= dropMin:
            if hierarchy[0, i, 3] == -1:
                cv2.drawContours(droplets_outer, [cnt], -1, 1, -1)
            elif hierarchy[0, i, 3] != -1:
                cv2.drawContours(droplets_inner, [cnt], -1, 1, -1)
                cv2.drawContours(droplets_inner, [cnt], -1, 0, 1) # subtract contour
        if dropMax > conv >= dropMin:
            if hierarchy[0, i, 3] == -1:
                cv2.drawContours(droplets_outer, [hull], -1, 1, -1)
                cv2.drawContours(droplets_inner, [hull], -1, 1, -1)
                cv2.drawContours(droplets_inner, [cnt], -1, 0, -1)

    droplets_inner = cv2.morphologyEx(droplets_inner,
                                      cv2.MORPH_OPEN,
                                      cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                                                (3, 3)))

    contours, hierarchy = cv2.findContours(droplets_inner.copy(),
                                           cv2.RETR_CCOMP,
                                           cv2.CHAIN_APPROX_SIMPLE)
    for i, cnt in enumerate(contours):
        if cv2.contourArea(cnt) < dropMin:
            cv2.drawContours(droplets_inner, [cnt], -1, 0, -1)

    if np.sum(droplets_inner) == 0:
        droplets_outer = cv2.morphologyEx(droplets_outer,
                                          cv2.MORPH_CLOSE,
                                          cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                                                    (11, 11)))
        contours, hierarchy = cv2.findContours(droplets_outer,
                                               cv2.RETR_CCOMP,
                                               cv2.CHAIN_APPROX_SIMPLE)
        droplets_outer = np.zeros_like(droplets_outer)
        for i, cnt in enumerate(contours):
            area = cv2.contourArea(cnt)
            if dropMax > area >= dropMin:
                if hierarchy[0, i, 3] == -1:
                    cv2.drawContours(droplets_outer, [cnt], -1, 1, -1)
                elif hierarchy[0, i, 3] != -1:
                    cv2.drawContours(droplets_inner, [cnt], -1, 1, -1)
                    cv2.drawContours(droplets_inner, [cnt], -1, 0, 1) # subtract contour

    if np.sum(droplets_outer) == 0:
        closed_beads = cv2.morphologyEx(beads, cv2.MORPH_CLOSE,
                                        cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                                                  (9, 9)))
        contours, hierarchy = cv2.findContours(closed_beads.copy(),
                                               cv2.RETR_CCOMP, 1)
        for i, cnt in enumerate(contours):
            area = cv2.contourArea(cnt)
            if dropMax > area >= dropMin:
                if hierarchy[0, i, 3] == -1:
                    cv2.drawContours(droplets_outer, [cnt], -1, 1, -1)
                elif hierarchy[0, i, 3] != -1:
                    cv2.drawContours(droplets_inner, [cnt], -1, 1, -1)
                    cv2.drawContours(droplets_inner, [cnt], -1, 0, 1)

    beads = beads*droplets_outer

    return thresh, droplets_outer, droplets_inner, beads

##################################################################

def seperateSingleBeads(beads, seperator):
    '''
    Identify single beads among all bead objects

    Parameters
    ----------
    beads : array_like
        Contours of all bead objects.
    seperator : float
        The upper limit for the size of a single droplet.

    Returns
    -------
    beads : array_like
        Contours of all single beads.
    clumps : array_like
        Contours of all objects that is two or more beads.

    '''
    contours, hierarchy = cv2.findContours(beads.copy(),
                                           cv2.RETR_CCOMP,
                                           cv2.CHAIN_APPROX_SIMPLE)

    clumps = np.zeros_like(beads)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area >= seperator:
            cv2.drawContours(beads, [cnt], -1, 0, -1)
            cv2.drawContours(clumps, [cnt], -1, 1, -1)

    return beads, clumps

#################################################################

def seperateBeadsFromBorder(droplets_inner, beads, beadMin, imgname):
    '''
    Seperate the beads from the border to ensure droplet border integrity

    Parameters
    ----------
    droplets_inner : array_like
        The inner border contour of the droplet.
    beads : array_like
        Contours of the beads in the droplet.
    beadMin : float
        Smallest possible size for a bead.
    imgname : string
        The name of the image that is being processed.

    Returns
    -------
    droplets_inner : array_like
        The inner contour of the droplet after sepearation from beads.
    beads : array_like
        The contours of the beads after adding any beads that was previously
        megred with the droplet border.

    '''
    try:

        hull = np.zeros_like(droplets_inner)
        contours, hierarchy = cv2.findContours(droplets_inner.copy(),
                                               cv2.RETR_EXTERNAL,
                                               cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            hull_points = cv2.convexHull(cnt)
            cv2.drawContours(hull, [hull_points], -1, 1, -1)

        beads2 = hull-droplets_inner
        beads2 = cv2.morphologyEx(beads2,
                                  cv2.MORPH_OPEN,
                                  cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                                            (5, 5)))

        contours, hierarchy = cv2.findContours(beads2,
                                               cv2.RETR_CCOMP,
                                               cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > beadMin:
                cv2.drawContours(beads, [cnt], -1, 1, -1)
        droplets_inner = hull

    except IndexError:

        print('Convex hull could net be created! Image number: %s\n'%imgname)

    return droplets_inner, beads
