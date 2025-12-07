---
sidebar_position: 3
title: Sensors and Perception
description: Understanding how robots sense and perceive their environment
---

# Sensors and Perception

## Introduction to Robot Sensing

Just as humans rely on senses to navigate and interact with the world, robots depend on sensors to perceive their environment. This chapter explores the various sensing modalities used in humanoid robotics and how sensor data is processed for perception.

## Types of Sensors

### Proprioceptive Sensors

Proprioceptive sensors measure the robot's internal state—its own body position and motion.

#### Joint Encoders

Encoders measure joint angles and are essential for knowing the robot's configuration.

**Types of Encoders:**
- **Incremental Encoders**: Measure relative changes in position
- **Absolute Encoders**: Provide absolute position at any time
- **Resolution**: Measured in counts per revolution (CPR), typically 1000-10000+

**Applications:**
- Joint position feedback for control
- Velocity estimation through differentiation
- Forward kinematics calculation

#### Inertial Measurement Units (IMU)

IMUs combine multiple sensors to measure orientation and acceleration.

**Components:**
- **Accelerometers**: Measure linear acceleration (3-axis)
- **Gyroscopes**: Measure angular velocity (3-axis)
- **Magnetometers**: Measure magnetic field direction (optional)

**6-DOF vs 9-DOF IMUs:**
- 6-DOF: Accelerometer + Gyroscope
- 9-DOF: Accelerometer + Gyroscope + Magnetometer

**Key Specifications:**
- Sampling rate: 100-1000 Hz typical
- Gyro drift: 0.1-10 °/hour
- Accelerometer noise: 50-500 μg/√Hz

#### Force/Torque Sensors

These sensors measure forces and torques, crucial for:
- Detecting contact with the environment
- Controlling manipulation force
- Measuring ground reaction forces

**Strain Gauge Based:**
Most common type, using the change in electrical resistance when material deforms.

**6-Axis F/T Sensors:**
Measure all three force components (Fx, Fy, Fz) and three torque components (Tx, Ty, Tz).

### Exteroceptive Sensors

Exteroceptive sensors measure the external environment.

#### Vision Systems

**Camera Types:**

1. **RGB Cameras**: Capture color images
   - Resolution: VGA (640×480) to 4K+
   - Frame rate: 30-120 fps
   - Applications: Object recognition, visual servoing

2. **Depth Cameras**: Measure distance to objects
   - **Structured Light**: Project patterns and analyze distortion (e.g., Intel RealSense)
   - **Time of Flight (ToF)**: Measure light travel time
   - **Stereo Vision**: Use two cameras to triangulate depth

3. **Event Cameras**: Detect brightness changes asynchronously
   - Very high temporal resolution (μs)
   - High dynamic range
   - Low latency

**Camera Specifications:**
| Parameter | Typical Range |
|-----------|---------------|
| Resolution | 640×480 to 4096×2160 |
| Frame Rate | 30-120 fps |
| Field of View | 60°-180° |
| Depth Range | 0.3-10 m |

#### LiDAR (Light Detection and Ranging)

LiDAR uses laser pulses to measure distances.

**Operating Principle:**
1. Emit laser pulse
2. Pulse reflects off objects
3. Measure time until return
4. Calculate distance: $d = \frac{c \cdot t}{2}$

**Types:**
- **2D LiDAR**: Single scanning plane
- **3D LiDAR**: Multiple planes or rotating head

**Advantages:**
- High accuracy (±1-3 cm)
- Long range (up to 100+ m)
- Works in various lighting conditions

**Limitations:**
- Struggles with transparent/reflective surfaces
- Higher cost than cameras
- Lower resolution than cameras

#### Tactile Sensors

Tactile sensors enable robots to "feel" contact and texture.

**Technologies:**

1. **Resistive**: Pressure changes electrical resistance
2. **Capacitive**: Pressure changes capacitance
3. **Piezoelectric**: Generates voltage from pressure
4. **Optical**: Uses light to detect deformation

**Tactile Arrays:**
- Arranged in grids on fingertips or palms
- Resolution: 1-5 mm spacing
- Sensitivity: 0.01-1 N

**BioTac and Similar:**
Advanced sensors that mimic human fingertip:
- Detect force, vibration, temperature
- Fluid-filled for compliance

#### Proximity Sensors

Detect objects without contact.

**Ultrasonic Sensors:**
- Use sound waves (40-200 kHz)
- Range: 2 cm to 5 m
- Lower cost, lower resolution

**Infrared Sensors:**
- Emit and detect IR light
- Short range (1 cm to 1 m)
- Affected by ambient light

## Sensor Fusion

Combining data from multiple sensors improves reliability and accuracy.

### Why Sensor Fusion?

- **Complementary**: Different sensors capture different information
- **Redundant**: Multiple sensors measuring the same quantity increase reliability
- **Cooperative**: Sensors working together can measure what neither could alone

### Kalman Filter

The Kalman filter is the foundational algorithm for sensor fusion.

**State Estimation:**
Estimates hidden state from noisy measurements.

**Two Steps:**
1. **Predict**: Use motion model to predict next state
2. **Update**: Incorporate new measurement

