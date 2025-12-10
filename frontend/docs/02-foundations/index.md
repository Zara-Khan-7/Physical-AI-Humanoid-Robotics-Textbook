---
sidebar_position: 2
slug: /foundations
title: Foundations of Humanoid Robotics
description: Core concepts in humanoid robot design and control
---

# Foundations of Humanoid Robotics

## Overview

Building a humanoid robot requires understanding multiple engineering disciplines. This chapter covers the fundamental concepts that underpin humanoid robot design, including kinematics, dynamics, and control theory.

## Robot Morphology

### The Human Body as Blueprint

The human body serves as the primary inspiration for humanoid robot design. Key anatomical systems we must replicate include:

- **Skeletal System**: Provides structure and defines degrees of freedom
- **Muscular System**: Generates forces for movement
- **Nervous System**: Processes sensory information and coordinates motion
- **Sensory Organs**: Enable perception of the environment

### Degrees of Freedom (DOF)

A degree of freedom represents an independent axis of motion. The human body has approximately 244 DOF, but humanoid robots typically implement 20-50 for practical operation.

Common DOF allocations:

| Body Part | Human DOF | Typical Robot DOF |
|-----------|-----------|-------------------|
| Neck | 7 | 2-3 |
| Each Arm | 7 | 6-7 |
| Each Hand | 23 | 5-20 |
| Torso | 3 | 1-3 |
| Each Leg | 7 | 6 |
| Each Foot | 6 | 1-2 |

### Link-Joint Structure

Robots are modeled as a series of rigid **links** connected by **joints**:

- **Revolute Joints**: Allow rotation around an axis (like your elbow)
- **Prismatic Joints**: Allow linear sliding motion
- **Spherical Joints**: Allow rotation in multiple axes (like your shoulder, simplified)

## Kinematics

Kinematics describes motion without considering the forces that cause it.

### Forward Kinematics

Forward kinematics calculates the position and orientation of the end-effector (like a hand) given joint angles.

For a simple 2-link planar arm:

$$
x = L_1 \cos(\theta_1) + L_2 \cos(\theta_1 + \theta_2)
$$

$$
y = L_1 \sin(\theta_1) + L_2 \sin(\theta_1 + \theta_2)
$$

Where:
- $L_1, L_2$ are link lengths
- $\theta_1, \theta_2$ are joint angles
- $x, y$ is the end-effector position

### Inverse Kinematics

Inverse kinematics solves the opposite problem: given a desired end-effector position, what joint angles achieve it?

This is more complex because:
- Multiple solutions may exist
- Some positions may be unreachable
- Singularities can cause mathematical difficulties

Common solution methods:
1. **Analytical Methods**: Derive closed-form solutions (fast but only for simple kinematic chains)
2. **Numerical Methods**: Iteratively converge to solutions (general but slower)
3. **Learning-Based**: Train neural networks to approximate inverse kinematics

### The Jacobian Matrix

The Jacobian relates joint velocities to end-effector velocities:

$$
\dot{x} = J(\theta) \dot{\theta}
$$

Where:
- $\dot{x}$ is the end-effector velocity vector
- $J(\theta)$ is the Jacobian matrix (depends on current configuration)
- $\dot{\theta}$ is the joint velocity vector

The Jacobian is crucial for:
- Velocity control
- Force transformation
- Identifying singularities (when $\det(J) = 0$)

## Dynamics

Dynamics describes how forces and torques produce motion.

### Equations of Motion

The general form of robot dynamics follows from Lagrangian mechanics:

$$
M(\theta)\ddot{\theta} + C(\theta, \dot{\theta})\dot{\theta} + g(\theta) = \tau
$$

Where:
- $M(\theta)$ is the mass matrix
- $C(\theta, \dot{\theta})$ contains Coriolis and centrifugal terms
- $g(\theta)$ is the gravity vector
- $\tau$ is the vector of applied joint torques

### Mass and Inertia

Each link has:
- **Mass**: Resistance to linear acceleration
- **Moment of Inertia**: Resistance to angular acceleration
- **Center of Mass**: Point where mass is effectively concentrated

These properties, combined with the kinematic structure, determine how the robot responds to applied forces.

### Ground Reaction Forces

