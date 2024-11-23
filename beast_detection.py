import setup_path 
import airsim
import cv2
import numpy as np 
import pprint
import os
import re
import tempfile
import math
import random
import time
import unreal
import pyautogui
import functions

IMG = {
    "width": 640,
    "height": 640
}

# connect to the AirSim simulator
client = airsim.client.VehicleClient()
client.confirmConnection()

# set camera name and image type to request images and detections
camera_name = "0"
image_type = airsim.ImageType.Scene

# cars coords
car_vectors = [
    (-50, -95, -50)
    # with camera default on top of cluster looking down
    # first value changes up down or y coord: [ +-20 ] + moves up, - moves down (y-axis)
    # second value changes left right or x coord: [ +-30 ] + moves left, - moves right
    # third value changes height of camera or z coord: [ -10 ] - moves cam down (z-axis)
]
x_range = (-68, -37)   # (-65, -40)     solid lines, can tweak a little to get them closer to the edge
y_range = (-108, -77)    # (-105, -80)
z_range = (-50, -40)    # (-50, -45) 
ranges = [x_range, y_range, z_range]

car_quarterns = [
    (-10, 0.54, -0.35, 0.67)
    # first value should be negative to look down from camera
    # range: (-5 : -10) lower end can be super low but doesnt change much
]
cam_quarter = airsim.Quaternionr(-5, 0.55, -0.35, 0.67)

# set desired camera position
camera_pose = airsim.Pose(
    airsim.Vector3r(-50, -95, -40),
    cam_quarter
)
# set camera above objects
client.simSetCameraPose(camera_name, camera_pose)

# set detection radius in [cm]
client.simSetDetectionFilterRadius(camera_name, image_type, 200 * 50) 
# add desired object name to detect in wild card/regex format
client.simAddDetectionFilterMeshName(camera_name, image_type, "SK_*") 

# create a small openCV window
cv2.namedWindow("AirSim", cv2.WINDOW_NORMAL)
cv2.resizeWindow("AirSim", 720, 480)

temp_dir = os.path.join(tempfile.gettempdir(), "dataset_images")
print("Images will be saved to %s" % temp_dir)

image_counter = 0
DATASET_LENGTH = 2000
try:
    os.makedirs(temp_dir)
except OSError:
    if not os.path.isdir(temp_dir):
        raise

# Instantiate object pool and define placement box
object_pool = client.simListSceneObjects("SK_.*")   # change this to SM_* if on beast
print(object_pool)
MAX_OBJ_NUM = 5
first_corner = (-35, -75)
second_corner = (-70, -110)  # change this

while True and image_counter < DATASET_LENGTH:
    rawImage = client.simGetImage(camera_name, image_type)
    if not rawImage:
        continue
    png = cv2.imdecode(airsim.string_to_uint8_array(rawImage), cv2.IMREAD_UNCHANGED)
    objects = client.simGetDetections(camera_name, image_type)
    if objects:
        # save bounding box info to .txt file for all objects in frame
        functions.save_box_info(objects, image_counter, IMG, temp_dir)
        functions.save_frame(png, image_counter, temp_dir)
        image_counter += 1

    cv2.imshow("AirSim", png)

    functions.reset_objects_to_origin(object_pool, client)

    functions.move_cam(cam_quarter, camera_name, ranges, client)

    functions.place_objects_randomly(object_pool, first_corner, second_corner, MAX_OBJ_NUM, client)

    pyautogui.press('space')


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    elif cv2.waitKey(1) & 0xFF == ord('c'):
        client.simClearDetectionMeshNames(camera_name, image_type)
    elif cv2.waitKey(1) & 0xFF == ord('a'):
        client.simAddDetectionFilterMeshName(camera_name, image_type, "SK_*")
    elif cv2.waitKey(1) & 0xFF == ord('p'):
        # save image to the temp folder
        image_path = os.path.join(temp_dir, f"frame_{image_counter}.png")
        cv2.imwrite(image_path, png)
        print(f"Saved {image_path}")
        image_counter += 1
        # test simGetImage vs cv2
    elif cv2.waitKey(1) & 0xFF == ord('l'):
        current_pos = client.simGetCameraInfo(camera_name)
        print(current_pos)

    time.sleep(0.1)
    # resetting objects to origin results in bug where objects do not appear on cv window output

cv2.destroyAllWindows() 
