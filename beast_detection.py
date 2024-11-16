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

IMG_WIDTH, IMG_HEIGHT = 640, 640

# used for positioning CAMERA not objects
def get_random_coords(y_range, x_range, z_range):
    random_y = random.randint(*y_range)
    random_x = random.randint(*x_range)
    random_z = random.randint(*z_range)
    return random_y, random_x, random_z

def get_random_rotation():
     # Generate random rotation angles in degrees
    yaw_degrees = random.uniform(0, 360)
    yaw_radians = yaw_degrees * (3.14159 / 180)
    return airsim.Quaternionr(0, 0, yaw_radians)

def get_random_position(first_corner, second_corner, z=1):
    # Generate random x and y within the bounds of the box
    x = random.uniform(first_corner[0], second_corner[0])
    y = random.uniform(first_corner[1], second_corner[1])
    return airsim.Vector3r(x, y, z)

def distance_between_positions(pos1, pos2):
    # calc euclidean distance between two positions
    return math.sqrt((pos1.x_val - pos2.x_val)**2 + (pos1.y_val - pos2.y_val)**2)

def get_valid_position(first_corner, second_corner, existing_locations, min_distance):
    valid_position = False
    while not valid_position:
        # generate a random position
        new_position = get_random_position(first_corner, second_corner)

        # check if it is far enough from all existing positions
        valid_position = all(
            distance_between_positions(new_position, loc) >= min_distance
            for loc in existing_locations
        )
        if valid_position:
            return new_position

def place_objects_randomly(object_pool, first_corner, second_corner, max_num):
    # randomly select max_num objects from pool
    selected_objects = random.sample(object_pool, min(max_num, len(object_pool)))
    # empty list of poses (object locations)
    random_locations =  []

    for obj in selected_objects:
        # get valid position
        position = get_valid_position(first_corner, second_corner, random_locations, min_distance=6)    # tweak min_distance to separate objects
        orientation = get_random_rotation()
        # add to random_locations list
        random_locations.append(position)
        # before adding pose to list of locations, check to make sure they are far enough apart from each other
        object_pose = airsim.Pose(position, orientation)             
        client.simSetObjectPose(obj, object_pose, True)

def move_cam(cam_quarter, camera_name):
    # move camera randomly
    random_y, random_x, random_z = get_random_coords(y_range, x_range, z_range)
    camera_pose = airsim.Pose(
        airsim.Vector3r(random_y, random_x, random_z),
        cam_quarter
    )
    client.simSetCameraPose(camera_name, camera_pose)

def save_box_info(objects, counter):
    class_id = "#"
    if objects:
        bbox_path = os.path.join(temp_dir, f"detection_{counter}.txt")
        with open(bbox_path, 'w') as f:
            for obj in objects:
                x_min, y_min = int(obj.box2D.min.x_val), int(obj.box2D.min.y_val)
                x_max, y_max = int(obj.box2D.max.x_val), int(obj.box2D.max.y_val)
                # x_min, y_min, x_max, y_max
                # f.write(f"{obj.name} {x_min} {y_min} {x_max} {y_max}\n")

                # yolo format: x_center, y_center, width, height
                x_center = (x_min + x_max / 2) / IMG_WIDTH
                y_center = (y_min + y_max / 2) / IMG_HEIGHT
                width = x_max - x_min / IMG_WIDTH   # divide by width to normalize
                height = y_max - y_min / IMG_HEIGHT

                # if checks for obj.name
                if re.match(r'SK_.*', obj.name):
                    class_id = "0"

                f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")

                # Draw the bounding box on the image
                # cv2.rectangle(png, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)  # Blue color with thickness of 2
            print(f"Saved detection info to {bbox_path}")

def save_frame(png, counter):
    image_path = os.path.join(temp_dir, f"frame_{counter}.png")
    cv2.imwrite(image_path, png)

def reset_objects_to_origin(object_pool):
    origin_position = airsim.Vector3r(0, 0, 0)  # define the origin position
    for obj in object_pool:
        # set the object's pose to the origin
        object_pose = airsim.Pose(origin_position, airsim.Quaternionr(0, 0, 0, 1))
        client.simSetObjectPose(obj, object_pose)

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
y_range = (-70, -30)
x_range = (-120, -65)
z_range = (-50, -40)

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
first_corner = (-40, -80)
second_corner = (-60, -105)  # change this

while True and image_counter <= DATASET_LENGTH:
    rawImage = client.simGetImage(camera_name, image_type)
    if not rawImage:
        continue
    png = cv2.imdecode(airsim.string_to_uint8_array(rawImage), cv2.IMREAD_UNCHANGED)
    objects = client.simGetDetections(camera_name, image_type)
    if objects:
        # save bounding box info to .txt file for all objects in frame
        save_box_info(objects, image_counter)
        # snap pic
        save_frame(png, image_counter)
        image_counter += 1

    cv2.imshow("AirSim", png)

    move_cam(cam_quarter, camera_name)

    place_objects_randomly(object_pool, first_corner, second_corner, MAX_OBJ_NUM)

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
    # reset_objects_to_origin(object_pool)
    # resetting objects to origin results in bug where objects do not appear on cv window output

cv2.destroyAllWindows() 

