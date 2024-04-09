import pygame
import sys

# Global Constants
FPS = 60  # Frames per second
DELAY_TIME = 1000
MIN_GREEN_TIME = 5  # Minimum green time for each signal
YELLOW_TIME = 3  # Yellow time for each signal after green
SWITCH_DELAY = 2  # Delay before switching to the next green light (all signals are red)
TRAFFIC_DENSITY = 0.3  # Default traffic density

# Global Variables
signals = []  # List to store traffic signals
laneGroups = {}  # Dictionary to store vehicles in each lane
currentGreen = 0  # Index indicating which signal is currently green
nextGreen = 0  # Index indicating which signal will turn green next
currentYellow = 0  # Indicates whether yellow signal is on or off
vehicleTypes = {0: 'car', 1: 'truck', 2: 'taxi', 3: 'bike'}  # Types of vehicles
directionNumbers = {0: 'down', 1: 'left', 2: 'up', 3: 'right'}  # Directions of vehicles
acceleration = {'car': 0.0005, 'truck': 0.0003, 'taxi': 0.0005, 'bike': 0.0008}  # Acceleration of vehicles
x = {'right': [-400], 'down': [625], 'left': [1800], 'up': [709]}  # X-coordinates of vehicles' start
y = {'right': [510], 'down': [-400], 'left': [420], 'up': [1400]}  # Y-coordinates of vehicles' start
speeds = {'car': 0.3, 'truck': 0.29, 'taxi': 0.32, 'bike': 0.35}  # speeds of vehicles
stopLines = {'right': 480, 'down': 280, 'left': 920, 'up': 720}  # Stop lines for vehicles
defaultStop = {'right': 570, 'down': 360, 'left': 840, 'up': 638}  # Threshold for vehicles to cross the intersection
noOfSignals = 4  # Number of traffic signals
signalCords = [(572, 340), (770, 375), (795, 535), (535, 590)]  # Coordinates for signals
