import random
import time
import threading
import pygame
import sys

# Constants
FPS = 500
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
total_crossed_vehicles = 0  # Total number of crossed vehicles
vehicle_counter = 0  # Counter for total spawned vehicles
vehicle_spawned_counter = 0  # Counter for vehicles spawned in the simulation
vehicle_kill_counter = 0  # Counter for vehicles kill in the simulation
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

    # return the vehicle which is in front of the current vehicle
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

    def check_reach_stop_line(self):
        # Determine if the vehicle has reached the stop line:
        if self.direction == 'right' and self.x + self.hit_box.width >= stopLines[self.direction]:
            return True
        elif self.direction == 'down' and self.y + self.hit_box.height >= stopLines[self.direction]:
            return True
        elif self.direction == 'left' and self.x <= stopLines[self.direction]:
            return True
        elif self.direction == 'up' and self.y <= stopLines[self.direction]:
            return True

    def check_crossed(self):
        # Determine if the vehicle has crossed the intersection (default stop line):
        if self.direction == 'right' and self.x + self.hit_box.width > defaultStop[self.direction]:
            return True
        elif self.direction == 'down' and self.y + self.hit_box.height > defaultStop[self.direction]:
            return True
        elif self.direction == 'left' and self.x < defaultStop[self.direction]:
            return True
        elif self.direction == 'up' and self.y < defaultStop[self.direction]:
            return True

    def update(self):
        global total_crossed_vehicles

        if self.check_reach_stop_line() and self.crossed is False:
            if self.direction_number != currentGreen:
                # Harsh braking when reaching a red signal at the stop line
                self.speed *= 0.99
                # If the signal is red, stop the vehicle just before the default stop line
                if self.direction == 'right' and self.x + self.hit_box.width > defaultStop[self.direction]:
                    self.x = defaultStop[self.direction] - self.hit_box.width
                elif self.direction == 'down' and self.y + self.hit_box.height > defaultStop[self.direction]:
                    self.y = defaultStop[self.direction] - self.hit_box.height
                elif self.direction == 'left' and self.x < defaultStop[self.direction]:
                    self.x = defaultStop[self.direction]
                elif self.direction == 'up' and self.y < defaultStop[self.direction]:
                    self.y = defaultStop[self.direction]
            else:
                # Adjust the speed based on acceleration
                if self.speed < speeds[self.vehicle_type]:
                    self.speed += self.acceleration * 2 * self.simulation_speed
        else:
            # If not at the stop line or the signal is green, keep moving
            # Adjust the speed based on acceleration
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

        # Check if the vehicle has crossed the intersection
        if self.check_crossed() and self.crossed is False:
            self.crossed = True
            self.simulation_instance.total_crossed_vehicles += 1

            self.cross_time = time.time()
            # Check for collision with other vehicles
        if self.check_collision_with_vehicles():
            self.speed = 0

        # Move the vehicle based on the direction
        self.move()

        # Update rotated hit_box
        self._create_hit_box()

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


def repeat(simulation_instance, simulation_speed):
    global currentGreen, nextGreen, currentYellow
    last_time = pygame.time.get_ticks()

    while not simulation_instance.exit_event.is_set():
        dt = pygame.time.get_ticks() - last_time
        dt_seconds = dt / 1000  # Convert milliseconds to seconds
        last_time = pygame.time.get_ticks()

        signals[currentGreen].remaining_green_time -= simulation_speed * dt_seconds

        if simulation_instance.traffic_light_policy == "optimal":
            nextGreen = signals.index(max(signals, key=lambda x: x.vehicles_in_front))
        else:  # Random traffic light policy
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

            if simulation_instance.traffic_light_policy == "optimal":
                signals[currentGreen].remaining_green_time = max(MIN_GREEN_TIME + 1,
                                                                 signals[currentGreen].vehicles_in_front / 2)
            else:  # Random traffic light policy
                signals[currentGreen].remaining_green_time = MIN_GREEN_TIME + 1

        pygame.time.delay(int(DELAY_TIME / simulation_speed))


def generateVehicles(simulation_instance, simulation_speed, trafficDensity, direction_priority):
    global vehicle_counter, vehicle_spawned_counter
    while not simulation_instance.exit_event.is_set():
        # Randomly select a vehicle type and direction
        vehicle_type = vehicleTypes[random.randint(0, 3)]

        # Randomly select a vehicle type based on the direction priority
        direction_number = random.choices(population=[0, 1, 2, 3], weights=direction_priority, k=1)[0]
        direction = directionNumbers[direction_number]

        # Create a vehicle object
        new_vehicle = Vehicle(vehicle_type, direction_number, direction, simulation_speed, simulation_instance)

        # Check if there are existing vehicles on the lane
        if len(laneGroups[direction]) > 0:
            # Get the last vehicle on the lane based on his direction and current coords
            last_vehicle = laneGroups[direction].sprites()[-1]

            # Set the spawn position behind the last vehicle based on the direction with a distance
            if direction == 'right':
                new_vehicle.x = last_vehicle.x - new_vehicle.hit_box.width - random.randint(100, 200)
            elif direction == 'down':
                new_vehicle.y = last_vehicle.y - new_vehicle.hit_box.height - random.randint(100, 200)
            elif direction == 'left':
                new_vehicle.x = last_vehicle.x + last_vehicle.hit_box.width + random.randint(100, 200)
            elif direction == 'up':
                new_vehicle.y = last_vehicle.y + last_vehicle.hit_box.height + random.randint(100, 200)

        simulation_instance.add(new_vehicle)
        vehicle_counter += 1
        vehicle_spawned_counter += 1
        time.sleep(1 / (simulation_speed * 3 * trafficDensity))  # Adjusted delay based on simulation speed