For legged robots, interaction with the ground is critical. The ground reaction force (GRF) must:
- Support the robot's weight
- Enable forward propulsion
- Maintain balance

The relationship between GRF and center of mass is governed by:

$$
\sum F_{GRF} = m\ddot{x}_{CoM}
$$

## Stability and Balance

### Static Stability

A robot is statically stable when its center of mass (CoM) projection falls within the support polygon (the convex hull of contact points).

```
      CoM projection
           ●
    ┌──────────────┐
    │              │ Support
    │   ●    ●     │ Polygon
    └──────────────┘
       Left  Right
       foot  foot
```

### Dynamic Stability

During walking, the CoM may temporarily leave the support polygon. Dynamic stability uses momentum to maintain balance.

### Zero Moment Point (ZMP)

The ZMP is the point on the ground where the sum of all moments (except vertical) is zero. For stable walking:

- ZMP must remain within the support polygon
- This constraint drives most walking trajectory planners

### Linear Inverted Pendulum Model (LIPM)

A simplified model for walking treats the robot as an inverted pendulum:

$$
\ddot{x} = \omega^2(x - p)
$$

Where:
- $x$ is the CoM horizontal position
- $p$ is the ZMP position
- $\omega = \sqrt{g/z_c}$ with $z_c$ being the CoM height

This simplified model enables efficient trajectory planning.

## Control Systems

### PID Control

The Proportional-Integral-Derivative (PID) controller is foundational:

$$
u(t) = K_p e(t) + K_i \int e(t)dt + K_d \frac{de(t)}{dt}
$$

Where:
- $e(t)$ is the error (desired - actual)
- $K_p, K_i, K_d$ are tuning gains

### Computed Torque Control

This method uses the dynamic model to compute feedforward torques:

$$
\tau = M(\theta)(\ddot{\theta}_d + K_d\dot{e} + K_pe) + C(\theta,\dot{\theta})\dot{\theta} + g(\theta)
$$

This cancels nonlinear dynamics, leaving simple error dynamics.

### Operational Space Control

Control in task space (Cartesian coordinates) rather than joint space:

1. Define desired behavior in task space
2. Use the Jacobian to transform to joint commands
3. Handle redundancy through null-space projection

### Hierarchical Control

Modern humanoids use hierarchical control:

1. **High Level**: Task planning and decision making
2. **Mid Level**: Motion planning and trajectory generation
3. **Low Level**: Joint position/velocity/torque control

## Walking Gaits

### Gait Cycle

A walking gait cycle consists of:
- **Stance Phase**: Foot in contact with ground (~60%)
- **Swing Phase**: Foot moving through air (~40%)

Key events:
1. Heel strike
2. Foot flat
3. Mid-stance
4. Heel off
5. Toe off
6. Mid-swing

### Gait Parameters

- **Step Length**: Distance between successive foot placements
- **Step Width**: Lateral distance between feet
- **Cadence**: Steps per minute
- **Walking Speed**: Step length × cadence

### Types of Walking

1. **Quasi-static Walking**: Always statically stable (slow)
2. **Dynamic Walking**: Uses momentum (natural human walking)
3. **Running**: Flight phases with no ground contact

## Summary

The foundations of humanoid robotics rest on understanding:
- Kinematic structure and degrees of freedom
- Forward and inverse kinematics
- Dynamic equations of motion
- Stability criteria (static and dynamic)
- Control system design
- Walking gait fundamentals

These concepts form the basis for designing robots that can move safely and effectively in human environments.

## Key Equations

| Concept | Equation |
|---------|----------|
| Forward Kinematics | $x = f(\theta)$ |
| Jacobian Relation | $\dot{x} = J(\theta)\dot{\theta}$ |
| Dynamics | $M\ddot{\theta} + C\dot{\theta} + g = \tau$ |
| LIPM | $\ddot{x} = \omega^2(x-p)$ |
| PID Control | $u = K_pe + K_i\int e + K_d\dot{e}$ |

## Review Questions

1. What is the difference between forward and inverse kinematics?
2. Why is the ZMP important for walking robots?
3. How does computed torque control simplify the control problem?
4. What distinguishes dynamic walking from quasi-static walking?
