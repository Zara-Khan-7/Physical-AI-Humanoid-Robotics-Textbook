---
sidebar_position: 4
title: Actuators and Movement
description: Understanding how robots generate motion through actuators
---

# Actuators and Movement

## Introduction

Actuators are the muscles of robots—they convert energy into motion. In humanoid robotics, actuators must provide the strength, speed, and precision needed for human-like movement while operating safely around people.

## Types of Actuators

### Electric Motors

Electric motors are the most common actuators in humanoid robots due to their controllability, efficiency, and reliability.

#### DC Motors

Direct Current motors are simple and easy to control.

**Operating Principle:**
- Current flows through coils in a magnetic field
- Produces torque on the rotor
- Direction controlled by current polarity

**Characteristics:**
- Simple speed control via voltage
- Linear torque-speed relationship
- Require brushes (wear component)

**Brushless DC (BLDC) Motors:**
- Electronic commutation instead of brushes
- Higher efficiency and lifetime
- More complex control electronics
- Standard in modern robotics

#### Servo Motors

Servo motors include feedback for precise position control.

**Components:**
1. Motor (often BLDC)
2. Encoder or resolver for position feedback
3. Controller/driver electronics

**Control Modes:**
- Position control
- Velocity control
- Torque control

#### Stepper Motors

Move in discrete steps, providing position control without feedback.

**Characteristics:**
- Precise open-loop positioning
- Hold torque when stationary
- Limited speed and efficiency
- Prone to resonance issues

**Applications:**
- Low-cost applications
- Slow, precise movements
- 3D printers, CNC machines

### Hydraulic Actuators

Use pressurized fluid to generate force.

**Advantages:**
- Very high power density
- Can generate large forces
- Smooth motion

**Disadvantages:**
- Heavy support equipment (pumps, reservoirs)
- Maintenance intensive
- Risk of leaks
- Difficult precise control

**Applications:**
- Large industrial robots
- Heavy lifting applications
- Boston Dynamics Atlas (historically)

### Pneumatic Actuators

Use compressed air for actuation.

**Advantages:**
- Lightweight actuators
- Natural compliance (compressible medium)
- Safe for human interaction
- Clean and simple

**Disadvantages:**
- Lower precision than electric
- Compressor noise and bulk
- Limited force

**Applications:**
- Soft robotics
- Grippers
- Compliant manipulation

### Emerging Actuator Technologies

#### Series Elastic Actuators (SEA)

Include a compliant element (spring) between motor and load.

```
Motor → Gearbox → Spring → Load
```

**Benefits:**
- Measures force via spring deflection
- Absorbs impact shocks
- Natural compliance for safety
- Energy storage and release

**Trade-offs:**
- Reduced bandwidth
- Increased complexity
- Added weight

#### Quasi-Direct Drive

High-torque motors with low-ratio gearing.

**Characteristics:**
- Backdrivable (can be pushed)
- High bandwidth
- Good torque sensing
- Lower gear wear

**Examples:**
- MIT Cheetah leg actuators
- Many modern humanoid designs

#### Artificial Muscles

Biologically-inspired actuators.

**Types:**

1. **Pneumatic Artificial Muscles (PAM)**
   - McKibben muscles
   - Contract when inflated
   - High power-to-weight ratio

2. **Shape Memory Alloys (SMA)**
   - Nitinol wires
   - Contract when heated
   - Slow response, limited cycles

3. **Electroactive Polymers (EAP)**
   - Change shape with electric field
   - Dielectric elastomers
   - Ionic polymer-metal composites

4. **Hydraulically Amplified Self-healing Electrostatic (HASEL)**
   - Combine benefits of hydraulic and electric
   - Soft, fast, high force

## Transmission Systems

### Gearboxes

Convert motor speed/torque characteristics.

**Gear Ratio:**
$$
n = \frac{\omega_{in}}{\omega_{out}} = \frac{\tau_{out}}{\tau_{in}}
$$

**Types:**

1. **Spur Gears**: Simple, efficient, but noisy
2. **Planetary Gears**: Compact, high ratio, inline
3. **Harmonic Drives**: Very high ratio, zero backlash, compact
4. **Cycloidal Drives**: High ratio, robust, shock resistant

**Key Specifications:**
| Parameter | Description |
|-----------|-------------|
| Ratio | Speed reduction factor |
| Efficiency | Power out / Power in |
| Backlash | Angular play between gears |
| Torque Capacity | Maximum continuous torque |

### Harmonic Drives

Special mention due to prevalence in robotics.

**Components:**
- Wave generator (elliptical)
- Flexspline (thin, flexible)
- Circular spline (rigid, internal teeth)

**Advantages:**
- Ratios 30:1 to 320:1 in single stage
- Zero backlash
- High torque density
- Compact

**Disadvantages:**
- Flexspline fatigue
- Limited efficiency (80-90%)
- Cost

### Belt and Chain Drives

**Timing Belts:**
- Quiet operation
- No lubrication needed
- Moderate precision
- Limited power transmission

