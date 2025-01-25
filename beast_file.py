# functions.py
############################
import airsim
import cv2
import math
import os
import random
import re
import time

# Define dict of all object regex to class IDs
regex_to_class_id = {
    r'SM_.*': "0",
    r'football_.*': "1",
    r'Wilson_.*': "2",      # football
    r'Matress.*': "3",
    r'Baseball.*': "4",
    r'luggage.*': "5",
    r'Black_Umbrella.*': "6",
    r'volleyball.*': "7",
    r'tenis_.*': "8",
    r'Stop_.*': "9",
    r'motorcycle.*': "10",
    # r'Default_.*': "10",
    r'small_boat_.*': "11",
    r'Basketball_.*': "12"
}
MAX_OBJ_NUM = 5

# used for positioning CAMERA not objects
def get_random_coords(x_range, y_range, z_range):
    random_x = random.randint(*x_range)
    random_y = random.randint(*y_range)
    random_z = random.randint(*z_range)
    return random_x, random_y, random_z

def get_random_rotation(x_rotation=0, y_rotation=0, z_rotation=0):
    x_radians = math.radians(x_rotation)
    y_radians = math.radians(y_rotation)
    z_radians = math.radians(z_rotation)
    return airsim.Quaternionr(x_radians, y_radians, z_radians)

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
        
def decrement_count(objects, num_objs):
    for obj in objects:
        name = obj.name
        for pattern in num_objs:
            if re.match(pattern, name) and num_objs[pattern] > 0:
                num_objs[pattern] -= 1
                print(f"Placed {name}. Remaining: {num_objs[pattern]}")       # may move this to save box in beast_detection

# NEW PLACE_OBJECTS FUNCTION
def place_objects_randomly(object_pool, num_objs, first_corner, second_corner, max_num, client):
    # hold names of objs that should be rotated differently
    # currently: boat (test out other models first), stop sign, maybe umbrella
    DIFF_ROTATIONS = {
        r'Stop_.*': -60
    }
    # filter object_pool to only include objects that have > 0 instances to be placed
    valid_objects = [
        obj for obj in object_pool
        for pattern in num_objs
        if re.match(pattern, obj) and num_objs[pattern] > 0
    ]
    # randomly select max_num objects from pool
    selected_objects = random.sample(valid_objects, min(max_num, len(valid_objects)))
    # empty list of poses (object locations)
    random_locations =  []

    for obj_name in selected_objects:
        fixed_orientation = None        # reset for each object
        for pattern in num_objs:    # pattern is just the regex key
            if re.match(pattern, obj_name):
                if num_objs[pattern] > 0:
                    # check for objects that require different rotations
                    for rotation_pattern, x_rotation in DIFF_ROTATIONS.items():
                        if re.match(rotation_pattern, obj_name):
                            # use the x_rotation stated
                            fixed_orientation = get_random_rotation(x_rotation=x_rotation)
                    # get valid position
                    position = get_valid_position(first_corner, second_corner, random_locations, min_distance=7)    # tweak min_distance to separate objects
                    if fixed_orientation:
                        orientation = fixed_orientation
                    else:
                        orientation = get_random_rotation(z_rotation=random.uniform(0, 360))     # bug where objects that are rotated (stop sign, etc...) get rotated and are not in ideal rotation
                    # add to random_locations list
                    random_locations.append(position)
                    # before adding pose to list of locations, check to make sure they are far enough apart from each other
                    object_pose = airsim.Pose(position, orientation)             
                    client.simSetObjectPose(obj_name, object_pose, True)

                    # decrement count from pattern's total
                    # num_objs[pattern] -= 1
                    # print(f"Placed {obj_name}. Remaining: {num_objs[pattern]}")       # may move this to save box in beast_detection

def move_cam(cam_quarter, camera_name, ranges, client):
    # move camera randomly
    random_x, random_y, random_z = get_random_coords(ranges[0], ranges[1], ranges[2])
    camera_pose = airsim.Pose(
        airsim.Vector3r(random_x, random_y, random_z),
        cam_quarter
    )
    client.simSetCameraPose(camera_name, camera_pose)

def set_random_floor(client, floor_objs, floor_materials):
    choice = random.choice(floor_materials)
    for floor in floor_objs:
        client.simSetObjectMaterial(floor, choice)