**Equations:**
```
Predict:
  x̂ₖ|ₖ₋₁ = Fₖx̂ₖ₋₁|ₖ₋₁ + Bₖuₖ
  Pₖ|ₖ₋₁ = FₖPₖ₋₁|ₖ₋₁Fₖᵀ + Qₖ

Update:
  Kₖ = Pₖ|ₖ₋₁Hₖᵀ(HₖPₖ|ₖ₋₁Hₖᵀ + Rₖ)⁻¹
  x̂ₖ|ₖ = x̂ₖ|ₖ₋₁ + Kₖ(zₖ - Hₖx̂ₖ|ₖ₋₁)
  Pₖ|ₖ = (I - KₖHₖ)Pₖ|ₖ₋₁
```

### Extended Kalman Filter (EKF)

For nonlinear systems, linearize around current estimate:
- Replace F with Jacobian of motion model
- Replace H with Jacobian of measurement model

### Particle Filters

For highly nonlinear or multimodal distributions:
- Represent belief with weighted particles
- Sample, weight, resample
- More flexible but computationally expensive

## Computer Vision for Robotics

### Image Processing Fundamentals

**Color Spaces:**
- RGB: Red, Green, Blue
- HSV: Hue, Saturation, Value (better for color detection)
- Grayscale: Single intensity channel

**Common Operations:**
- **Filtering**: Smoothing, edge detection (Sobel, Canny)
- **Morphology**: Erosion, dilation, opening, closing
- **Segmentation**: Thresholding, clustering, region growing

### Object Detection and Recognition

**Traditional Approaches:**
1. Feature extraction (SIFT, SURF, ORB)
2. Feature matching
3. Model fitting

**Deep Learning Approaches:**
- **CNN-based**: YOLO, SSD, Faster R-CNN
- **Real-time capable**: 30+ fps on GPU
- **High accuracy**: 80-90%+ mAP on standard benchmarks

### Pose Estimation

Determining object or human pose from images.

**Object Pose:**
- 6-DOF: 3 position + 3 orientation
- Methods: PnP, ICP, learning-based

**Human Pose:**
- Keypoint detection (OpenPose, MediaPipe)
- Full body mesh estimation (SMPL)
- Applications: Human-robot interaction, motion capture

### Visual SLAM

Simultaneous Localization and Mapping using vision.

**Process:**
1. Extract visual features from camera images
2. Track features across frames
3. Estimate camera motion (Visual Odometry)
4. Build and update map
5. Detect loop closures
6. Optimize trajectory and map

**Popular Systems:**
- ORB-SLAM3
- LSD-SLAM
- RTAB-Map

## Depth Perception

### Stereo Vision

Using two cameras to triangulate depth.

**Geometry:**
```
      Left     Right
      Camera   Camera
        ●--------●
        |   b    |
        |        |
      fl|      fr|
        |        |
        +---------+
              Object
```

**Disparity:**
$d = x_L - x_R$

**Depth:**
$Z = \frac{f \cdot b}{d}$

Where:
- $f$ is focal length
- $b$ is baseline (distance between cameras)
- $d$ is disparity

### Structured Light

Project known pattern and analyze distortion.

**Process:**
1. Project pattern (dots, lines, grids)
2. Capture image of deformed pattern
3. Compare with reference to compute depth

**Example:** Intel RealSense D4xx series

### Time of Flight

Measure light travel time directly.

**Phase-based ToF:**
- Modulate light amplitude
- Measure phase shift of return
- Range limited by modulation frequency

**Example:** Microsoft Azure Kinect

## Sensor Integration in Humanoids

### Head Sensors
- Stereo cameras for vision
- IMU for head orientation
- Microphones for audio

### Body Sensors
- Torso IMU for balance
- Joint encoders throughout
- Force/torque at wrists and ankles

### Hand Sensors
- Tactile arrays on fingertips
- Joint encoders in fingers
- Force sensors for grip

### Foot Sensors
- Force/torque for ground reaction
- Pressure distribution sensors
- Contact switches

## Challenges and Future Directions

### Current Challenges
1. **Sensor noise and drift**: Requires careful calibration and filtering
2. **Real-time processing**: High-bandwidth sensor data needs fast processing
3. **Sensor fusion complexity**: Integrating diverse modalities is difficult
4. **Cost**: High-quality sensors remain expensive

### Emerging Technologies
- **Event cameras**: Ultra-high speed vision
- **Neuromorphic sensors**: Brain-inspired sensing
- **Soft sensors**: Conformable to curved surfaces
- **Self-calibrating systems**: Reduce maintenance burden

## Summary

Robot sensing encompasses a wide array of technologies:
- Proprioceptive sensors measure internal state
- Exteroceptive sensors perceive the environment
- Sensor fusion combines multiple sources for robust estimation
- Computer vision enables understanding of visual information
- Depth perception provides 3D environmental awareness

Effective sensor integration is essential for humanoid robots to operate safely and effectively in human environments.

## Key Concepts

| Sensor Type | Measures | Key Specifications |
|-------------|----------|-------------------|
| Encoder | Joint angle | Resolution (CPR) |
| IMU | Orientation, acceleration | Drift rate, noise |
| F/T Sensor | Force, torque | Range, resolution |
| Camera | Visual scene | Resolution, frame rate |
| LiDAR | Distance | Range, accuracy |
| Tactile | Contact, pressure | Resolution, sensitivity |

## Review Questions

1. What is the difference between proprioceptive and exteroceptive sensors?
2. How does a Kalman filter combine predictions with measurements?
3. Explain the relationship between stereo disparity and depth.
4. Why is sensor fusion important for robot perception?
