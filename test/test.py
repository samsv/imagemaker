import cv2
import numpy as np
from random import random, choice, uniform
import os



def resize_img(img, width=1.5, height=1.5):
    width = int(img.shape[1] * width)
    height = int(img.shape[0] * height)
    
    resized = cv2.resize(img, (width, height))

    return resized

def join_images(img_obj, img_bkg):
    """
    Places the object image on the background images. 
    """

    # ensure the object is fully visible
    y_percentage = img_obj.shape[0] / img_bkg.shape[0]
    x_pencentage = img_obj.shape[1] / img_bkg.shape[1]

    # choose a random position on screen
    y_offset = int(uniform(0, 1 - y_percentage) * img_bkg.shape[0])
    x_offset = int(uniform(0, 1 - x_pencentage) * img_bkg.shape[1])

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


img = cv2.imread("../imagemaker/obj/0.png")

rows, cols, ch = img.shape

print("Height: ", rows)
print("Width: ", cols)

y = x = random()*50

pts1 = [[x, y]]
pts2 = [[x+100,y+100]]

x,y = rows*random(), cols*random()/2
r = random()*30
pts1.append([x, y])
pts2.append([x+r+50, y+r+50])

pts1.append([rows/2, cols/2])
pts2.append([rows/2, cols/2])


#pts1.append([rows, cols])
#pts2.append([rows, cols])   

pts1 = np.float32(pts1)
pts2 = np.float32(pts2)

pts1 = np.float32([[0,0],[0, 100],[rows, 0]])
pts2 = np.float32([[10,0],[0,100],[rows, -100]])

print(pts1)

for i in range(20):
    x1 = 10*random()
    y1 = 50*random()

    y2 = 50*random() + 50

    x3 = rows - 100*random()
    y3 = 100*(random() - 0.5)

    pts1 = np.float32([[0,0],[0, y2],[rows, 0]])
    pts2 = np.float32([[x1,y1],[0,y2],[x3, y3]])

    print(pts2)

    M = cv2.getAffineTransform(pts1,pts2)

    translated_img = cv2.warpAffine(img, M, (cols, rows))

    tmp = cv2.cvtColor(translated_img, cv2.COLOR_BGR2GRAY)
    _,alpha = cv2.threshold(tmp,0,255,cv2.THRESH_BINARY)
    b, g, r = cv2.split(translated_img)
    rgba = [b,g,r, alpha]
    img_obj = cv2.merge(rgba,4)



    img_bkg = None
    # pick another image if the chosen one can't be opened
    while (img_bkg is None):
        img_bkg = cv2.imread("../imagemaker/bkg/" + choice([f for f in os.listdir('../imagemaker/bkg') if f[-4:] in ['.png','.jpg']]))
    
    # if the background is smaller than the object, expand the background image
    while ((img_bkg.shape[0] < img_obj.shape[0]) or (img_bkg.shape[1] < img_obj.shape[1])):
        img_bkg = resize_img(img_bkg)

    b, g, r = cv2.split(img_bkg)
    a = np.ones(b.shape, dtype=b.dtype) * 50 #creating a dummy alpha channel image.
    img_bkg = cv2.merge((b, g, r, a))

    translated_img = join_images(img_obj, img_bkg)

    cv2.imwrite('s.png', img_bkg)
    break

    # cv2.imshow("Translated image", translated_img)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