def rotate_bounding_box(x_min, y_min, x_max, y_max, angle, img_width, img_height):
    """Adjust bounding box coordinates after rotation."""
    if angle == 90:
        # Rotate 90 degrees clockwise
        x_min_new = y_min
        y_min_new = img_width - x_max
        x_max_new = y_max
        y_max_new = img_width - x_min
    elif angle == 180:
        # Rotate 180 degrees
        x_min_new = img_width - x_max
        y_min_new = img_height - y_max
        x_max_new = img_width - x_min
        y_max_new = img_height - y_min
    elif angle == 270:
        # Rotate 270 degrees clockwise (or 90 counterclockwise)
        x_min_new = img_height - y_max
        y_min_new = x_min
        x_max_new = img_height - y_min
        y_max_new = x_max
    else:
        # No rotation (0 degrees)
        x_min_new = x_min
        y_min_new = y_min
        x_max_new = x_max
        y_max_new = y_max

    return x_min_new, y_min_new, x_max_new, y_max_new

def save_box_info(objects, counter, png, img, temp_dir, angle):
    print(f"Angle: {angle}")
    class_id = "#"
    if objects:
        bbox_path = os.path.join(temp_dir, f"frame_{counter}.txt")
        with open(bbox_path, 'w') as f:
            for obj in objects:
                x_min, y_min = int(obj.box2D.min.x_val), int(obj.box2D.min.y_val)
                x_max, y_max = int(obj.box2D.max.x_val), int(obj.box2D.max.y_val)
                # print(f"min: ({x_min}, {y_min}), max: ({x_max}, {y_max})")

                # Adjust bounding box based on the rotation
                x_min, y_min, x_max, y_max = rotate_bounding_box(x_min, y_min, x_max, y_max, angle, img.get('width'), img.get('height'))

                # yolo format: x_center, y_center, width, height
                x_center = ((x_min + x_max) / 2) / img.get('width')
                y_center = ((y_min + y_max) / 2) / img.get('height')
                width = (x_max - x_min) / img.get('width')     # divide by width to normalize
                height = (y_max - y_min) / img.get('height')

                # print(IMG_WIDTH, IMG_HEIGHT)
                for regex, cid in regex_to_class_id.items():
                    if re.match(regex, obj.name):
                        print(f"Regex: {regex}/t name: {obj.name}")
                        class_id = cid
                        break  

                # f.write(f"{class_id} {x_min} {y_min} {x_max} {y_max}\n")
                f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")

                # Draw the bounding box on the image
                cv2.rectangle(png, (x_min, y_min), (x_max, y_max), (255, 0, 0), 1)  # Blue color with thickness of 2
            print(f"Saved detection info to {bbox_path}")
            time.sleep(3)

def random_rotate(image):
    """
    Randomly rotates the image by 0, 90, 180, or 270 degrees.
    The output image retains the original square dimensions.
    """
    # Generate a random choice of rotation: 0, 90, 180, or 270 degrees
    rotation_angle = random.choice([0, 90, 180, 270])

    # Apply rotation based on the angle
    if rotation_angle == 90:
        rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif rotation_angle == 180:
        rotated_image = cv2.rotate(image, cv2.ROTATE_180)
    elif rotation_angle == 270:
        rotated_image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    else:  # 0 degrees, no rotation
        rotated_image = image

    return rotated_image, rotation_angle

def save_frame(png, counter, temp_dir, objects, img):
    # rotated_png, angle = random_rotate(png)

    image_path = os.path.join(temp_dir, f"frame_{counter}.png")
    cv2.imwrite(image_path, png)

    save_box_info(objects, counter, png, img, temp_dir, angle=0)

def reset_objects_to_origin(object_pool, client):
    origin_position = airsim.Vector3r(0, 0, 0)
    for obj in object_pool:
        object_pose = airsim.Pose(origin_position, airsim.Quaternionr(0, 0, 0, 1))
        client.simSetObjectPose(obj, object_pose)

def add_mesh_filters(client, cam_name, image_type, obj_list):
    for i in range(len(obj_list)):
        client.simAddDetectionFilterMeshName(cam_name, image_type, obj_list[i])

def generate_object_pool(client, obj_list):
    object_pool = []
    for i in range(len(obj_list)):
        object_pool += client.simListSceneObjects(obj_list[i])
    return object_pool

########################################################
########################################################
########################################################
# beast_detection.py
############################
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
import pyautogui
import functions

# VARIABLES
###############################################
###############################################
IMG = {
    "width": 640,
    "height": 640
}
# OBJECT STRINGS (regex from name of object within UE environment)
###############################################
car = "SM_.*"
soccer_ball = "football_.*"     # soccerball
football = "Wilson_.*"
mattress = "Matress.*"
baseball_bat = "Baseball.*"
suitcase = "luggage.*"
umbrella = "Black_Umbrella.*"
volleyball = "volley_ball.*"
tennis_r = "tenis_.*"
stop_sign = "Stop_.*"
motorcycle = "Generic_Bike.*"
# mannequin = "Default_.*"
boat = "small_boat.*"
basketball = "basketball.*"
ground = "Floor.*"
###############################################
# Add variables above to obj_list
obj_list = [car, soccer_ball, football, mattress, baseball_bat, suitcase, umbrella, volleyball,
            tennis_r, stop_sign, motorcycle, boat, basketball]
