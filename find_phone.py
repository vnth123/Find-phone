from skimage import io
import sys
import numpy as np
import math


def find_phone():
    """
    Main entry point for finding the phone coordinates in the RGB image
    This involves computing grayscale image based on image texture and intensity
    """
    texture_threshold = 5
    intensity_threshold = 80
    window_size = 5
    shift = int(window_size/2)

    phone = None
    try:
        phone = io.imread(file_path)
    except OSError:
        print ("Input image cannot be found")
        sys.exit(0)

    print ("Running sliding window on image, this can take ~30 secs. Please wait for the execution to complete")
    img_length = phone.shape[0]
    img_width = phone.shape[1]
    texture = np.zeros(shape=(img_length, img_width), dtype=np.int32)

    for row in range(0, img_length - window_size + 1):
        for col in range(0, img_width - window_size + 1):
            # For each sub image of window size, find the texture and intensity for the middle pixel of sub image
            sub_img = phone[row:row+window_size, col:col+window_size]
            texture_val = get_texture(sub_img, window_size)
            intensity_val = get_intensity(sub_img, window_size)

            # Create a gray scale image based on texture and intensity threshold
            if texture_val < texture_threshold and intensity_val < intensity_threshold:
                texture[row+shift, col+shift] = 0
            else:
                texture[row+shift, col+shift] = 255

    find_connected_components(phone, texture, window_size)


def get_texture(sub_img, window_size):
    """
    Find the texture value for the center pixel of the sub image using the
    pixel values of the pixel values in the sub image
    :param sub_img: Image of window size
    :param window_size: Size of the sub image eg: 5 * 5
    :return: Texture value of the center pixel of the window
    """
    texture_val = 0
    count = 2*(window_size*(window_size-1))
    sub_img = np.mean(sub_img, axis=2)
    for row in range(0, window_size):
        texture_val += np.sum(np.fabs(np.ediff1d(sub_img[row,:])))

    for col in range(0, window_size):
        texture_val += np.sum(np.fabs(np.ediff1d(sub_img[:col])))

    return texture_val/count


def get_intensity(sub_img, window_size):
    """
    Find the average rgb values of the center pixel of the subimage
    :param sub_img: Image of window size
    :param window_size: Size of the subimage eg: 5 * 5
    :return:
    """
    row = int(window_size/2)
    col = int(window_size/2)
    return np.sum(sub_img[row, col])/3


def find_connected_components(phone_original, phone_grayscale, window_size):
    """
    Logic to find various connected components in a grayscale image
    Logic to find presence of white patch around each of the connected component to
    identify potential component as phone
    Logic to find the mid coordinate of the components that may represent a phone
    :param phone_original: ndarray of the original image
    :param phone_grayscale: ndarray of grayscale image
    :param window_size: Size of the window
    """
    phone_grayscale_copy = np.copy(phone_grayscale)
    candidate_phone_location = num_of_connected_components(phone_grayscale_copy, window_size)
    if candidate_phone_location:
        phone_location = find_white_patch(phone_original, candidate_phone_location)
        (final_x, final_y) = find_mid_coordinates(phone_grayscale, phone_location)
        norm_x = final_x / float(phone_grayscale.shape[0])
        norm_y = final_y / float(phone_grayscale.shape[1])
        print ("{0:.4f}".format(norm_y), "{0:.4f}".format(norm_x))
    else:
        print (" Sorry could not find the co-ordinates of the center of the phone")


def num_of_connected_components(img_array, window_size):
    """
    Depth first logic to find various connected components represented by pixel value of 1 in a grayscale image
    :param img_array: ndarray of grayscale image
    :param window_size: Size of the window
    :return:
    """
    length = len(img_array)
    width = len(img_array[0])
    shift = int(window_size/2)

    # List of black patches and their coordinate information
    black_components = []
    for row in range(shift, length-window_size+1):
        for col in range(shift, width-window_size+1):
            if img_array[row, col] == 0:
                component_size = dfs(img_array, length, width, row, col, window_size, shift, 0)
                component = (row, col)
                component += (component_size,)
                black_components.append(component)

    if len(black_components) == 0:
        return

    # Pick a black patch that has max component size
    max_component_size_entry = max(black_components, key=lambda x: x[2])

    # Remove all black patches that are not of significant size
    prominent_black_components = []
    if len(black_components) > 1:
        for component in black_components:
            component_size = component[2]
            if 50 < component_size < 500:
                prominent_black_components.append(component)

    if len(prominent_black_components) == 0:
        return [max_component_size_entry]
    return prominent_black_components


