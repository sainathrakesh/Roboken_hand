# Roboken Hand: A Fully Actuated Robotic Hand with Intrinsic Actuation

A fully and intrinsically actuated robotic hand with 20 degrees of freedom, designed to replicate human-like dexterity while maintaining a compact 1:1 form factor.

---

## 🎯 Introduction

The human hand is one of the most sophisticated biomechanical systems in nature, combining strength, mobility, dexterity, and flexibility to enable tasks ranging from delicate object manipulation to precise gesture control. Beyond physical manipulation, hands serve as a primary communication tool. Millions of people worldwide rely on sign language, which demands complex, independently controlled finger configurations to convey the intent of the user more accurately. Replicating this level of dexterity in robotic systems has therefore become a central challenge in the field of human-robot interaction, with applications spanning prosthetics, collaborative robotics, and assistive communication devices.

### 📚 Background

Replicating the functionality of the human hand in robotic systems has been a longstanding pursuit in human-robot interaction research. Human hands are capable of high dexterity, adaptability, and precision due to their complex kinematic structure formed by 27 bones, delicate coordination of over 30 muscles, and an intricate network of tendons across multiple joints. Replicating this level of dexterity in robotic systems is challenging due to the need to balance complex control, advanced actuation, mechanical design constraints, and manufacturability.

While significant advancements have taken place in the field of design of the robotic hand, compromises have been made on the dexterity to simplify it or implement complex designs that are difficult to control and reproduce. This is a critical challenge to handle the trade-offs between human likeness and the robotic manipulation of the designed hand.

### ⚙️ Actuation Approaches

A fully actuated system is one in which the number of actuators match the degrees of freedom to improve dexterity compared to underactuated designs and allows precise control of the hand. The fully actuated robotic hand allows for precise finger positioning while the kinematic design is simplified. This reduces the complexity in the mechanical design and decouples multiple motions or trajectories being performed by a single actuator.

Although the geometric workspace of an underactuated system may be comparable to that of a fully actuated design, the mechanical coupling between joints reduces independent controllability and limits the set of achievable configurations. For applications such as sign language communication, where specific, complex finger poses are essential for conveying meaning, this limitation is critical. 

Existing approaches like the Inspire Robotics hand with 6 degrees of freedom come in two variants: one focuses on the speed of finger actuation while the other focuses on the force applied by the fingers. The Shadow Robotics hand, with 24 degrees of freedom, implements a tendon drive mechanism but houses its actuators in a bulky forearm assembly.

---

## 🤖 The Roboken Hand

To address these limitations, this project proposes the **Roboken hand**: a fully and intrinsically actuated robotic hand with **20 degrees of freedom**. Unlike existing fully actuated systems such as the Shadow Dexterous hand, which houses its actuators in a bulky forearm assembly, the Roboken hand embeds all actuators within the finger phalanges and palm, all while trying to maintain a human-like 1:1 form factor. The design is evaluated using a simulation framework that applies dexterity metrics across multiple robotic hand platforms, enabling direct quantitative comparison of kinematic performance.

---

## 🎯 Objectives

The primary objective of this project is to design, simulate, manufacture, and analyze a robotic hand to evaluate its ability to achieve human-like dexterity while maintaining a compact form factor. This refers to the ability of the robotic hand to move and perform gestures similar to the human hand, both in finger trajectories and grasp kinematics. The focus lies on three main components: design, actuation, and evaluation of human-likeness.

### ✨ Key Objectives

1. **✏️ Design**: A five-fingered robotic hand with a minimum of 20 degrees of freedom, where all actuators are embedded within the finger phalanges and palm structure rather than housed in an external forearm. The hand's proportions follow the Fibonacci golden ratio to replicate the kinematic relationships of a human hand.

2. **🔬 Simulation Framework**: Development of a simulation framework using ROS2 and URDF-based models that enables quantitative evaluation of the hand's kinematic performance. This framework is applied not only to the proposed design but also to four existing robotic hand platforms — the Ability Hand, Inspire Hand, Schunk SVH Hand, and Shadow Dexterous Hand. This enables the establishment of comparative benchmarks.

3. **📊 Dexterity Evaluation**: Evaluation of dexterity using multiple quantitative metrics, including:
   - Kapandji test for thumb opposition
   - Yoshikawa manipulability index for kinematic dexterity
   - Dexterity normalized by degrees of freedom
   - Dexterity normalized by structural volume

4. **👁️ Vision-Based Teleoperation**: Implementation of a vision-based teleoperation system using MediaPipe hand tracking integrated with ROS2, enabling real-time mapping of human hand motion to the robotic hand model.

5. **🏗️ Physical Prototype**: Manufacture of a physical prototype using additive manufacturing techniques, with material selection informed by structural requirements at the actuator link interfaces.

