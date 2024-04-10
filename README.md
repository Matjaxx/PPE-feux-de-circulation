
# Simulation de Trafic Open-Source

Ce projet vise à simuler la gestion du trafic à une intersection, en utilisant Pygame pour la visualisation et en appliquant des principes d'apprentissage par renforcement pour optimiser les signaux de circulation. Notre objectif est de réduire les temps d'attente, minimiser les congestions et améliorer la fluidité du trafic.

## Fonctionnalités

- Simulation en temps réel d'une intersection avec gestion dynamique des feux de signalisation.
- Utilisation de Pygame pour une visualisation interactive du trafic.
- Stratégies d'optimisation des signaux basées sur l'apprentissage par renforcement.

## Commencer

### Prérequis

- Python 3.6+
- Pygame

### Installation

Clonez ce répertoire et installez les dépendances :

```bash
git clone https://github.com/votre-repo/simulation-trafic.git
cd simulation-trafic
pip install -r requirements.txt
```

### Exécution

Pour lancer la simulation, exécutez :

```python
python main.py
```

## Contribution

Nous encourageons activement les contributions ! Si vous avez des suggestions, des corrections de bugs ou des améliorations, n'hésitez pas à soumettre une pull request ou à ouvrir un issue.



## Reconnaissance

- Merci à la communauté Pygame pour le soutien et la documentation.
- Ce projet a été inspiré par des travaux de recherche sur l'optimisation du trafic urbain.


## Explication du Code

Le projet est structuré autour de plusieurs classes principales et de fonctions permettant de simuler le comportement dynamique des feux de signalisation et des véhicules à une intersection.

### Classes Principales

- `TrafficSignal`: Représente un feu de signalisation, avec des durées configurables pour les phases rouge, jaune et verte.
- `Vehicle`: Représente un véhicule circulant dans la simulation. Chaque véhicule a un type, une direction, et peut détecter les collisions avec d'autres véhicules.

### Fonctionnalités Clés

- **Simulation de Trafic**: Utilise Pygame pour créer une fenêtre de visualisation où les véhicules se déplacent et réagissent aux feux de signalisation.
- **Gestion Dynamique des Feux**: Les durées des feux sont ajustées en fonction de la densité du trafic, visant à optimiser le flux de circulation.
- **Détection des Collisions**: Les véhicules peuvent détecter les autres véhicules devant eux pour éviter les collisions, en ajustant leur vitesse ou en s'arrêtant.
- **Politiques de Feux de Signalisation**: Supporte différentes stratégies pour changer les feux, incluant un mode optimal basé sur le nombre de véhicules en attente.

### Architecture du Code

Le code est divisé en plusieurs fichiers pour une meilleure organisation et clarté. Le fichier principal `simulation.py` initialise la simulation et contrôle le cycle principal du jeu. Les classes `TrafficSignal` et `Vehicle` sont définies dans des fichiers séparés pour encapsuler leur comportement.

### Exécution et Configuration

La simulation peut être configurée en ajustant les constantes au début du fichier `run.py`, telles que la densité du trafic, les temps de feux, etc. Pour lancer la simulation, exécutez simplement le fichier `main.py` avec Python.



## Utilisation de la Simulation

La fonction principale de simulation est encapsulée dans la classe `RunSimulation`, qui prend plusieurs paramètres à l'initialisation pour configurer la simulation.

### Paramètres de la Simulation

- `total_vehicles_to_cross`: Nombre total de véhicules à traverser l'intersection avant que la simulation ne s'arrête.
- `simulation_speed`: Vitesse de la simulation. Plus cette valeur est élevée, plus la simulation s'exécute rapidement.
- `trafficDensity`: Densité du trafic, affectant le nombre de véhicules générés.
- `direction_priority`: Liste des poids pour la génération aléatoire des directions des véhicules, permettant de simuler des flux de trafic plus denses dans certaines directions.
- `traffic_light_policy`: Stratégie pour la gestion des feux de signalisation. Peut être `"random"` pour une sélection aléatoire ou `"optimal"` pour une sélection basée sur la densité du trafic.

### Démarrer la Simulation

Pour démarrer une simulation, créez une instance de `RunSimulation` avec les paramètres désirés, puis appelez la méthode `run()` pour lancer la simulation.

```python
from simulation import RunSimulation

simulation_instance = RunSimulation(
    total_vehicles_to_cross=200,
    simulation_speed=20,
    trafficDensity=0.3,
    direction_priority=[1, 1, 1, 1],  # Égal pour toutes les directions
    traffic_light_policy="optimal"  # Utilisation de la stratégie optimale
)

simulation_instance.run()
```

### Sorties de la Simulation

La simulation produit plusieurs sorties, notamment le temps total écoulé, le nombre total de véhicules ayant traversé, ainsi que les temps d'attente moyens, minimums et maximums. Ces métriques peuvent être consultées après l'exécution de la simulation pour évaluer la performance des stratégies de gestion du trafic.

### Personnalisation des Politiques de Feux

La simulation supporte la personnalisation des politiques de gestion des feux de signalisation. En passant `"random"` ou `"optimal"` au paramètre `traffic_light_policy`, vous pouvez expérimenter avec différentes approches pour trouver celle qui optimise le mieux le flux de trafic selon vos critères.