# Recursive DFS to find connected components that are represented by pixel value of 1
def dfs(img_array, length, width, x, y, window_size, shift, component_size):
    if img_array[x, y] == 255:
        return component_size
    img_array[x, y] = 255
    component_size += 1

    if x > shift:
        component_size = dfs(img_array, length, width, x-1, y, window_size, shift, component_size)
    if x != length-window_size+1:
        component_size = dfs(img_array, length, width, x+1, y, window_size, shift, component_size)
    if y > shift:
        component_size = dfs(img_array, length, width, x, y-1, window_size, shift, component_size)
    if y != width-window_size+1:
        component_size = dfs(img_array, length, width, x, y+1, window_size, shift, component_size)

    return component_size


def find_white_patch(original_img_array, candidate_phone_location):
    """
    Logic to find presence of white patch starting from (x, y) pixel coordinates and going
    in all four direction (top, down, left and right) in the original image
    :param original_img_array: ndarray of original image
    :param candidate_phone_location: List of (x,y) pixel coordinates of potential phone location
    :return: (x, y) - pixel coordinates that has white patch in maximum number of direction
    """
    white_patch_th = 120
    phone_loc_with_white_patch = []
    for loc in candidate_phone_location:
        x = loc[0]
        y = loc[1]
        try:
            bottom = None
            for i in range(x, x+20):
                rgb_avg = np.sum(original_img_array[i, y])/3
                if rgb_avg > white_patch_th:
                    bottom = (i, y)
                    break
        except IndexError:
            bottom = None

        try:
            right = None
            for i in range(y, y+20):
                rgb_avg = np.sum(original_img_array[x, i])/3
                if rgb_avg > white_patch_th:
                    right = (x, i)
                    break
        except IndexError:
            right = None

        try:
            top = None
            for i in range(x, x-20, -1):
                rgb_avg = np.sum(original_img_array[i, y])/3
                if rgb_avg > white_patch_th:
                    top = (i, y)
                    break
        except IndexError:
            top = None

        try:
            left = None
            for i in range(y, y-20, -1):
                rgb_avg = np.sum(original_img_array[x, i])/3
                if rgb_avg > white_patch_th:
                    left = (x, i)
                    break
        except IndexError:
            left = None

        non_nones = 0
        if bottom is not None:
            non_nones += 1
        if right is not None:
            non_nones += 1
        if top is not None:
            non_nones += 1
        if left is not None:
            non_nones += 1

        phone_loc_with_white_patch.append((x, y, non_nones))

    max_entry = max(phone_loc_with_white_patch, key=lambda x: x[2])
    return max_entry


def find_mid_coordinates(img_array, phone_loc):
    """
    Finding the approximate middle coordinates of the phone by identify the
    center of the black patch starting from (x, y) phone_loc in grayscale image
    :param img_array: ndarry of grayscale image
    :param phone_loc: (x, y) - corner pixel coordinates of a black patch representing phone
    :return: (x,y) - approximate middle coordinates values
    """
    x = phone_loc[0]
    y = phone_loc[1]
    top = (x,y)
    bottom = (x,y)

    try:
        while img_array[x, y] == 0:
            x += 1
        bottom = (x-1, y)
    except IndexError:
        bottom = (x-1, y)

    try:
        x = (top[0] + bottom[0])/2
        y = bottom[1]
        left = (x, y)
        while img_array[x, y] == 0:
            y -= 1
        left = (x, y + 1)
    except IndexError:
        left = (x, y + 1)

    try:
        x = (top[0] + bottom[0])/2
        y = bottom[1]
        right = (x, y)
        while img_array[x, y] == 0:
            y += 1
        right = (x, y - 1)
    except IndexError:
        right = (x, y - 1)

    final_x = int(top[0] + bottom[0] + right[0] + left[0])/4
    final_y = int(top[1] + bottom[1] + right[1] + left[1])/4
    return (final_x, final_y)


file_path = sys.argv[1]
find_phone()