---

## 📦 Project Structure

```
roboken/
├── src/
│   ├── hands_one/                 # Main robotic hand package
│   ├── hands_one_controller/      # Hand controller
│   └── hands_one_moveit_configs/  # MoveIt configurations
├── build/                         # Build artifacts (generated)
├── install/                       # Installation artifacts (generated)
├── log/                           # Build logs
├── comparison.py                  # Hand comparison utility
└── README.md                      # This file
```

---

## 🚀 Quick Start Guide

### ✅ Prerequisites

- **OS**: Ubuntu 22.04
- **ROS2**: Humble or compatible version
- **Python**: 3.8+
- **Tools**: colcon, rosdep, rviz2

### 📥 Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/sainathrakesh/Roboken_hand.git
   cd roboken
   ```

2. **Source ROS2 Setup**
   ```bash
   source /opt/ros/humble/setup.bash
   ```

3. **Install Dependencies**
   ```bash
   rosdep install --from-paths src --ignore-src -y
   ```

4. **Build the Workspace**
   ```bash
   colcon build
   ```

5. **Source Installation**
   ```bash
   source install/setup.bash
   ```

---

## ▶️ How to Run the Project

### 🎮 Basic Hand Simulation & Visualization

1. **Launch RViz with the Hand Model**
   ```bash
   ros2 launch hands_one display.launch.py
   ```
   This will open RViz with the robotic hand URDF model fully loaded and visible.

2. **View Hand in Gazebo Simulator**
   ```bash
   ros2 launch hands_one gazebo.launch.py
   ```
   The hand will appear in the Gazebo physics simulator for interactive testing.

### 🎯 Hand Control & Movement

3. **Run Hand Controller Node**
   ```bash
   ros2 run hands_one_controller controller
   ```
   This starts the main controller node for hand actuation and joint control.

4. **Send Joint Commands**
   ```bash
   # Example: Move finger joint
   ros2 topic pub /hand/joint_command std_msgs/msg/Float64MultiArray \
     "data: [0.5, 0.3, 0.2, 0.1, 0.0]"
   ```

### 🗺️ MoveIt! Motion Planning

5. **Launch MoveIt with Hand**
   ```bash
   ros2 launch hands_one_moveit_configs demo.launch.py
   ```
   This opens MoveIt! for planning and executing complex hand gestures and trajectories.

6. **Plan & Execute Motions in MoveIt**
   - Open MoveIt! RViz plugin
   - Use the interactive marker to set target poses
   - Click "Plan" to calculate trajectory
   - Click "Execute" to perform the motion

### 📊 Hand Analysis & Comparison

7. **Run Comparison Analysis**
   ```bash
   python3 comparison.py
   ```
   This script analyzes and compares the Roboken hand with other robotic hand platforms.

---

## 🔧 Build & Compilation

### Full Build
```bash
colcon build
```

### Build Specific Package
```bash
colcon build --packages-select hands_one_controller
```

### Clean Build
```bash
colcon clean all && colcon build
```

### Verbose Build Output
```bash
colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release
```

---

## 📊 Focus Areas

The project focuses on motion and trajectory over the investigation into the ability to bear loads or pick heavy objects. This project analyzes the design of the hand where the actuators are intrinsic, making up the body of the finger. The aim is to study the ability of the design to conceal the actuators while maintaining the structure of the hand and to design a thumb that is dexterous enough to mimic the trajectory of an actual human thumb all while maintaining the size of the hand relatively close to a human hand.

Human-likeness in this project will be quantified through thumb opposition, manipulability, dexterity-per-DoF, and workspace characteristics. The study also aims to identify the factors where the underactuation in robot hands could fail to perfectly imitate a hand sign and where the hand with a higher degree of freedom shows a clearer indication.

---

## ❓ Problem Statement

Existing robotic hand designs are forced to choose between high dexterity with bulky extrinsic actuation, or compact form with reduced independent finger control. Current platforms have trade-offs between underactuated, independently controllable fingers with a bulky design or intrinsically actuated hands that maintains a human-like 1:1 form factor. This creates a gap in the ability to quantitatively evaluate how actuation architecture affects human-likeness in robotic hand motion.

### 🔍 Key Research Questions

- What is the minimum kinematic configuration required for an intrinsically actuated hand to achieve a good score on the Kapandji test?
- How does the manipulability of a fully actuated, intrinsic design compare to established underactuated and extrinsically actuated platforms when evaluated using various metrics?
- What are the tradeoffs between dexterity, mechanical efficiency, and structural volume across different actuation philosophies?

---

## 👥 Author

**Sainath Rakesh** - Primary contributor and maintainer

## 📧 Support

For issues, questions, or suggestions, please open an issue in the repository.

**Last Updated**: 2026-06-16
