# Find-phone

Visual object detection system: The task is to find a location of a phone dropped on the floor from a single RGB camera image. There is only one type of phone that is of interest.

Consider a normalized XY-coordinate system for an image. Left-top corner of the image is defined as (x, y) = (0, 0), left-bottom as (x, y) = (0, 1), right-top as (x, y) = (1, 0), and finally right-bottom corner as (x, y) = (1, 1). The “phone detector” has to find normalized coordinates of the center of the phone. In the example above, the coordinates of the phone are approximately (x, y) = (0.26, 0.80). Every image contains a phone.

A small labeled dataset can be found in find_phone_data folder. A dataset consists of approximately 100 jpeg images of the floor from the factory building with a phone on it. There is
a file named labels.txt that contains normalized coordinates of a phone for each picture.
Each line of the labels.txt is composed of img_path,x,yseparated by spaces:

img_path,x(coordinate of the phone), y(coordinate of the phone)
Here is an example of the first 3 lines from labels.txt:

    51.jpg 0.2388 0.6012
    95.jpg 0.2551 0.3129
    84.jpg 0.7122 0.7117
    
The find_phone.py takes a single command line argument which is a path to the jpeg image to be tested. This script will print the normalized coordinates of the phone detected on the image in the format shown below. 

Here is what a terminal command will look like. 

    > python find_phone.py ~/find_phone_data/51.jpg
      0.2551 0.3129
 
### Solution: 
    The solution uses a traditional image processing technique to detect the image in the photo and its corresponding center coordinates. 

### Evaluation Criteria: 
    A phone is considered to be detected correctly on an image if the output is within a radius of 0.05 (normalized distance) centered on the phone