**Chain Drives:**
- Higher power capacity
- Less precise than gears
- Require lubrication

### Cable/Tendon Drives

Common in dexterous hands.

**Advantages:**
- Remote motor placement
- Lightweight distal segments
- Flexible routing

**Challenges:**
- Cable stretch
- Friction management
- Complexity of routing

## Motion Control

### Position Control

Regulating actuator position to follow a reference.

**PID Control:**
$$
u = K_p(x_d - x) + K_i\int(x_d - x)dt + K_d(\dot{x}_d - \dot{x})
$$

**Typical Implementation:**
1. Outer position loop (lower bandwidth)
2. Inner velocity loop (higher bandwidth)
3. Innermost current loop (highest bandwidth)

### Velocity Control

For continuous motion tasks.

**Applications:**
- Conveyor following
- Smooth trajectory execution
- Grinding/polishing

### Torque/Force Control

Direct control of actuator output force.

**Importance for Robotics:**
- Safe human interaction
- Compliant manipulation
- Contact task control

**Methods:**
1. **Current Control**: Motor torque ∝ current
2. **Force Sensor Feedback**: Measure and control directly
3. **SEA Force Control**: Infer from spring deflection

### Impedance Control

Control the dynamic relationship between force and motion.

**Desired Behavior:**
$$
F = K(x_d - x) + D(\dot{x}_d - \dot{x}) + M(\ddot{x}_d - \ddot{x})
$$

Where K, D, M are virtual stiffness, damping, and inertia.

**Benefits:**
- Unified framework for position and force
- Graceful contact handling
- Intuitive parameter tuning

## Humanoid-Specific Considerations

### Joint Design

**Hip Joint:**
- 3 DOF typically (flexion/extension, abduction/adduction, rotation)
- High torque requirements
- Often uses serial arrangement of motors

**Knee Joint:**
- 1 DOF (flexion/extension)
- Very high torque during stance
- Often includes spring for energy storage

**Ankle Joint:**
- 2 DOF (plantarflexion/dorsiflexion, inversion/eversion)
- Critical for balance
- Series elastic popular here

**Shoulder:**
- 3 DOF (like hip)
- Large range of motion needed
- Cable-driven designs common

**Elbow:**
- 1-2 DOF
- Moderate torque requirements

**Wrist:**
- 2-3 DOF
- Compact design challenging

### Power Requirements

**Walking Energy:**
$$
P \approx m \cdot g \cdot v \cdot CoT
$$

Where:
- m = mass
- g = gravity
- v = velocity
- CoT = Cost of Transport (efficiency measure)

**Human CoT:** ~0.2
**Robot CoT:** 0.5-5 (improving)

### Safety Mechanisms

**Torque Limiting:**
- Slip clutches
- Electronic current limiting
- Breakaway mechanisms

**Collision Detection:**
- Joint torque monitoring
- Arm acceleration limits
- Contact detection algorithms

**Safe Design:**
- Compliant covers
- Rounded edges
- Low inertia distal segments

## Energy Storage and Management

### Battery Systems

**Common Types:**
- Lithium-ion (Li-ion)
- Lithium polymer (LiPo)
- Lithium iron phosphate (LiFePO4)

**Key Metrics:**
| Metric | Typical Value |
|--------|---------------|
| Energy density | 150-250 Wh/kg |
| Voltage | 3.7V per cell |
| Cycle life | 500-2000 cycles |

### Energy Recuperation

Regenerative braking recovers energy during deceleration.

**Implementation:**
1. Motor acts as generator
2. Energy flows back to battery
3. Requires bidirectional motor drivers

**Efficiency gains:** 10-30% depending on motion profile

### Thermal Management

Heat is the enemy of actuators.

**Sources:**
- Motor copper losses (I²R)
- Motor iron losses
- Gearbox friction
- Electronics

**Solutions:**
- Passive heatsinks
- Active cooling (fans, liquid)
- Derating under high load

## Summary

Actuators and their control are fundamental to humanoid robot capability:

- Electric motors dominate due to controllability
- Gearboxes adapt motor characteristics to load requirements
- New technologies (SEA, quasi-direct drive) improve safety and performance
- Motion control spans position, velocity, force, and impedance
- Energy management is critical for practical operation
- Safety is paramount for human-robot interaction

## Key Specifications Reference

| Actuator Type | Power Density | Efficiency | Control Bandwidth |
|---------------|---------------|------------|-------------------|
| BLDC Motor | 500-2000 W/kg | 85-95% | High |
| Hydraulic | 2000-5000 W/kg | 60-80% | Medium |
| Pneumatic | 500-1000 W/kg | 20-40% | Low |
| SEA | 200-500 W/kg | 70-85% | Medium |

## Review Questions

1. What are the advantages and disadvantages of hydraulic vs. electric actuators?
2. How does a Series Elastic Actuator improve force control and safety?
3. Why is impedance control preferred over pure position or force control in many robotics applications?
4. What factors determine the battery requirements for a humanoid robot?
