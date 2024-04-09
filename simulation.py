import pygame
import sys
import threading
import time
import random

# Global Constants
FPS = 1000  # Frames per second
DELAY_TIME = 1000
MIN_GREEN_TIME = 5  # Minimum green time for each signal
YELLOW_TIME = 3  # Yellow time for each signal after green
SWITCH_DELAY = 2  # Delay before switching to the next green light (all signals are red)
TRAFFIC_DENSITY = 5  # Default traffic density
SIMULATION_SPEED = 1  # Default simulation speed

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

    def update(self):
        """Update the vehicle's position and speed."""

        if self.speed < speeds[self.vehicle_type]:
            self.speed += self.acceleration * 2 * self.simulation_speed

        self.get_vehicle_in_front()

        # If a vehicle is in front of the current vehicle, reduce the speed to avoid collision
        if self.vehicle_in_front:
            distance_to_front_vehicle = self.get_distance_to_front_vehicle()
            braking_distance = 150  # Tweak this value for smoother braking

            if distance_to_front_vehicle < 10:
                # Harsh braking when very close to the front vehicle
                self.speed = 0
            elif distance_to_front_vehicle < braking_distance:
                # Gradual deceleration when approaching the front vehicle
                self.speed *= 0.99

        if self.check_collision_with_vehicles():
            self.speed = 0

        # Move the vehicle based on the direction
        self.move()

        # Update rotated hit_box
        self._create_hit_box()

    def check_collision_with_vehicles(self):
        # Check for collision with other vehicles
        for vehicle in laneGroups[self.direction]:
            if vehicle != self:
                if self.hit_box.colliderect(vehicle.hit_box):
                    if self.get_collision_direction(vehicle) == 'front':
                        self.vehicle_in_front = vehicle
                        return True
                    else:
                        pass
        return False

    def get_distance_to_front_vehicle(self):
        # Get the distance to the vehicle in front of the current vehicle
        if self.vehicle_in_front:
            if self.direction in ['right']:
                # Calculate distance considering hit_box dimensions
                return abs(self.vehicle_in_front.x - (self.x + self.hit_box.width / 2))
            elif self.direction in ['down']:
                # Calculate distance considering hit_box dimensions
                return abs(self.vehicle_in_front.y - (self.y + self.hit_box.height / 2))
            elif self.direction in ['left']:
                # Calculate distance considering hit_box dimensions
                return abs(self.x - (self.vehicle_in_front.x + self.vehicle_in_front.hit_box.width / 2))
            elif self.direction in ['up']:
                # Calculate distance considering hit_box dimensions
                return abs(self.y - (self.vehicle_in_front.y + self.vehicle_in_front.hit_box.height / 2))
        return float('inf')  # Return infinity if there is no vehicle in front

    def move(self):
        # Move the vehicle based on the direction
        if self.direction == 'right':
            self.x += (self.speed * 2 * self.simulation_speed)
        elif self.direction == 'down':
            self.y += (self.speed * 2 * self.simulation_speed)
        elif self.direction == 'left':
            self.x -= (self.speed * 2 * self.simulation_speed)
        elif self.direction == 'up':
            self.y -= (self.speed * 2 * self.simulation_speed)

        # Update the rect attribute for collision detection
        self.rect.x = self.x
        self.rect.y = self.y

    def get_collision_direction(self, other_vehicle):
        # Get the direction of the collision with another vehicle
        if self.direction == 'right':
            if other_vehicle.x > self.x:
                return 'front'
            elif other_vehicle.x < self.x:
                return 'back'
            else:
                return 'side'
        elif self.direction == 'down':
            if other_vehicle.y > self.y:
                return 'front'
            elif other_vehicle.y < self.y:
                return 'back'
            else:
                return 'side'
        elif self.direction == 'left':
            if other_vehicle.x < self.x:
                return 'front'
            elif other_vehicle.x > self.x:
                return 'back'
            else:
                return 'side'
        elif self.direction == 'up':
            if other_vehicle.y < self.y:
                return 'front'
            elif other_vehicle.y > self.y:
                return 'back'
            else:
                return 'side'

    def check_limit(self):
        # Check if the vehicle has reached the limit
        if self.direction == 'right' and self.x > 1600:
            return True
        elif self.direction == 'down' and self.y > 1600:
            return True
        elif self.direction == 'left' and self.x < -200:
            return True
        elif self.direction == 'up' and self.y < -200:
            return True
        else:
            return False

    def get_vehicle_in_front(self):
        # Get the vehicle in front of the current vehicle (closest one)
        if self.direction == 'right':
            vehicles_in_front = [vehicle for vehicle in laneGroups[self.direction] if vehicle.x > self.x]
            if vehicles_in_front:
                self.vehicle_in_front = min(vehicles_in_front, key=lambda x: x.x)
            else:
                self.vehicle_in_front = None
        elif self.direction == 'down':
            vehicles_in_front = [vehicle for vehicle in laneGroups[self.direction] if vehicle.y > self.y]
            if vehicles_in_front:
                self.vehicle_in_front = min(vehicles_in_front, key=lambda x: x.y)
            else:
                self.vehicle_in_front = None
        elif self.direction == 'left':
            vehicles_in_front = [vehicle for vehicle in laneGroups[self.direction] if vehicle.x < self.x]
            if vehicles_in_front:
                self.vehicle_in_front = max(vehicles_in_front, key=lambda x: x.x)
            else:
                self.vehicle_in_front = None
        elif self.direction == 'up':
            vehicles_in_front = [vehicle for vehicle in laneGroups[self.direction] if vehicle.y < self.y]
            if vehicles_in_front:
                self.vehicle_in_front = max(vehicles_in_front, key=lambda x: x.y)
            else:
                self.vehicle_in_front = None


