# -*- coding: utf-8 -*-
"""
Python module to create images to train darknet neural network
Run this inside a folder containig a folder named obj with the classes
and a folder called bkg with the background images.
The classes images must be named as their respective classes, from 1 to N.
​"""

from __future__ import print_function, division

import os
import cv2
import random
import numpy as np


obj_list = []
bkg_list = []


def get_images(folder_name):
    """
    Returns list containing valid image names of the images inside folder_name.
    """

    image_extensions = [".jpg", ".png", ".gif"]

    return [f for f in os.listdir(folder_name) if f[-4:] in image_extensions]


def get_images_names():
    """
    Gets the names of the images inside the obj and bkg folders.
    """
    global obj_list, bkg_list
    obj_list = get_images('obj/')
    bkg_list = get_images('bkg/')


def join_images(img_obj, img_bkg):
    """
    Places the object image on the background images. 
    """

    # ensure the object is fully visible
    y_percentage = img_obj.shape[0] / img_bkg.shape[0]
    x_pencentage = img_obj.shape[1] / img_bkg.shape[1]

    # choose a random position on screen
    y_offset = int(random.uniform(0, 1 - y_percentage) * img_bkg.shape[0])
    x_offset = int(random.uniform(0, 1 - x_pencentage) * img_bkg.shape[1])

    if (x_offset + img_obj.shape[1]) > img_bkg.shape[1]:
        x_offset -= (x_offset + img_obj.shape[1]) - img_bkg.shape[1]
    
    if (y_offset + img_obj.shape[0]) > img_bkg.shape[0]:
        y_offset -= (y_offset + img_obj.shape[0]) - img_bkg.shape[0]

    # copy img_bkg to img_join to maked the changes
    img_join = img_bkg.copy()


    img_join[y_offset:y_offset+img_obj.shape[0], x_offset:x_offset+img_obj.shape[1]] = img_obj

    x = ((2 * x_offset + img_obj.shape[1]) / 2) / img_bkg.shape[1]
    y = ((2 * y_offset + img_obj.shape[0]) / 2) / img_bkg.shape[0]
    w = img_obj.shape[1] / img_bkg.shape[1]
    h = img_obj.shape[0] / img_bkg.shape[0]

    coords = (x,y,w,h)

    return img_join, coords


def blur_random(img):
    """
    Blurs the image to a random percentage.
    """

    blur_level = (int(random.uniform(10, 40)),) * 2
    return cv2.blur(img, blur_level)


def resize_random(img):
    """
    resizes the img to a random size.
    """

    if random.random() > 0.3: # downscale
        width = int(img.shape[1] * random.uniform(0.4,0.7))
        height = int(img.shape[0] * random.uniform(0.4,0.7))
    else: # upscale
        width = int(img.shape[1] * random.uniform(1,1.2))
        height = int(img.shape[0] * random.uniform(1,1.2))

    resized = cv2.resize(img, (width, height))

    return resized


def water_tint(img):
    """
    Adds a tint to the image trying to emulate a underwater effect.
    """

    blue = int(random.uniform(128,255))
    green = int(random.uniform(0,128))
    
    img_tinted = img.copy()

    for i,c in enumerate([blue, green]):
        img_tinted[...,i] = cv2.add(img[...,i], c)

    return img_tinted


def random_darken(img):
    """
    Darkens the image by a random amount.
    """
    invGamma = 1.0 / random.uniform(0.3, 0.7)
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")

    return cv2.LUT(img, table)
    

def modify(obj_count, blur=True, flip=True, resize=True, tint=True, darken=True):
    """
    Modifies images. 
    """

    if type(obj_count) != int:
        assert(len(obj_count) == len(obj_list))
    else:
        obj_count = [obj_count] * (len(obj_list))

    for i,o  in enumerate(obj_list): # loop through objects
        for j in range(obj_count[i]): # create new image
            
            img_obj = cv2.imread("obj/" + o)

            if blur and random.random() >= 0.75:
                img_obj = blur_random(img_obj)
            
            if resize and random.random() >= 0.75:
                img_obj = resize_random(img_obj)

            # mirror image
            if flip and random.random() >= 0.5:
                img_obj = cv2.flip(img_obj, 1)

            # choose a random image from the background images
            img_bkg = cv2.imread("bkg/" + random.choice(bkg_list))
            
            if blur and random.random() >= 0.5:
                img_bkg = blur_random(img_bkg)
            
            # mirror image
            if flip and random.random() >= 0.5:
                img_bkg = cv2.flip(img_bkg, 1)

            img_join, coords = join_images(img_obj, img_bkg)
            
            if tint and random.random() >= 0.75:
                img_join = water_tint(img_join)

            if darken and random.random() >= 0.75:
                img_join = random_darken(img_join)
            
            name = 'save/' + str(i) + "_" + str(j)

            # save txt
            with open(name + ".txt", "w+") as outfile:
                outfile.write(str(i) + " " + str(coords[0]) + " " + str(coords[1]) + " "
                                           + str(coords[2]) + " " + str(coords[3]))

            cv2.imwrite(name + ".jpg", img_join) # save image


if __name__ == "__main__":
    get_images_names()
    modify([5])
