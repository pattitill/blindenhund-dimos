# Blindenhund-DimOS

Dieses Repository ist Teil unseres Bachelorprojekts. Ziel ist es, einen **Roboterhund (Unitree Go2 EDU)** mit **Assistenz-Funktionalitäten eines Blindenhundes** auszustatten.  
Das Projekt kombiniert **Simulation in Gazebo** mit **LLM-basierten Agenten (DimOS)**, um Navigation, Hinderniserkennung und Interaktion umzusetzen.

---

## Ziele des Projekts

- Entwicklung eines KI-gestützten Assistenzroboters für blinde oder sehbehinderte Menschen.
- Simulation realistischer Szenarien (z. B. Navigation durch eine Welt mit Gehwegen, Türen, Hindernissen).
- Integration von **DimOS Agents** mit ROS2, um sensorische Eingaben zu verarbeiten und in Aktionen zu übersetzen.
- Umsetzung eines **Pilot-Szenarios**:
  - Der Roboter navigiert in einer Umgebung.
  - Erkennt Hindernisse und Personen.
  - Führt Befehle über Spracheingabe oder vordefinierte Kommandos aus.
  - Unterstützt den Benutzer sicher beim Navigieren (z. B. „Stoppe vor Tür“, „folge Person“, „weiche Hindernis aus“).

---

Technologien und Frameworks

- **ROS2 Humble**  
  Middleware zur Kommunikation von Robotik-Systemen (Topics, Actions, Services).

- **Gazebo Fortress**  
  Simulationsumgebung zur Modellierung des Unitree Go2, Sensoren (LiDAR, Kamera) und einer Testwelt.

- **Unitree Go2 EDU Spezifikationen**  
  - URDF/Xacro-Modelle im `go2_description` Paket  
  - Simulation in `go2_gazebo`  
  - Navigation & SLAM in `go2_navigation`  

- **Nav2 + SLAM Toolbox**  
  Klassische ROS2-Pakete zur autonomen Navigation und Kartierung.

- **DimOS Framework**  
  - Multi-Agenten-Architektur zur Integration von LLMs (GPT-4o, Claude, etc.)  
  - Bindung an ROS2-Sensoren (Kamera, LiDAR, IMU)  
  - Steuerung über Skills (`NavigateToGoal`, `FollowHuman`, `StopAtObstacle` usw.)

- **Python (ament_python)**  
  Hauptsprache für ROS2-Pakete und DimOS-Integration.  

- **Docker (optional)**  
  Zur Reproduzierbarkeit und Teamarbeit.

---

## Repository Struktur


blindenhund-dimos/
├── go2_ws/                  # ROS2-Workspace
│   └── src/
│       ├── go2_description/ # Roboter-Spezifikationen (URDF, meshes, xacro)
│       ├── go2_gazebo/      # Gazebo-Welten + Launchfiles
│       ├── go2_navigation/  # Nav2 + SLAM (Config, Maps, Launches)
│       ├── go2_bringup/     # Master-Launcher (startet alles zusammen)
│       └── dimos_ros_bridge/# Bridge ROS2 ↔ DimOS
│
├── dimos/                   # DimOS-Framework (lokal eingebunden)
├── agents/                  # Eigene Agent-Definitionen (NavigationAgent, InteractionAgent)
└── README.md



ToDo / Roadmap

 Basis-Repo mit ROS2-Workspace und DimOS-Integration erstellen.

 Roboter-Description + Gazebo-Welten übernehmen.

 DimOS-Agent mit ROS2-Sensoren verbinden.

 Navigation-Scenario mit Nav2 + SLAM stabilisieren.

 Sprach- und Bildinteraktion einbinden.

 Szenario „Blindenhund führt Person durch Umgebung“ demonstrieren.
