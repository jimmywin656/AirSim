import airsim
import cv2
import math
import os
import random
import re

# Define dict of all object regex to class IDs
regex_to_class_id = {
    r'SK_.*': "0",
    r'football.*': "1",
    r'Wilson_.*': "2",
    r'Matress.*': "3",
    r'Baseball.*': "4",
    r'luggage.*': "5",
    r'Black_Umbrella.*': "6",
    r'volleyball.*': "7",
    r'tenis_.*': "8",
    r'Stop_.*': "9",
    r'motorcycle.*': "10",
    r'Default_.*': "11",
    r'small_boat_.*': "12",
    r'Basketball_.*': "13"
}

# used for positioning CAMERA not objects
def get_random_coords(x_range, y_range, z_range):
    random_x = random.randint(*x_range)
    random_y = random.randint(*y_range)
    random_z = random.randint(*z_range)
    return random_x, random_y, random_z

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

# OLD PLACE_OBJECTS FUNCTION
# def place_objects_randomly(object_pool, first_corner, second_corner, max_num, client):
#     # randomly select max_num objects from pool
#     selected_objects = random.sample(object_pool, min(max_num, len(object_pool)))
#     # empty list of poses (object locations)
#     random_locations = []

#     for obj in selected_objects:
#         # get valid position
#         position = get_valid_position(first_corner, second_corner, random_locations, min_distance=6)
#         orientation = get_random_rotation()
#         # add to random_locations list
#         random_locations.append(position)
#         # before adding pose to list of locations, check to make sure they are far enough apart from each other
#         object_pose = airsim.Pose(position, orientation)
#         client.simSetObjectPose(obj, object_pose, True)

# NEW PLACE_OBJECTS FUNCTION
def place_objects_randomly(object_pool, num_objs, first_corner, second_corner, max_num, client):
    # hold names of objs that should be rotated differently
    # currently: boat (test out other models first), stop sign, maybe umbrella
    DIFF_ROTATIONS = []
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
        for pattern in num_objs:    # pattern is just the regex key
            if re.match(pattern, obj_name):
                if num_objs[pattern] > 0:
                    # get valid position
                    position = get_valid_position(first_corner, second_corner, random_locations, min_distance=6)    # tweak min_distance to separate objects
                    orientation = get_random_rotation()     # bug where objects that are rotated (stop sign, etc...) get rotated and are not in ideal rotation
                    # add to random_locations list
                    random_locations.append(position)
                    # before adding pose to list of locations, check to make sure they are far enough apart from each other
                    object_pose = airsim.Pose(position, orientation)             
                    client.simSetObjectPose(obj_name, object_pose, True)

                    # decrement count from pattern's total
                    num_objs[pattern] -= 1
                    # print(f"Placed {obj_name}. Remaining: {num_objs[pattern]}")

def move_cam(cam_quarter, camera_name, ranges, client):
    # move camera randomly
    random_x, random_y, random_z = get_random_coords(ranges[0], ranges[1], ranges[2])
    camera_pose = airsim.Pose(
        airsim.Vector3r(random_x, random_y, random_z),
        cam_quarter
    )
    client.simSetCameraPose(camera_name, camera_pose)

def save_box_info(objects, counter, png, img, temp_dir):
    class_id = "#"
    if objects:
        bbox_path = os.path.join(temp_dir, f"detection_{counter}.txt")
        with open(bbox_path, 'w') as f:
            for obj in objects:
                x_min, y_min = int(obj.box2D.min.x_val), int(obj.box2D.min.y_val)
                x_max, y_max = int(obj.box2D.max.x_val), int(obj.box2D.max.y_val)
                # print(f"min: ({x_min}, {y_min}), max: ({x_max}, {y_max})")

                # yolo format: x_center, y_center, width, height
                x_center = ((x_min + x_max) / 2) / img.get('width')
                y_center = ((y_min + y_max) / 2) / img.get('height')
                width = (x_max - x_min) / img.get('width')     # divide by width to normalize
                height = (y_max - y_min) / img.get('height')

                # print(IMG_WIDTH, IMG_HEIGHT)
                for regex, cid in regex_to_class_id.items():
                    if re.match(regex, obj.name):
                        class_id = cid
                        break  

                # f.write(f"{class_id} {x_min} {y_min} {x_max} {y_max}\n")
                f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")

                # Draw the bounding box on the image
                cv2.rectangle(png, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)  # Blue color with thickness of 2
            print(f"Saved detection info to {bbox_path}")

def save_frame(png, counter, temp_dir):
    image_path = os.path.join(temp_dir, f"frame_{counter}.png")
    cv2.imwrite(image_path, png)

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
