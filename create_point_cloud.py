# see README for complete sources.
# for finding the contours, the tutorial by Rosebrock (2021) and the OpenCV documentation were used.
# for extracting the point cloud, the Open3D documentation was used.

import open3d as o3d
import numpy as np
import cv2
import imutils
import os
from natsort import natsort

all_contour_list = []
z = 0
# ooi = "embryo" # object of interest
# directory_path = "embryo_allshifted" # zebrafish embryo
ooi = "mammary" # object of interest
directory_path = "mammary_gland/all_contour"

for file in natsort.natsorted(os.listdir(directory_path)):
    if file.endswith(".tif"):
        image = cv2.imread(f"{directory_path}/{file}")

        # convert image to grayscale
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # threshold the image (binarization of the image)
        image_threshold = cv2.threshold(image_gray, 60, 255, cv2.THRESH_BINARY)[1]

        # find contours in thresholded image
        contours = cv2.findContours(image_threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)

        # loop over contours
        for i in range(len(contours)):
            for j in range(len(contours[i])):
                [[x, y]] = contours[i][j] # to get the x, y
                all_contour_list.append([x, y, z]) # all_contour_list is a nested list
        z += 10

contours_array = np.array(all_contour_list) # convert list to array

# making, drawing and saving the pcl
pcl = o3d.geometry.PointCloud()
pcl.points = o3d.utility.Vector3dVector(contours_array)
o3d.visualization.draw_geometries([pcl]) # prints the point cloud
o3d.io.write_point_cloud(f"{ooi}-pcl.ply", pcl) # saves the point cloud in ply format

# estimating normals, orienting them consistently, drawing and saving the oriented pcl
pcl.estimate_normals()
# o3d.visualization.draw_geometries([pcl], point_show_normal=True)
pcl.orient_normals_consistent_tangent_plane(100) # k nearest neighbors used in constructing the Riemannian graph
o3d.visualization.draw_geometries([pcl], point_show_normal=True)
o3d.io.write_point_cloud(f"oriented-{ooi}-pcl.ply", pcl) # saves the oriented point cloud in ply format
