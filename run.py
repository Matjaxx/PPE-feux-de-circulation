from simulation import RunSimulation

if __name__ == "__main__":
    total_vehicles_to_cross = 20  # Number of vehicles to cross in each simulation
    simulation_speed = 10  # Speed factor for the simulation
    traffic_density = 0.3  # Density of traffic (ranges from 0.1 to 1)
    num_simulations = 2  # Number of simulations to run
    direction_priority = [1, 0, 1, 0]  # Direction priority array (0: Down, 1: Left, 2: Up, 3: Right) (0 to 1)
    simulation_results = []  # List to store results of each simulation

    # Run multiple simulations
    for _ in range(num_simulations):
        simulation_instance = RunSimulation(total_vehicles_to_cross, simulation_speed, traffic_density,
                                            direction_priority, traffic_light_policy="optimal")  # normal or optimal
        results = simulation_instance.get_results()
        simulation_results.append(results)

    # Calculate the averages for all variables across simulations
    total_results_sum = {key: 0 for key in simulation_results[0].keys()}
    for result in simulation_results:
        for key, value in result.items():
            total_results_sum[key] += value  # Accumulate sum for each variable

    # Calculate averages from the total sums
    averages = {key: value / num_simulations for key, value in total_results_sum.items()}

    # Print the averages for all variables
    for key, value in averages.items():
        print(f"{key}: {value}")
