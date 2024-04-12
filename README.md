
# Simulation de Trafic Open-Source

Ce projet vise à simuler la gestion du trafic à une intersection, en intégrant la détection de véhicules avec une Raspberry Pi et en utilisant Pygame pour la visualisation. En appliquant des principes d'apprentissage par renforcement, notre objectif est d'optimiser les signaux de circulation afin de réduire les temps d'attente, de minimiser les congestions et d'améliorer la fluidité du trafic.

## Fonctionnalités

- Détection de véhicules en temps réel sur une Raspberry Pi.
- Envoie des données à un serveur.
- Simulation en temps réel d'une intersection avec gestion dynamique des feux de signalisation.
- Utilisation de Pygame pour une visualisation interactive du trafic.
- Stratégies d'optimisation des signaux basées sur l'apprentissage par renforcement.

## Commencer

### Prérequis

- Raspberry Pi 3+
- Un PC Serveur
- Python 3.6+
- Pygame

### Installation

Clonez ce répertoire et installez les dépendances :

```bash
git clone https://github.com/Matjaxx/PPE-feux-de-circulation.git
cd PPE-feux-de-circulation
pip install -r requirements.txt
```

Sur la Raspberry Pi:

Installez OpenCV:
```bash
sudo apt install python3-opencv
```

Installez dlib:
```bash
git clone https://github.com/davisking/dlib.git

cd dlib
mkdir build
cd build
cmake ..
cmake --build .
sudo make install

sudo python3 setup.py install
```

### Exécution

Pour lancer la simulation de détection, exécutez :

```python
python3 detect.py
```

Pour lancer la simulation de Machine Learning, exécutez :

```python
python run.py
```

## Contribution

Nous encourageons activement les contributions ! Si vous avez des suggestions, des corrections de bugs ou des améliorations, n'hésitez pas à soumettre une pull request ou à ouvrir un issue.

## Reconnaissance

- Merci à la communauté Pygame et YOLO pour le soutien et la documentation.
- Ce projet a été inspiré par des travaux de recherche sur l'optimisation du trafic urbain.
- Ce projet a été inspiré par des travaux de détection de Pysource et Code-X (https://github.com/sathyaraj819/Vehicle-Detection-And-Speed-Tracking).

## Explication du Code

Le projet est structuré autour de plusieurs classes principales et de fonctions permettant de simuler le comportement dynamique des feux de signalisation et des véhicules à une intersection.

### Détection

La partie détection de ce projet implique deux bibliothèques :
- YOLOv4 : est une IA configurée avec `yolov4-tiny.cfg` et `yolov4-tiny.weights`. Elle utilise un réseau neuronal pour détecter les objets tels que les véhicules dans la liste `classes.txt`.
- dlib : permet le suivi des véhicules et met à jour les traqueurs. 

Les données du compteur de voitures sont envoyées au serveur via des sockets pour un traitement ultérieure.

### Classes Principales du Machine Learning

- `TrafficSignal`: Représente un feu de signalisation, avec des durées configurables pour les phases rouge, jaune et verte.
- `Vehicle`: Représente un véhicule circulant dans la simulation. Chaque véhicule a un type, une direction, et peut détecter les collisions avec d'autres véhicules.

### Fonctionnalités Clés du Machine Learning

- **Simulation de Trafic**: Utilise Pygame pour créer une fenêtre de visualisation où les véhicules se déplacent et réagissent aux feux de signalisation.
- **Gestion Dynamique des Feux**: Les durées des feux sont ajustées en fonction de la densité du trafic, visant à optimiser le flux de circulation.
- **Détection des Collisions**: Les véhicules peuvent détecter les autres véhicules devant eux pour éviter les collisions, en ajustant leur vitesse ou en s'arrêtant.
- **Politiques de Feux de Signalisation**: Supporte différentes stratégies pour changer les feux, incluant un mode optimal basé sur le nombre de véhicules en attente.

### Architecture du Code

Le code est divisé en plusieurs fichiers pour une meilleure organisation et clarté. Le fichier principal `simulation.py` initialise la simulation et contrôle le cycle principal du jeu. Les classes `TrafficSignal` et `Vehicle` sont définies dans des fichiers séparés pour encapsuler leur comportement.

### Exécution et Configuration

La simulation peut être configurée en ajustant les constantes au début du fichier `run.py`, telles que la densité du trafic, les temps de feux, etc. Pour lancer la simulation, exécutez simplement le fichier `main.py` avec Python.

## Utilisation de la Première Simulation

### Configuration de la Simulation

Pour configurer cette simulation, remplacez le chemin d'accès de la source vidéo par celui de votre propre fichier vidéo, ou utilisez nos vidéos par défaut.
Vous pouvez également connecter une webcam et modifier le code dans le fichier `detect.py` :

```python
video = cv2.VideoCapture(0)
```

Pour configurer votre serveur, modifiez l'adresse dans le code du fichier `server.py` :
```python
s.connect(("10.0.0.9", 5000))
```

### Exécution de la Simulation

Exécutez les deux codes sur deux machines différentes.

Pour la détection, une première fenêtre apparaît, vous permettant de sélectionner les 4 points pour sélectionner la zone d'intérêt :

![selection5](https://github.com/Matjaxx/PPE-feux-de-circulation/assets/144214410/089a3150-dcc7-4df3-9980-df4458c1aafa)

### Sorties de la Simulation

Une deuxième fenêtre apparaît pour afficher et compter les voitures dans la zone sélectionnée :

![outputcopie](https://github.com/Matjaxx/PPE-feux-de-circulation/assets/144214410/78c37284-05e6-4e8c-a417-acb7c18014a7)

Sur le serveur, la valeur du compteur a été transmise :

![server](https://github.com/Matjaxx/PPE-feux-de-circulation/assets/144214410/48bd8fb2-a757-43fb-8fa5-3bd82a23ae53)

## Utilisation de la Seconde Simulation

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