def kill_vehicle():
    """Destroy a vehicle."""
    while True:
        for direction, group in laneGroups.items():
            for vehicle in group:
                if vehicle.check_limit():
                    vehicle.kill()
                    print(f"Vehicle removed from {direction} direction")
        pygame.time.delay(500)


def initialize():
    """Initialize the simulation."""
    global signals, laneGroups

    # Initialize traffic signals
    for i in range(noOfSignals):
        signal = TrafficSignal(0, 0, MIN_GREEN_TIME)
        signals.append(signal)

    # Initialize lane groups
    for direction in directionNumbers.values():
        laneGroups[direction] = pygame.sprite.Group()


class RunSimulation:
    """Class to run the traffic simulation."""

    def __init__(self):
        """Initialize the simulation."""
        self.exit_event = threading.Event()
        initialize()

        self.thread1 = threading.Thread(name="repeat", target=self.repeat, args=(SIMULATION_SPEED,))
        self.thread1.daemon = True
        self.thread1.start()

        self.thread2 = threading.Thread(name="kill vehicles", target=kill_vehicle)
        self.thread2.daemon = True
        self.thread2.start()

    def repeat(self, simulation_speed):
        global currentGreen, currentYellow, nextGreen
        last_time = pygame.time.get_ticks()

        while not self.exit_event.is_set():
            dt = pygame.time.get_ticks() - last_time
            dt_seconds = dt / 1000  # Convert milliseconds to seconds
            last_time = pygame.time.get_ticks()

            signals[currentGreen].remaining_green_time -= simulation_speed * dt_seconds
            nextGreen = (currentGreen + 1) % noOfSignals

            if signals[currentGreen].remaining_green_time < 0 and currentYellow == 0:
                signals[currentGreen].remaining_green_time = 0
                currentYellow = 1
                signals[currentGreen].remaining_yellow_time = YELLOW_TIME  # Reset yellow time

            if currentYellow == 1:
                signals[currentGreen].remaining_yellow_time -= simulation_speed * dt_seconds

            if signals[currentGreen].remaining_yellow_time < 0 and currentYellow == 1:
                currentYellow = 0
                signals[currentGreen].remaining_yellow_time = 0

                currentGreen = -1
                pygame.time.delay(int(DELAY_TIME / simulation_speed))

                currentGreen = nextGreen
                green_time = MIN_GREEN_TIME + 1
                signals[currentGreen].remaining_green_time = green_time / simulation_speed

            pygame.time.delay(int(DELAY_TIME / simulation_speed))

    def spawn_vehicle(self):
        """Spawn a vehicle."""
        direction = random.choice(list(directionNumbers.values()))
        vehicle_type = random.choice(list(vehicleTypes.values()))
        vehicle = Vehicle(vehicle_type, 0, direction, 1, self)
        vehicle.spawn_time = time.time()  # Update spawn time
        laneGroups[direction].add(vehicle)  # Add the vehicle to the lane group

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

        # Spawn vehicles at the start of simulation
        self.spawn_vehicle()

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

            # Update and draw vehicles
            for direction, group in laneGroups.items():
                for vehicle in group:
                    vehicle.update()
                    screen.blit(vehicle.image, (vehicle.x, vehicle.y))

            # Spawn a new vehicle with a certain probability
            if random.random() < TRAFFIC_DENSITY / FPS:
                self.spawn_vehicle()

            # Update the display
            pygame.display.flip()

            # Cap the frame rate
            clock.tick(FPS)


if __name__ == "__main__":
    simulation = RunSimulation()
    simulation.run()