def destroy_vehicle(simulation_speed, simulation_instance):
    global vehicle_kill_counter
    while not simulation_instance.exit_event.is_set():
        for vehicle in simulation_instance.simulation:
            if vehicle.check_limit():
                vehicle.kill()
                vehicle_kill_counter += 1
        time.sleep(1 / simulation_speed)


class RunSimulation:
    def __init__(self, total_vehicles_to_cross, simulation_speed, trafficDensity, direction_priority,
                 traffic_light_policy):
        global total_crossed_vehicles
        pygame.init()  # Initialize pygame
        self.traffic_light_policy = traffic_light_policy
        self.direction_priority = direction_priority
        self.simulation = pygame.sprite.Group()
        self.total_time = 0
        self.average_waiting_time = 0
        self.min_waiting_time = 0
        self.max_waiting_time = 0

        # Flag to toggle debug mode
        self.debug_mode = False

        self.exit_event = threading.Event()
        self.total_vehicles_to_cross = total_vehicles_to_cross
        self.simulation_speed = simulation_speed
        # Initialize a clock object to control the frame rate
        self.clock = pygame.time.Clock()
        self.crossing_times = []  # Initialize crossing times list

        self.total_crossed_vehicles = 0
        self.crossing_times = []  # Initialize crossing times list

        # Variable to track the total number of crossed vehicles
        self.total_crossed_vehicles = 0

        self.initialize()

        self.thread1 = threading.Thread(name="generate_vehicles", target=generateVehicles,
                                        args=(self, self.simulation_speed, trafficDensity, self.direction_priority))
        self.thread1.daemon = True
        self.thread1.start()

        self.thread2 = threading.Thread(name="kill_and_replace", target=destroy_vehicle,
                                        args=(self.simulation_speed, self,))
        self.thread2.daemon = True
        self.thread2.start()

        self.thread3 = threading.Thread(name="repeat", target=repeat, args=(self, simulation_speed))
        self.thread3.daemon = True
        self.thread3.start()

        # Set up pygame
        pygame.init()

        # Define colors and screen size
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.screenWidth = 1400
        self.screenHeight = 1000
        self.screenSize = (self.screenWidth, self.screenHeight)

        # Load background image and set up display
        self.background = pygame.image.load('images/intersection.png')
        self.screen = pygame.display.set_mode(self.screenSize)
        pygame.display.set_caption("SIMULATION")

        # Set up font
        self.font = pygame.font.Font(None, 30)
        self.run()

    def add(self, vehicle):
        self.simulation.add(vehicle)

    def reset_simulation(self):
        global total_crossed_vehicles, signals, vehicle_counter, vehicle_spawned_counter, vehicle_kill_counter
        # kill all threads
        # Set the exit event to signal threads to exit
        self.exit_event.set()

        # Wait for threads to finish
        self.thread1.join()
        self.thread2.join()
        self.thread3.join()

        # Reset the exit event
        self.exit_event.clear()

        total_crossed_vehicles = 0
        self.simulation.empty()
        signals.clear()
        vehicle_counter = 0
        vehicle_spawned_counter = 0
        vehicle_kill_counter = 0
        self.initialize()  # Reinitialize signals
        for direction in laneGroups:
            laneGroups[direction].empty()
        # Recreate laneGroups for each direction
        laneGroups['right'] = pygame.sprite.Group()
        laneGroups['down'] = pygame.sprite.Group()
        laneGroups['left'] = pygame.sprite.Group()
        laneGroups['up'] = pygame.sprite.Group()
        # Recreate signals with initial values
        for i in range(0, noOfSignals):
            signals.append(TrafficSignal(10, 3, 5))
        self.exit_event.clear()
        pygame.quit()

    def toggle_debug_mode(self):
        self.debug_mode = not self.debug_mode

    def run(self):
        while self.total_crossed_vehicles < self.total_vehicles_to_cross:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F10:
                        self.toggle_debug_mode()

            self.screen.blit(self.background, (0, 0))

            if self.debug_mode:
                # Display total crossed vehicles in the top left corner
                crossed_text = f"DEBUG SIMULATION"
                crossed_text_surface = self.font.render(crossed_text, True, self.white, self.black)
                self.screen.blit(crossed_text_surface, (10, 10))
                # Display total crossed vehicles in the top left corner
                crossed_text = f"Crossed: {self.total_crossed_vehicles}"
                crossed_text_surface = self.font.render(crossed_text, True, self.white, self.black)
                self.screen.blit(crossed_text_surface, (10, 40))
                # display the elapsed time in the simulation
                elapsed_time = f"Elapsed time: {pygame.time.get_ticks() * self.simulation_speed / 1000} seconds"
                elapsed_time_surface = self.font.render(elapsed_time, True, self.white, self.black)
                self.screen.blit(elapsed_time_surface, (10, 60))
                # display the total vehicles spawned
                vehicle_text = f"Spawned: {vehicle_spawned_counter} vehicles"
                vehicle_text_surface = self.font.render(vehicle_text, True, self.white, self.black)
                self.screen.blit(vehicle_text_surface, (10, 100))
                # display the total vehicles killed
                killed_vehicles = f"Killed: {vehicle_kill_counter} vehicles"
                killed_vehicles_surface = self.font.render(killed_vehicles, True, self.white, self.black)
                self.screen.blit(killed_vehicles_surface, (10, 120))
                # display the total vehicles currently in the simulation
                current_vehicles = f"Current vehicles: {len(self.simulation)}"
                current_vehicles_surface = self.font.render(current_vehicles, True, self.white, self.black)
                self.screen.blit(current_vehicles_surface, (10, 160))
                # display the total vehicles for each direction
                vehicles_right = f"Right: {len(laneGroups['right'])}"
                vehicles_right_surface = self.font.render(vehicles_right, True, self.white, self.black)
                self.screen.blit(vehicles_right_surface, (10, 180))
                vehicles_down = f"Down: {len(laneGroups['down'])}"
                vehicles_down_surface = self.font.render(vehicles_down, True, self.white, self.black)
                self.screen.blit(vehicles_down_surface, (10, 200))
                vehicles_left = f"Left: {len(laneGroups['left'])}"
                vehicles_left_surface = self.font.render(vehicles_left, True, self.white, self.black)
                self.screen.blit(vehicles_left_surface, (10, 220))
                vehicles_up = f"Up: {len(laneGroups['up'])}"
                vehicles_up_surface = self.font.render(vehicles_up, True, self.white, self.black)
                self.screen.blit(vehicles_up_surface, (10, 240))

            # Display signals
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

                self.screen.blit(rotated_signal, signalCords[i])

                # Update the number of vehicles in front of the stop line for each signal
                signals[i].vehicles_in_front = 0

                for vehicle in laneGroups[directionNumbers[i]]:
                    if vehicle.crossed is False:
                        signals[i].vehicles_in_front += 1

                if self.debug_mode:
                    # Display the number of vehicles in front of the stop line
                    vehicles_in_front_text = f"Vehicles in front ({directionNumbers[i]}): {signals[i].vehicles_in_front}"
                    vehicles_in_front_surface = self.font.render(vehicles_in_front_text, True, self.white, self.black)
                    self.screen.blit(vehicles_in_front_surface, (10, 260 + i * 20))

            # Display vehicles
            for vehicle in self.simulation:
                self.screen.blit(vehicle.image, [vehicle.x, vehicle.y])
                if self.debug_mode:
                    # Display the direction of each vehicle
                    direction_text = f"{vehicle.direction}"
                    direction_surface = self.font.render(direction_text, True, self.white, self.black)
                    self.screen.blit(direction_surface, (vehicle.x + 10, vehicle.y - 20))
                    pygame.draw.rect(self.screen, (255, 0, 0), vehicle.hit_box, 2)

                vehicle.update()
                if vehicle.cross_time is not None and vehicle.flag is False:
                    spawn_to_cross_time = vehicle.cross_time - vehicle.spawn_time
                    self.crossing_times.append(spawn_to_cross_time * self.simulation_speed)
                    vehicle.flag = True

            pygame.display.update()

            # Use clock.tick() to control the frame rate
            self.clock.tick(FPS)  # Adjust to the desired frame rate

        self.total_time = pygame.time.get_ticks() * self.simulation_speed / 1000
        print(f"Simulation completed. Total time: {self.total_time} seconds.")
        self.average_waiting_time = sum(self.crossing_times) / len(self.crossing_times)
        self.min_waiting_time = min(self.crossing_times)
        self.max_waiting_time = max(self.crossing_times)

        # Reset the simulation after completion
        self.reset_simulation()

    def initialize(self):
        global signals, laneGroups
        signals = []  # Clear existing signals
        self.crossing_times = []  # Clear existing crossing times
        for i in range(0, noOfSignals):
            signals.append(TrafficSignal(10, 3, 5))

        laneGroups = {'right': pygame.sprite.Group(), 'down': pygame.sprite.Group(), 'left': pygame.sprite.Group(),
                      'up': pygame.sprite.Group()}

    def get_results(self):
        return {
            'Total time': self.total_time,
            'average_crossing_time': self.average_waiting_time,
            'max_crossing_time': self.max_waiting_time,
            'min_crossing_time': self.min_waiting_time
        }
