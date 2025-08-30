# Blindenhund-Projekt – Unitree Go2 mit DimOS 

## 🎯 Projektziele  

Dieses Projekt hat das Ziel, einen **Roboterhund (Unitree Go2 EDU mit 3D LiDAR)** mit den **Funktionalitäten eines Blindenhundes** auszustatten.  
Dazu kombinieren wir **Robotik-Frameworks (ROS2, Gazebo)** mit **LLM-basierten Agenten** (DimOS, RAI).  

Am Ende soll der Roboter:  
- Hindernisse erkennen und umgehen  
- Türen, Wege und relevante Objekte erkennen  
- Navigation (SLAM, Kartenbasiert + Echtzeitplanung) durchführen  
- Mit Menschen über Sprache und multimodale Eingaben interagieren  
- Szenarien wie „Führe eine Person sicher von A nach B“ oder „Warne vor Hindernissen“ umsetzen  

---

## 🏗️ Aufbau & Struktur  

Das Repository ist in **zwei Hauptteile** gegliedert:  

### 1. DimOS-Integration  
- Zentrale Schnittstelle zwischen **LLMs (Agents)** und **Robotersensorik / -steuerung**  
- Ermöglicht, dass KI-Agents **ROS2 Nodes, Sensoren, Skills** direkt ansprechen können  
- Infrastruktur für:  
  - **Agents** (Planung, Execution, Memory)  
  - **Perception** (Objekterkennung, Segmentierung, Tiefenschätzung)  
  - **Navigation & Skills** (Global Planner, Local Planner, Bewegungsprimitive)  
  - **Simulation** (Isaac Sim, Genesis, Gazebo)  
  - **Streaming** (Video/Audio über WebRTC)  
  - **Unitree-spezifische Steuerung** (ROS2 Nodes + WebRTC Actions)  

👉 **Ordner im Repo**:  
- `dimos/` – Hauptframework (Agents, Models, Perception, Robot, Skills, Simulation, Stream, Web)  
- `tests/` – Tests für Agenten, ROS2-Integration, Skills  
- `docker/` – Containerisierte Entwicklungsumgebungen  

### 2. ROS2 Workspaces für Unitree Go2  
- Enthält alles, um den Roboter in **ROS2 Humble** und **Gazebo Fortress** zu betreiben  
- **Pakete**:  
  - `go2_bringup/` → Startskripte & Launch-Files  
  - `go2_description/` → URDF, Meshes, Config für Robotermodell  
  - `go2_gazebo/` → Welten, Launch-Files für Simulation  
  - `go2_navigation/` → Navigation, SLAM, Karten  

👉 **Ordner im Repo**:  
- `go2_ws/src/go2_bringup/`  
- `go2_ws/src/go2_description/`  
- `go2_ws/src/go2_gazebo/`  
- `go2_ws/src/go2_navigation/`  

---

## ⚙️ Eingesetzte Technologien  

- **ROS2 Humble** – Roboter-Middleware  
- **Gazebo Fortress** – Simulation & Testumgebung  
- **Unitree Go2 EDU** – Hardwareplattform mit 3D LiDAR  
- **DimOS** – Agenten-Framework für KI-gestützte Steuerung  
- **RAI** – Framework für Embodied AI & Multi-Agenten Systeme  
- **Python (ROS2 Nodes, Agenten, CV-Modelle)**  
- **Docker** – Containerisierte Entwicklungsumgebung  
- **LLMs / APIs** – OpenAI, Claude, ggf. HuggingFace für Perception & Reasoning  

---

## 🚀 Szenario (Endziel)  

Das Endziel ist ein **autonomer Blindenhund-Roboter**, der in einer realistischen Umgebung folgende Aufgaben beherrscht:  

1. Startet per Sprachbefehl (z. B. „Bring mich zur Tür“)  
2. Verarbeitet Sensordaten (Kameras, LiDAR) und erstellt eine Karte  
3. Nutzt SLAM + Navigation, um eine sichere Route zu berechnen  
4. Erkennt Hindernisse, Menschen, Türen und signalisiert diese  
5. Interagiert über Sprache mit dem Nutzer  
6. Führt die Person sicher ans Ziel  

---

👉 Diese README gibt jedem (und auch ChatGPT) einen klaren Überblick:  
- **Was das Ziel ist** (Blindenhund-Roboter mit KI)  
- **Wie die Struktur aufgebaut ist** (DimOS + ROS2 Workspaces)  
- **Welche Technologien im Spiel sind**  
