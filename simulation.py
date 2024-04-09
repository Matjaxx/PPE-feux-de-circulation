import pygame
import sys
import threading
import time

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

# Load images
car_image = pygame.image.load('images/vehicles/car.png')
truck_image = pygame.image.load('images/vehicles/truck.png')
taxi_image = pygame.image.load('images/vehicles/taxi.png')
bike_image = pygame.image.load('images/vehicles/bike.png')
red_signal_image = pygame.image.load('images/signals/red.png')
yellow_signal_image = pygame.image.load('images/signals/yellow.png')
green_signal_image = pygame.image.load('images/signals/green.png')
intersection_image = pygame.image.load('images/intersection.png')


class TrafficSignal:
    """Class to represent a traffic signal."""

    def __init__(self, red, yellow, green):
        """Initialize the traffic signal."""
        self.red = red
        self.yellow = yellow
        self.green = green
        self.remaining_green_time = green
        self.remaining_yellow_time = YELLOW_TIME
        self.remaining_switch_time = SWITCH_DELAY
        self.signal_status = 'green' if green > 0 else 'yellow' if yellow > 0 else 'red'
        self.signalText = (
            f"Green ({green})" if green > 0 else f"Yellow ({yellow})" if yellow > 0 else f"Red ({red})"
        )
        self.vehicles_in_front = 0


class Vehicle(pygame.sprite.Sprite):
    """Class to represent a vehicle."""

    def __init__(self, vehicle_type, direction_number, direction, simulation_speed, simulation_instance):
        """Initialize the vehicle."""
        super().__init__()
        self.simulation_instance = simulation_instance
        self.flag = False
        self.simulation_speed = simulation_speed
        self.cross_time = None
        self.spawn_time = time.time()
        self.hit_box = None
        self.direction_number = direction_number
        self.vehicle_type = vehicle_type
        self.crossed = False
        self.acceleration = acceleration[vehicle_type]
        self.vehicle_in_front = None

        # Load vehicle image based on the type
        if vehicle_type == 'car':
            self.image = pygame.image.load('images/vehicles/car.png')
        elif vehicle_type == 'truck':
            self.image = pygame.image.load('images/vehicles/truck.png')
        elif vehicle_type == 'taxi':
            self.image = pygame.image.load('images/vehicles/taxi.png')
        elif vehicle_type == 'bike':
            self.image = pygame.image.load('images/vehicles/bike.png')

        self.original_image = self.image  # Store the original image for rotation
        self.rect = self.image.get_rect()

        # Set the initial position based on the direction
        if direction == 'right':
            self.x = x['right'][0]
            self.y = y['right'][0]
            self.rotation = 0
        elif direction == 'down':
            self.x = x['down'][0]
            self.y = y['down'][0]
            self.rotation = 270
        elif direction == 'left':
            self.x = x['left'][0]
            self.y = y['left'][0]
            self.rotation = 180
        elif direction == 'up':
            self.x = x['up'][0]
            self.y = y['up'][0]
            self.rotation = 90

        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.direction = direction
        self.speed = speeds[vehicle_type]
        self.stop = stopLines[direction]
        self.defaultStop = defaultStop[direction]
        self.colliding = False  # Flag to indicate if a collision occurred
        self._create_hit_box()

        # Add the vehicle to the appropriate lane group
        laneGroups[self.direction].add(self)

    def _create_hit_box(self):
        # Create a hit_box based on the rotated image
        self.hit_box = self.image.get_rect()
        self.hit_box.x = self.x
        self.hit_box.y = self.y


class RunSimulation:
    """Class to run the traffic simulation."""

    def __init__(self):
        """Initialize the simulation."""
        self.initialize()

    def initialize(self):
        """Initialize the simulation."""
        global signals, laneGroups

        # Initialize traffic signals
        for i in range(noOfSignals):
            signal = TrafficSignal(0, 0, MIN_GREEN_TIME)
            signals.append(signal)

        # Initialize lane groups
        for direction in directionNumbers.values():
            laneGroups[direction] = pygame.sprite.Group()

    def run(self):
        """Run the simulation."""
        # Initialize pygame
        pygame.init()

        # Set up the screen
        screen_width = 1400
        screen_height = 1000
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Traffic Simulation")

        # Clock for controlling the frame rate
        clock = pygame.time.Clock()

        # Main simulation loop
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Clear the screen
            screen.fill((255, 255, 255))

            # Draw intersection image
            screen.blit(intersection_image, (0, 0))

            # Draw traffic lights
            for i in range(0, noOfSignals):
                rotated_signal = pygame.transform.rotate(red_signal_image, i * 90)
                if i == currentGreen:
                    if currentYellow == 1:
                        rotated_signal = pygame.transform.rotate(yellow_signal_image, i * 90)
                    else:
                        # Adjust the rotation angle for signals 0 and 2
                        rotated_signal = pygame.transform.rotate(green_signal_image, (i + 2) % noOfSignals * 270)
                else:
                    # Adjust the rotation angle for signals 0 and 2
                    rotated_signal = pygame.transform.rotate(red_signal_image, (i + 2) % noOfSignals * 270)
                screen.blit(rotated_signal, signalCords[i])

            # Update the display
            pygame.display.flip()

            # Cap the frame rate
            clock.tick(FPS)


if __name__ == "__main__":
    simulation = RunSimulation()
    simulation.run()
