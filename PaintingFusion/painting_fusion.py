# TODO
# remove the background from the images
# change the global constants according to the tree structure of the project
# get the images from the user
# return the final image properly

#######################
#                     #
#       Imports       #
#                     #
#######################

from json.tool import main
import torch
import tensorflow as tf
import os
import re
import cv2
import matplotlib.pyplot as plt
import random
import numpy as np
import time

#######################
#                     #
#  Global constants   #
#                     #
#######################

# Model used to dectect the elements
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

# Directory where everything is stored
dir = "" 

models = dir + "models/"
work   = dir + "working_dir/"

img    = work + "images/"

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

    # Initialise the array where the elements will be stored
    cropped = []

    # Will become a black image whith white parts corresponding
    # to the elements location
    masked = image.copy()

    # Fill the mask with black pixels
    masked[0:len(masked), 0:len(masked[0])] = [0, 0, 0]

    # Initialize a random percentage between 25 and 75%
    percentage = random.uniform(0.25, 0.75)

    # Initialize the coordinates of the rectangle
    xmin = int(random.uniform(0, length * (1 - percentage)))
    ymin = int(random.uniform(0, width  * (1 - percentage)))

    xmax = int(xmin + length * percentage)
    ymax = int(ymin + width  * percentage)

    # Store the randomly chosen rectangle in cropped
    cropped.append(image[xmin:xmax, ymin:ymax])

    # Fill the corresponding area with white
    masked[xmin:xmax, ymin:ymax] = [255, 255, 255]

    return cropped, masked

def extracting_elmnts(image):
    """
    Function extracting_elmnts - Extracts the main elements
    
    ---------------------------------------------------------
    
    Author     : Arthur Molia - <moliaarthu@eisti.eu>
    Parameters : image : image path
    Misc       : 
    ---------------------------------------------------------
    """
    # Uses the model on the image
    results = model(image)

    # If the model has detected elements, it extracts them
    if (results.xyxy[0].size()[0] > 0):
        # Initialise the array where the elements will be stored
        cropped = []

        # Read the image
        base = cv2.imread(image)
        # Will become a black image whith white parts corresponding
        # to the elements location
        masked = base.copy()

        # Fill the mask with black pixels
        masked[0:len(masked), 0:len(masked[0])] = [0, 0, 0]

        # For each element extracted
        for i in range(results.xyxy[0].size()[0]):
            # Extract the position of the element
            ymin = round(results.xyxy[0][i][0].item())
            xmin = round(results.xyxy[0][i][1].item())
            ymax = round(results.xyxy[0][i][2].item())
            xmax = round(results.xyxy[0][i][3].item())

            # Store the element in cropped
            # cropped.append(remove_background(base[xmin:xmax, ymin:ymax])) #TODO
            cropped.append(base[xmin:xmax, ymin:ymax])

            # Fill the corresponding area with white
            masked[xmin:xmax, ymin:ymax] = [255, 255, 255]

        # Print a message for the user
        print("   extracted " + str(results.xyxy[0].size()[0]) + " element(s)")
    
    # Else it picks a random rectangle in the image
    else:
        cropped, masked = getRandomSquare(image)

        # Print a message for the user
        print("   extracted 1 random rectangle as element")

    return cropped, masked        

def create_background(image, msk):
    """
    Function create_background - Creates the background
             substract the masked parts and inpaint over them
    
    ---------------------------------------------------------
    
    Author     : Arthur Molia - <moliaarthu@eisti.eu>
    Parameters : image : future background
                 msk   : mask
    Misc       : 
    ---------------------------------------------------------
    """
    msk = cv2.cvtColor(msk, cv2.COLOR_BGR2GRAY)

    # Inpaints the background using Alexandru Telea's algorithm
    return cv2.inpaint(image, msk, 3, cv2.INPAINT_TELEA)

def placing_elements(img_list, crop_dict, background):
    """
    Function placing_elements - Places the elements on the background
    
    ---------------------------------------------------------
    
    Author     : Arthur Molia - <moliaarthu@eisti.eu>
    Parameters : img_list   : list of the images' names
                 crop_dict  : dictionary containing the
                              elements cropped from the
                              paintings
                 background : image selected to be the
                              background of the new painting
    Misc       : 
    ---------------------------------------------------------
    """    
    # Background size
    bg_height = len(background)
    bg_width  = len(background[0])

    # For each painting, for each cropped part in the paintings
    for painting in crop_dict:
        for cropped in crop_dict[painting]:
            x_margin = int(len(cropped)    / 3)
            y_margin = int(len(cropped[0]) / 3)

            # Select random coordinates with security margins
            (x, y) = (int(random.uniform(- x_margin, bg_height - x_margin)), 
                      int(random.uniform(- y_margin, bg_width  - y_margin)))
            
            xmin = max(0, x)
            ymin = max(0, y)
            xmax = min(x + len(cropped),    bg_height)
            ymax = min(y + len(cropped[0]), bg_width)
            
            # background[xmin:xmax, y:ymax] = cropped[0:(xmax - x), 0:(ymax - y)]

            for i in range(x, xmax):
                for j in range(y, ymax): 
                    if ((0 <= i <= bg_height - 1) and (0 <= j <= bg_width - 1)):
            #             # if ((0 <= i + x <= bg_width - 1) and (0 <= j + y <= bg_height - 1)):
            #             # if ((0 <= i <= bg_height - 1) and (0 <= j <= bg_width - 1)):
                        background[i][j] = cropped[i - x][j - y]

    return background

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
    img_dict  = {}
    crop_dict = {}
    mask_dict = {}

    # Extracts the main elements and create the masks
    # for every images' path in the list given
    for img_name in img_list:
        print(img_name + " processing")

        # Path of the image
        img_path = img + img_name

        img_dict[img_name] = cv2.imread(img_path)

        # Extracts the element(s) from the image
        cropped, masked = extracting_elmnts(img_path)
        crop_dict[img_name] = cropped
        mask_dict[img_name] = masked

    # Selects the image to be used as background
    # Chooses the one with the smallest area extracted
    min_i = 0
    for i in range(len(crop_dict[img_list[0]])):
        min_i += len(crop_dict[img_list[0]][i]) * len(crop_dict[img_list[0]][i][0])

    background_selected = img_list[0]

    # Parses all the images to select the background
    for key in img_dict:
        area = 0
        for i in range(len(crop_dict[key])):
            area += len(crop_dict[key][i]) * len(crop_dict[key][i][0])

        if area < min_i:
            background_selected = key
            min_i = area
        
    print("Selected '" + background_selected + "' as background")

    # Extracts the background of the selected image
    background = create_background(img_dict[background_selected], mask_dict[background_selected])

    print("background created")

    # Places the other images' elements on the background
    final = placing_elements(img_list, crop_dict, background)

    return(final)

if __name__ == '__main__':
    """
    painting_fusion - creates the base of the generated
                      painting by mixing elements from the
                      user's uploaded paintings
    
    ---------------------------------------------------------
    
    Author     : Arthur Molia - <moliaarthu@eisti.eu>
    Misc       : Still need to add a function to remove the
                 background from the elements
    ---------------------------------------------------------
    """
    start_time = time.time()

    img_list = ["gioconda.jpg", "leRadeauDeLaMeduse.jpg", "LUltimaCena.jpg", "NascitaDiVenere.jpg"]

    # for i in range(len(img_list)):
    #     cv2.imshow(img_list[i], cv2.imread(img + img_list[i])) # debug
    #     time.sleep(5) # debug

    final = process_images(img_list)

    print("--- %s seconds ---" % (time.time() - start_time))

    cv2.imwrite("final_image.jpg", final) # debug