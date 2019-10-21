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
import argparse


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


def distort_random(img):
    """
    Distorts the image by a random amount
    """
    # I don't know how this code works, it was all made using trial and error 
    # Stack Overflow or anything like it was used
    # If you wish to learn how this code works, check OpenCV's affine transformation tutorial
    # Good luck using it
    rows, cols, ch = img.shape

    y = x = random.random()*50

    pts1 = [[x, y]]
    pts2 = [[x+100,y+100]]

    # The numbers are magic
    # Unexpected results WILL happen if you change them
    # Unexpected results might happen if you don't change them as well
    x,y = rows*random.random(), cols*random.random()/2
    r = random.random()*30
    pts1.append([x, y])
    pts2.append([x+r+50, y+r+50])

    # These points are the ones that work the best from the ones tested
    # I.e. they are better than [rows, col]
    pts1.append([rows/2, cols/2])
    pts2.append([rows/2, cols/2])

    pts1 = np.float32(pts1)
    pts2 = np.float32(pts2)

    M = cv2.getAffineTransform(pts1,pts2)

    return cv2.warpAffine(img, M, (cols, rows))



def blur_random(img):
    """
    Blurs the image to a random percentage.
    """

    blur_level = (int(random.uniform(10, 40)),) * 2
    return cv2.blur(img, blur_level)


def resize_img(img, width=1.5, height=1.5):
    width = int(img.shape[1] * width)
    height = int(img.shape[0] * height)
    
    resized = cv2.resize(img, (width, height))

    return resized


def resize_random(img):
    """
    resizes the img to a random size.
    """

    if random.random() > 0.3: # downscale
        width = random.uniform(0.4,0.7)
        height = random.uniform(0.4,0.7)
    else: # upscale
        width = random.uniform(1,1.2)
        height = random.uniform(1,1.2)

    return resize_img(img, width, height)


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
    

def modify(obj_count, transform=True, blur=True, flip=True, resize=True, tint=True, darken=True):
    """
    Modifies images. 
    """

    if type(obj_count) != int:
        assert len(obj_count) == len(obj_list) + 1, \
            "Given numbers of images to create is diffent than number of classes"
    else:
        obj_count = [obj_count] * (len(obj_list))

    for i,o  in enumerate(obj_list): # loop through objects
        for j in range(obj_count[i]): # create new image
            
            img_obj = cv2.imread("obj/" + o)

            if blur and random.random() <= 0.95:
                img_obj = blur_random(img_obj)
            
            if resize and random.random() <= 0.95:
                img_obj = resize_random(img_obj)

            # mirror image
            if flip and random.random() <= 0.5:
                img_obj = cv2.flip(img_obj, 1)

            # transform (experimental)
            if transform and random.random() <= 0.95:
                img_obj = distort_random(img_obj)

            # choose a random image from the background images

            img_bkg = None
            # pick another image if the chosen one can't be opened
            while (img_bkg is None):
                img_bkg = cv2.imread("bkg/" + random.choice(bkg_list))
            
            # if the background is smaller than the object, expand the background image
            while ((img_bkg.shape[0] < img_obj.shape[0]) or (img_bkg.shape[1] < img_obj.shape[1])):
                img_bkg = resize_img(img_bkg)


            if blur and random.random() <= 0.95:
                img_bkg = blur_random(img_bkg)
            
            # mirror image
            if flip and random.random() <= 0.5:
                img_bkg = cv2.flip(img_bkg, 1)

            img_join, coords = join_images(img_obj, img_bkg)
            
            if tint and random.random() <= 0.95:
                img_join = water_tint(img_join)

            if darken and random.random() <= 0.95:
                img_join = random_darken(img_join)
            
            name = 'save/' + str(i) + "_" + str(j)

            # save txt
            with open(name + ".txt", "w+") as outfile:
                outfile.write(str(i) + " " + str(coords[0]) + " " + str(coords[1]) + " "
                                           + str(coords[2]) + " " + str(coords[3]))

            cv2.imwrite(name + ".jpg", img_join) # save image
            print("saved", name)

    # make empty images


    i = len(obj_count) - 1

    for j in range(obj_count[i]):

        img_bkg = None
        # pick another image if the chosen one can't be opened
        while (img_bkg is None):
            img_bkg = cv2.imread("bkg/" + random.choice(bkg_list))

        name = 'save/' + str(i) + "_" + str(j)

        # save txt
        with open(name + ".txt", "w+") as outfile:
            pass

        cv2.imwrite(name + ".jpg", img_bkg) # save image
        print("saved", name)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Combine images to create new ones", conflict_handler="resolve")

    parser.add_argument("obj_count", help="Amount of images to create",
                    nargs='+', type=int)

    parser.add_argument('-n', action='store_true', default=False,
                    dest='n', help='Combines the images without modifing it')

    parser.add_argument('-t', action='store_true', default=False,
                    dest='t', help='Applies a linear transform distortion to the image')

    parser.add_argument('-b', action='store_true', default=False,
                    dest='b', help='Blurs the image')

    parser.add_argument('-f', action='store_true', default=False,
                    dest='f', help='Flips the image')

    parser.add_argument('-r', action='store_true', default=False,
                    dest='r', help='Resizes the image')

    parser.add_argument('-t', action='store_true', default=False,
                    dest='t', help='Tints the image')

    parser.add_argument('-d', action='store_true', default=False,
                    dest='d', help='Darkens the image')

    args = parser.parse_args()

    args_dict = vars(args)

    get_images_names()

    if args.n:
        modify(args.obj_count, False, False, False, False, False, False)

    elif any([args_dict[a] for a in args_dict if a != 'obj_count']):
        modify(args.obj_count, args.t, args.b, args.f, args.r, args.t, args.d)

    else:
        modify(args.obj_count)
