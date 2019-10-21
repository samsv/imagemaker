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

    img_join[np.where(img_join==[0,0,0])] = img_bkg[np.where(img_join==[0,0,0])]

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
    # These points seem to work fine
    # https://docs.opencv.org/3.4/d4/d61/tutorial_warp_affine.html

    rows, cols, ch = img.shape

    x1 = 10 * random.random()
    y1 = 50 * random.random()

    y2 = 50 * random.random() + 50

    x3 = rows - 100 * random.random()
    y3 = 100*(random.random() - 0.5)

    pts1 = np.float32([[0,0],[0, y2],[rows, 0]])
    pts2 = np.float32([[x1,y1],[0,y2],[x3, y3]])

    M = cv2.getAffineTransform(pts1,pts2)

    return cv2.warpAffine(img, M, (cols, rows))



def blur_random(img):
    """
    Blurs the image to a random percentage.
    """

    blur_level = (int(random.uniform(5, 20)),) * 2
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
        width = random.uniform(0.8,0.9)
        height = random.uniform(0.5,0.7)
    else: # upscale
        width = random.uniform(1,1.1)
        height = random.uniform(1,1.1)

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

            # mirror image
            if flip and random.random() <= 0.5:
                img_bkg = cv2.flip(img_bkg, 1)

            img_join, coords = join_images(img_obj, img_bkg)
            
            if tint and random.random() <= 0.95:
                img_join = water_tint(img_join)

            if darken and random.random() <= 0.95:
                img_join = random_darken(img_join)

            if blur and random.random() <= 0.75:
                img_join = blur_random(img_join)

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
