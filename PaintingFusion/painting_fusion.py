#######################
#                     #
#       Imports       #
#                     #
#######################

import tensorflow as tf
import os
import re
import pixellib
from pixellib.instance import instance_segmentation
import cv2
import matplotlib.pyplot as plt
import random
import numpy as np
import time
import math

#######################
#                     #
#  Global constants   #
#                     #
#######################

# Directory where everything is stored
dir = "" 
user_images = "../" 

models = dir + "models/"
work   = dir + "working_dir/"

img      = user_images + "Interface/images/"
elmnts   = work + "elements/"
mask     = work + "masks/"
bg       = work + "background/"
resultat = user_images + "Interface/results/"

#######################
#                     #
#      Functions      #
#                     #
#######################

def getRandomSquare(imagePath):
    """
    Function getRandomSquare - returns a random square from
    the image
    
    ---------------------------------------------------------
    
    Author     : Arthur Molia - <moliaarthu@eisti.eu>
    Parameters : imagePath : image's path
    Misc       : 
    ---------------------------------------------------------
    """
    image = cv2.imread(imagePath)

    length = len(image)
    width  = len(image[0])

    # Initialize a random percentage between 25 and 75%
    percentage = random.uniform(0.25, 0.75)

    # Initialize the coordinates of the rectangle
    xmin = int(random.uniform(0, length * (1 - percentage)))
    ymin = int(random.uniform(0, width  * (1 - percentage)))

    xmax = int(xmin + length * percentage)
    ymax = int(ymin + width  * percentage)

    # Initialize the mask, full of False   
    masks = np.zeros((length, width, 1), dtype=bool)

    rois = np.array([[xmin, ymin, xmax, ymax]])

    # The extracted object will be the rectangle made by the points
    extracted_objects = np.array([image[xmin:xmax, ymin:ymax]])

    cv2.imwrite("segmented_object_1.jpg", extracted_objects[0])
    
    # Create a mask in the zone corresponding of the rectangle
    for i in range(length):
        for j in range(width):
            if ((i >= xmin) and (i <= xmax) and 
                (j >= ymin) and (j <= ymax)):
                masks[i][j][0] = [True]

    # Store everything in a dictionary
    segmask = {
        'rois': rois,
        'masks': masks,
        'extracted_objects': extracted_objects,
    }

    return segmask, image

def extracting_elmnts(image):
    """
    Function extracting_elmnts - Extracts the main elements
    
    ---------------------------------------------------------
    
    Author     : Ayoola Olafenwa - <https://github.com/ayoolaolafenwa>
    Parameters : image : image path
    Misc       : found on the PixelLib documention then slightly
                 modified:
    https://pixellib.readthedocs.io/en/latest/Image_instance.html
    ---------------------------------------------------------
    """
    segment_image = instance_segmentation()
    segment_image.load_model(models + "mask_rcnn_coco.h5")

    segmask, output = segment_image.segmentImage(image, 
                            extract_segmented_objects=True, save_extracted_objects=True,
                            show_bboxes=True)    

    if (len(segmask["extracted_objects"]) <= 0):
        print("      no element detected in the image" )
        print("      so getting a random rectangle as element")
        segmask, output = getRandomSquare(image)

    return segmask, output

def create_mask(image, segmask):
    """
    Function create_mask - Create the main elements' mask
    
    ---------------------------------------------------------
    
    Author     : Arthur Molia - <moliaarthu@eisti.eu>
    Parameters : image   : image path
                 segmask : segmentation masks' arrays
    Misc       : 
    ---------------------------------------------------------
    """
    masked = cv2.imread(image)

    # Initialises pixel values to black
    for i in range(len(masked)):
        for j in range(len(masked[i])):
            masked[i][j] = [0, 0, 0]

    # Turns pixels that are in a masked area to white
    for i in range(len(segmask["extracted_objects"])):
        for j in range(len(masked)):
            for k in range(len(masked[j])):
                if segmask["masks"][j][k][i]:
                    masked[j][k] = [255, 255, 255]

    return masked

def create_background(img_name):
    """
    Function create_background - Creates the background
             substract the masked parts and inpaint over them
    
    ---------------------------------------------------------
    
    Author     : Arthur Molia - <moliaarthu@eisti.eu>
    Parameters : img_name : image's name
    Misc       : 
    ---------------------------------------------------------
    """
    mask_name = img_name + "_mask.jpg"

    # Reads the images
    image = cv2.imread(img + img_name)
    msk   = cv2.imread(mask + mask_name, 0) # 0 = greyscale

    # Inpaints the background using Alexandru Telea's algorithm
    background = cv2.inpaint(image, msk, 3, cv2.INPAINT_TELEA)

    # Saves the background
    bg_name = img_name + "_background.jpg"
    cv2.imwrite(bg_name, background)
    os.system('mv ' + bg_name + ' "' + bg + bg_name + '"')

