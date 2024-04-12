import cv2
import dlib
import numpy as np
import socket
import time
from threading import Timer


# Load YOLOv4 model
net = cv2.dnn.readNet('yolov4-tiny.weights', 'yolov4-tiny.cfg')
classes = []  # List to store the class names for detected objects
with open('classes.txt', 'r') as f:
    classes = f.read().splitlines()  # Read class names from file and store them in the list 

video = cv2.VideoCapture('videos/1.mp4')  # Video feed (change with file name)


WIDTH = 1280  # Width of the video frame
HEIGHT = 720  # Height of the video frame
SELECTION_POINTS = []  # List to store the selected points for region of interest


def mouse_callback(event, x, y, flags, params):
    """
    Callback function for mouse events. Utilitary function.
    
    Parameters:
    event, x, y, flags, params: Parameters provided by OpenCV for mouse events.
    """
    points = params['points']
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append((x, y))
            cv2.circle(params['selection_image'], (x, y), 5, (0, 255, 0), -1)
            cv2.imshow('selection', params['selection_image'])


def select_ROI():
    """
    Selects a Region of Interest (ROI) by allowing the user to click points on the image.
    
    Returns:
    np.array: The array containing the selected points defining the ROI.
    """
    _, frame = video.read()
    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    selection_image = frame.copy()
    cv2.imshow('selection', frame)
    points = []
    cv2.setMouseCallback('selection', mouse_callback, {'selection_image': selection_image, 'points': points})
    while True:
        if len(points) == 4:
            break
        if cv2.waitKey(33) == 27:
            break
    cv2.destroyAllWindows()
    return np.array(points, np.int32)


