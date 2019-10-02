# Image Maker
Python script to create new images to use on a neural network based on some given objects and background images.

To use the script create a folder called "obj" containing the objects you wish to train your network. The image names represent the class of the object inside it (e.g., if you have two classes, where class 0 is a soda can and class 1 is a computer mouse, the soda can image must be named 0.png or 0.jpg..., while the mouse image must be named 1.jpg...).

Create a folder called "bkg" containing the backgrounds to put the classes images on and create a "save" folder as well where the images will be saved.

Supported image extensions are .png, .jpg and .gif.

## Usage
Just run 
```bash
python3 image_maker.py
```

If you want to edit the parameters
```python
import image_maker
# List containing how many new images to create for each object
# In this case it will create 100 new images for the object with class number 0
# and 150 new images for the object with the class number 1
new_images = [100, 150] 
image_maker.get_images_names() # Get images from obj and bkg folder
image_maker.modify(new_images) # Create and save the new images
```

## Parameters
This modify function has the following parameters

* blur: blurs the image
* flip: mirrors the image
* resize: resizes the object size
* tint: Adds a blue or green tint to the image to emulate water
* darken: Darkens the image

All the parameters are invoked at random. The intensity of their effects is also random, when applicable (e.g. the blur levels are random, as well as the tint (how blue or green to turn the image), but flip will always just mirror the image).

To turn a parameter off just call modify while setting it to false:

```python
import image_maker
# List containing how many new images to create for each object
# In this case it will create 100 new images for the object with class number 0
# and 150 new images for the object with the class number 1
new_images = [100, 150] 
image_maker.get_images_names() # Get images from obj and bkg folder
# Create and save the new images. Don't mirror or darken the images
image_maker.modify(new_images, flip=False, darken=False) 
```