def placing_elements(img_dict, bg_name):
    """
    Function placing_elements - Places the elements on the background
    
    ---------------------------------------------------------
    
    Author     : Arthur Molia - <moliaarthu@eisti.eu>
    Parameters : img_dict : dictionnary containing :
                                the images' name as key
                                the segmask in item
                 bg_name  : name of the image selected to be
                            the background
    Misc       : 
    ---------------------------------------------------------
    """
    # Loads the background and the mask corresponding to it
    background = cv2.imread(bg + bg_name + "_background.jpg")
    
    # Background size
    bg_height = background.shape[0]
    bg_width  = background.shape[1]

    # For each element from the images
    for segmask in img_dict.items():
        for i in range(1, len(segmask[1]["extracted_objects"]) + 1):

            element = cv2.imread(elmnts + segmask[0] + "_element_" + str(i) + ".jpg")

            # "Security margins" not to paste an element too much outside
            x_margin = int(element.shape[0] / 3)
            y_margin = int(element.shape[1] / 3)

            # Select random coordinates with security margins
            (x, y) = (int(random.uniform(- x_margin, bg_height - x_margin)), 
                      int(random.uniform(- y_margin, bg_width - y_margin)))
        
            shift = segmask[1]["rois"][i - 1]

            for j in range(element.shape[0]): # height - x
                for k in range(element.shape[1]): # width - y
                    if segmask[1]["masks"][j + shift[0]][k + shift[1]][i-1]:
                        if ((0 <= j + x <= bg_height - 1) and (0 <= k + y <= bg_width - 1)):
                            background[j + x][k + y] = element[j][k]

    return background

def clear_working_dir():
    """
    Function clear_working_dir - clears the work directories
    
    ---------------------------------------------------------
    
    Author     : Arthur Molia - <moliaarthu@eisti.eu>
    Parameters : 
    Misc       : 
    ---------------------------------------------------------
    """
    os.system('rm -r -v ' + mask + '* ; rm -r -v '+ elmnts + '* ; rm -r -v ' + bg + '*')

def process_images(img_list):
    """
    Function process_images - Processes the images
    
    ---------------------------------------------------------
    
    Author     : Arthur Molia - <moliaarthu@eisti.eu>
    Parameters : img_list : list of the images' name
    Misc       : 
    ---------------------------------------------------------
    """
    # Create a dictionnary which will contain the number of
    # element extracted for each image
    img_dict = {}

    # Extracts the main elements and create the masks
    # for every images' path in the list given
    for img_name in img_list:
        print(img_name + " processing")

        # Path of the image
        img_path = img + img_name

        # Extracts the element(s) from the image
        segmask, output = extracting_elmnts(img_path)

        print("   element(s) extracted")

        # Saves the elements
        # Parses every segmented_object in the folder
        i = 0
        for filename in os.listdir():
            if filename.startswith("segmented_object_"):
                i += 1
                element_name = img_name + "_element_" + filename.replace("segmented_object_", "")
                os.system('mv ' + filename + ' "' + elmnts + element_name +'"')

        img_dict[img_name] = segmask

        print("   " + str(i) + " element(s) saved")

        # Creates the mask
        masked = create_mask(img_path, segmask)

        print("   mask created")

        # Saves the image's mask
        mask_name = img_name + "_mask.jpg"
        cv2.imwrite(mask_name, masked)
        os.system('mv ' + mask_name + ' "' + mask + mask_name + '"')

        print("   mask saved")

        # Prints a message to show the avancement
        print(img_name + " processed")

    # Selects the image to be used as background
    # Chooses the one with the smallest area extracted
    min_i = math.inf

    # Parses all the images to select the background
    for img_name in img_dict:
        area = 0

        img_mask = cv2.imread(mask + img_name + "_mask.jpg")

        for i in range(len(img_mask)):
            for j in range(len(img_mask[0])):
                if img_mask[i][j][0] == 255:
                    area += 1

        if area < min_i:
            background_selected = img_name
            min_i = area

    print("Selected '" + background_selected + "' as background")

    # Extracts the background of the selected image
    create_background(background_selected)

    print("background created")

    # Places the other images' elements on the background
    final = placing_elements(img_dict, background_selected)

    # Delete the working files when the processing is finished
    clear_working_dir()

    return(final)

if __name__ == '__main__':
    """
    painting_fusion - creates the base of the generated
                      painting by mixing elements from the
                      user's uploaded paintings
    
    ---------------------------------------------------------
    
    Author     : Arthur Molia - <moliaarthu@eisti.eu>
    Misc       : 
    ---------------------------------------------------------
    """
    start_time = time.time()

    # Parses every image from the folder
    img_list = []
    for filename in os.listdir(img):
        if (filename.endswith(".jpg") 
        or filename.endswith(".jpeg") 
        or filename.endswith(".png")):
            img_list.append(filename)
   
    final = process_images(img_list)

    print("--- %s seconds ---" % (time.time() - start_time))

    cv2.imwrite(resultat + "fusion.jpg", final)