def sendCounter(counter):
    """
    Sends the counter value to a specified IP address and port using a TCP socket connection.
    
    Parameters:
    counter (int): The counter value to be sent.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("10.0.0.9", 5000))  # Change with your own server's Ip address
    message = str(counter)
    s.send(bytes(message, "utf-8"))
    time.sleep(1)
    s.close()


def detectCars(img):
    """
    Detects cars (and other vehicles) in the input image using the YOLOv4 model. 
     
    Parameters:
    img (numpy.ndarray): The input image.
    
    Returns:
    list: A list of bounding boxes containing the coordinates (x, y, width, height) of the detected cars.
    """
    blob = cv2.dnn.blobFromImage(img, 1/255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    output_layers_names = net.getUnconnectedOutLayersNames()
    layerOutputs = net.forward(output_layers_names)
    boxes = []
    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            # 0 for person, 1 for bicycle, 2 for car, 3 for motorbike, and 5 for bus
            if confidence > 0.5 and class_id in [0, 1, 2, 3, 5]:
                center_x = int(detection[0] * WIDTH)
                center_y = int(detection[1] * HEIGHT)
                w = int(detection[2] * WIDTH)
                h = int(detection[3] * HEIGHT)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
    return boxes


def calculateCenter(carTracker, car):
    """
    Calculate the center coordinates of a tracked car's bounding box.
    
    Parameters:
        carTracker (dict): Dictionary containing trackers for each car.
        car: Car information containing the tracker and its bounding box.
    
    Returns:
        tuple: A tuple containing the x and y coordinates of the center.
    """
    trackedPosition = car['tracker'].get_position()
    t_x = int(trackedPosition.left())
    t_y = int(trackedPosition.top())
    t_w = int(trackedPosition.width())
    t_h = int(trackedPosition.height())
    t_x_bar = t_x + 0.5 * t_w
    t_y_bar = t_y + 0.5 * t_h
    return t_x_bar, t_y_bar, t_x, t_y, t_w, t_h


def trackCarsInROI(SELECTION_POINTS, image, carTracker, carLoc1, currentCar):
    """
    Track cars within the region of interest (ROI) defined by SELECTION_POINTS.

    Parameters:
    SELECTION_POINTS (numpy.ndarray): The points defining the ROI.
    image (numpy.ndarray): The input image.
    carTracker (dict): Dictionary to store trackers for each car.
    carLoc1 (dict): Dictionary to store initial locations of tracked cars.
    currentCar (int): Current ID to assign to new cars.

    Returns:
    dict: Updated carTracker.
    dict: Updated carLoc1.
    int: Updated currentCar.
    """
    cars = detectCars(image)
    for (x, y, w, h) in cars:
        # Calculate center of the car
        center_x = x + w // 2
        center_y = y + h // 2
        # Check if center of the car lies inside the area
        if cv2.pointPolygonTest(SELECTION_POINTS, (center_x, center_y), False) >= 0:
            matchCar = None
            # Track known car
            for carID, carData in carTracker.items():
                t_x_bar, t_y_bar, t_x, t_y, t_w, t_h = calculateCenter(carTracker, carData)
                if ((t_x <= center_x <= (t_x + t_w)) and (t_y <= center_y <= (t_y + t_h)) and (
                        x <= t_x_bar <= (x + w)) and (y <= t_y_bar <= (y + h))): 
                    matchCar = carID
                    break
            # Track new car
            if matchCar is None:
                tracker = dlib.correlation_tracker()
                tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))
                carTracker[currentCar] = {'tracker': tracker, 'location': [x, y, w, h]}
                carLoc1[currentCar] = [x, y, w, h]
                currentCar += 1
    return carTracker, carLoc1, currentCar


def trackMultipleCars(SELECTION_POINTS):
    """
    Tracks for each video frame multiple cars within ROI using YOLOv4 and tracking them with dlib.
    
    Parameters:
    SELECTION_POINTS (numpy.ndarray): The points defining the ROI.
    """
    frameCounter = 0
    currentCar = 0
    countedCars = set()  # Set to keep track of cars that have already been counted
    carCounter = 0  # Counter for cars within the ROI
    carTracker = {}  # Dictionary to store trackers for each car
    carLoc1 = {}  # Dictionary to store initial locations of tracked cars
    carLoc2 = {}  # Dictionary to store updated locations of tracked cars

    while True:
        rc, image = video.read()
        if not rc:
            break
        image = cv2.resize(image, (WIDTH, HEIGHT))
        resultImage = image.copy()
        frameCounter += 1
        carToDelete = []

        # Update tracking for existing cars
        for carID, carData in carTracker.items():
            if carData['tracker'].update(image) < 9:
                carToDelete.append(carID)

        # Remove cars from tracking
        for carID in carToDelete:
            carTracker.pop(carID, None)
            carLoc1.pop(carID, None)
            carLoc2.pop(carID, None)
            if carID in countedCars:
                carCounter -= 1
                countedCars.remove(carID)

        # Track every 30 frames
        if frameCounter % 30 == 0:
            carTracker, carLoc1, currentCar = trackCarsInROI(SELECTION_POINTS, image, carTracker, carLoc1, currentCar)

        # Draw area outline
        cv2.polylines(resultImage, [SELECTION_POINTS.reshape((-1, 1, 2))], True, (0, 0, 255), 2)

        # Extract the position from the tracker for each car
        for carID, carData in carTracker.items():
            t_x_bar, t_y_bar, t_x, t_y, t_w, t_h = calculateCenter(carTracker, carData)

            # Check if car is inside the area and display rectangle
            if cv2.pointPolygonTest(SELECTION_POINTS, (t_x + t_w/2, t_y + t_h/2), False) >= 0 and carID not in countedCars:
                carCounter += 1
                countedCars.add(carID)
            cv2.rectangle(resultImage, (t_x, t_y), (t_x + t_w, t_y + t_h), (0, 255, 0), 4)

        # Display counter
        cv2.putText(resultImage, f'Cars in line: {carCounter}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Send it to server
        Timer(1, sendCounter, args=(carCounter,)).start()
        cv2.imshow('result', resultImage)
        
        if cv2.waitKey(33) == 27:
            break
    cv2.destroyAllWindows()


if __name__ == '__main__':
    SELECTION_POINTS = select_ROI()
    trackMultipleCars(SELECTION_POINTS)
