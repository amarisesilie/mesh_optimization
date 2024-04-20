# see README for complete sources.
# for finding the contours and shifting the contours, the tutorial by Rosebrock (2021) and the OpenCV documentation were used.

import numpy as np
import cv2
import os
import imutils
from natsort import natsort

def find_object_center(image):
    """Finds the center of the object in the image.
    It does this by finding the contour of the object
    and deriving the x and y coordinates from that.

    Parameters
    ----------
    image : jpeg, png, tif, etc

    Returns
    -------
    tuple (int, int)
        returns (obj_x, obj_y) aka coordinates of the object's center

    """

    # convert image to grayscale
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # blur the image
    blurred = cv2.GaussianBlur(image_gray, (5, 5), 0)

    # threshold the image (binarization of the image)
    image_threshold = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

    # find contours in thresholded image
    contours = cv2.findContours(image_threshold.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    # loop over contours
    for c in contours:
    # calculate contour center
        M = cv2.moments(c)
        obj_x = int(M["m10"] / M["m00"])
        obj_y = int(M["m01"] / M["m00"])

    return obj_x, obj_y

def move_to_center(image, obj_x, obj_y):
    """Moves the object to the center of the image. It does this 
    by calculating the distance between the center of the object
    and the center of the image.

    Parameters
    ----------
    image : jpeg, png, tif, etc
    obj_x : int
        x-coordinate of the center of the object
    obj_y : int
        y-coordinate of the center of the object
    image_name : str
        name of the image used for naming the shifted image

    Returns
    -------
    image
        returns an image of the shifted object
    
    """

    # height, width of image
    rows, cols = image.shape[:2]

    # center of the image
    center_x = int(cols / 2)
    center_y = int(rows / 2)

    # the shift in (x, y) direction
    tx = obj_x - center_x
    ty = obj_y - center_y

    # transformation matrix
    transformation_matrix = np.float32([ [1,0,-tx] , [0,1,-ty] ])

    # shifting the image according to the matrix
    # 3rd argument of warpAffine() is (width (cols), height (rows)). 
    shifted_image = cv2.warpAffine(image, transformation_matrix, (cols, rows))

    return shifted_image

def make_dst(im_1, im_2):
    """Generates dst of two shifted images for overlay."""

    dst = cv2.addWeighted(im_1, 1, im_2, 1, 0)
    return dst

all_shifted_images = []
file_type = ".tif"
directory_path = "zebrafish_embryo/all_contour"
for file in natsort.natsorted(os.listdir(directory_path)):
    if file.endswith(file_type):
        image = cv2.imread(f"{directory_path}/{file}")
        image_name = file[:-4] # remove .tif
        aligned_image = move_to_center(image=image, obj_x=find_object_center(image)[0], 
                    obj_y=find_object_center(image)[1])

        # save the shifted image
        save_shifted_path = 'embryo_allshifted'
        try: 
            cv2.imwrite(os.path.join(save_shifted_path, f"shifted{image_name}.tif"), aligned_image)
        except:
            print("Could not save image!")

        all_shifted_images.append(aligned_image)

# laying the images on top of each other
start_dst = make_dst(all_shifted_images[0], all_shifted_images[1])
for img in all_shifted_images[2:]:
    start_dst = make_dst(start_dst, img)
cv2.imshow("Image Alignment Overlay", start_dst)
# cv2.imwrite(os.path.join('thesis_images', f"after-align.png"), start_dst)

cv2.waitKey(0)
cv2.destroyAllWindows()