mesh_list = [obj.replace(".", "") for obj in obj_list] 
num_objs = {obj: 100 for obj in obj_list}
###############################################
###############################################
floor_list = [ground]
floor_materials = ["Material'/Game/M_grass1.M_grass1'", "Material'/Game/M_grass2.M_grass2'", "Material'/Game/M_grass3.M_grass3'"]

# connect to the AirSim simulator3
client = airsim.client.VehicleClient()
client.confirmConnection()

floor_objs = functions.generate_object_pool(client, floor_list)
print(floor_objs)

# set camera name and image type to request images and detections
camera_name = "0"
image_type = airsim.ImageType.Scene

client.simClearDetectionMeshNames(camera_name, image_type)

# cars coords
car_vectors = [
    (-50, -95, -50)
    # with camera default on top of cluster looking down
    # first value changes up down or y coord: [ +-20 ] + moves up, - moves down (y-axis)
    # second value changes left right or x coord: [ +-30 ] + moves left, - moves right
    # third value changes height of camera or z coord: [ -10 ] - moves cam down (z-axis)
]
x_range = (-70, -30)
y_range = (-120, -65)
z_range = (-50, -40)
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

client.simClearDetectionMeshNames(camera_name, image_type)
# set detection radius in [cm]
client.simSetDetectionFilterRadius(camera_name, image_type, 80 * 100) 
# add desired object name to detect in wild card/regex format
functions.add_mesh_filters(client, camera_name, image_type, mesh_list)

# create a small openCV window
cv2.namedWindow("AirSim", cv2.WINDOW_NORMAL)
cv2.resizeWindow("AirSim", 720, 480)

temp_dir = os.path.join(tempfile.gettempdir(), "dataset_images")
print("Images will be saved to %s" % temp_dir)
                                 
image_counter = 0
DATASET_LENGTH = 500
try:
    os.makedirs(temp_dir)
except OSError:
    if not os.path.isdir(temp_dir):
        raise

# Instantiate object pool and define placement box
object_pool = functions.generate_object_pool(client, obj_list)
print("OBJECT POOL: ")
print(object_pool)
# 1500 of each object x 14 models = 21,000 total objects / 7 objects per image = 3,000 images for dataset
MAX_OBJ_NUM = 5
first_corner = (-40, -80)
second_corner = (-60, -105)  # change this

# set starting camera above objects
client.simSetCameraPose(camera_name, camera_pose)

while True and image_counter < DATASET_LENGTH:      # this needs to get changed to finish when all objs_nums have 0
    rawImage = client.simGetImage(camera_name, image_type)
    if not rawImage:
        continue
    png = cv2.imdecode(airsim.string_to_uint8_array(rawImage), cv2.IMREAD_UNCHANGED)

    # randomly pick floor material
    functions.set_random_floor(client, floor_objs, floor_materials)
    
    cv2.imshow("AirSim", png)
    
    objects = client.simGetDetections(camera_name, image_type)  # meshes not getting detected occurs here !!! but why ??
    if objects and len(objects) == MAX_OBJ_NUM:     # FIXES BUG WHERE SOME OBJECTS W/OUT BBOX GETS SAVED
        # save bounding box info to .txt file for all objects in frame
        # functions.save_box_info(objects, image_counter, png, IMG, temp_dir)
        # snap pic
        functions.save_frame(png, image_counter, temp_dir, objects, IMG)
        # decrement count from num_objs
        functions.decrement_count(objects, num_objs)
        image_counter += 1

    functions.reset_objects_to_origin(object_pool, client)

    functions.move_cam(cam_quarter, camera_name, ranges, client)

    functions.place_objects_randomly(object_pool, num_objs, first_corner, second_corner, MAX_OBJ_NUM, client)

    # pyautogui.press('space')


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    elif cv2.waitKey(1) & 0xFF == ord('c'):
        client.simClearDetectionMeshNames(camera_name, image_type)
        # test simGetImage vs cv2
    elif cv2.waitKey(1) & 0xFF == ord('l'):
        current_pos = client.simGetCameraInfo(camera_name)
        print(current_pos)

    time.sleep(.5)

cv2.destroyAllWindows() 

