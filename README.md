# 🐄 Smart Cow Shed Automation System

IoT-based smart cow shed built on **ESP32** — monitors and automates 
temperature, humidity, soil moisture, water level & lighting via a 
real-time WiFi web dashboard. Solar powered.

## 📊 System Architecture
![Block Diagram](block-diagram.jpg)

## 🏗️ 3D Model
![Cow Shed 3D View](shed-3d-1.jpg)
![Cow Shed 3D View](shed-3d-2.jpg)

## ✅ Features
- **Temperature & Humidity** monitoring via DHT11
- **Auto Fan cycling** (28–32°C) and **Sprinkler cycling** (>32°C)
- **Soil moisture monitoring** — 3 zones, auto irrigation
- **Water tank level** via Ultrasonic sensor — auto motor control
- **LDR-based smart lighting** — auto ON in dark
- **Solar Panel + Battery** powered system
- **Real-time IoT Web Dashboard** — auto-refreshes every 2 seconds
- **Manual override** for all actuators

## 🔌 Hardware
| Component | Purpose |
|---|---|
| ESP32 | Main Controller + WiFi |
| DHT11 | Temperature & Humidity |
| HC-SR04 Ultrasonic | Water tank level |
| LDR | Light sensing |
| Soil Moisture Sensors (x3) | Zone-wise irrigation |
| Relay Module (7-channel) | Fan, Sprinkler, Light, Motor, 3x Moisture |
| Solar Panel + Battery | Power supply |

## 📍 Pin Configuration
| Pin | Component |
|---|---|
| GPIO4 | DHT11 |
| GPIO34 | LDR |
| GPIO32/33 | Ultrasonic TRIG/ECHO |
| GPIO35/36/39 | Moisture Sensors 1/2/3 |
| GPIO27/26/25/14/15/2/5 | Relay outputs |

## 🌡️ Auto Control Logic
| Temperature | Action |
|---|---|
| ≤ 28°C | Fan OFF, Sprinkler OFF |
| 28–32°C | Fan cycling (30s ON/OFF) |
| > 32°C | Sprinkler cycling (30s ON/OFF) |

## 👩‍💻 Built By
**Tanvi Mohite** — ECE Final Year, DKTE Institute, Ichalkaranji
