# VR First Responder Training - Development Guide

## Overview
This project creates a VR first responder training simulation using Unity, developed **without requiring a VR headset** during initial development.

---

## 🚀 PHASE 1: Unity Setup (Current Phase)

### Step 1: Install Unity Hub & Unity Editor

1. **Download Unity Hub**: https://unity.com/download
2. **Install Unity Editor** (recommended version: **2022.3 LTS** or **6000.0 LTS**)
   - During installation, add these modules:
     - ✅ Windows Build Support
     - ✅ Android Build Support (for Quest deployment later)

### Step 2: Create New VR Project

1. Open Unity Hub → **New Project**
2. Select template: **3D (URP)** or **VR** template if available
3. Name: `VR_FirstResponder`
4. Location: This folder

### Step 3: Install Required Packages (Unity Package Manager)

Open **Window → Package Manager** and install:

```
1. XR Interaction Toolkit (latest stable)
2. XR Plugin Management
3. OpenXR Plugin
4. XR Device Simulator (comes with XR Interaction Toolkit samples)
```

**Detailed Steps:**
1. In Package Manager, click **+ → Add package by name**
2. Add: `com.unity.xr.interaction.toolkit`
3. After installation, expand "Samples" and import:
   - ✅ Starter Assets
   - ✅ XR Device Simulator

### Step 4: Configure XR Settings

1. Go to **Edit → Project Settings → XR Plug-in Management**
2. Enable: **OpenXR**
3. Under OpenXR settings, add interaction profiles:
   - Oculus Touch Controller Profile
   - Meta Quest Touch Pro Controller Profile

### Step 5: Set Up XR Device Simulator

1. In Project window, navigate to:
   `Packages/XR Interaction Toolkit/Samples/XR Device Simulator`
2. Drag **XR Device Simulator** prefab into your scene
3. Now you can simulate VR using keyboard/mouse!

---

## 🎮 XR Device Simulator Controls

| Action | Control |
|--------|---------|
| Move HMD | WASD + Mouse |
| Rotate HMD | Right-click + Mouse |
| Toggle Left Controller | T |
| Toggle Right Controller | Y |
| Move Controller | Mouse |
| Grip Button | G |
| Trigger Button | Left Mouse Button |
| Primary Button (A/X) | B |
| Secondary Button (B/Y) | N |

---

## 📁 Project Structure

```
VR_FirstResponder/
├── Assets/
│   ├── Scenes/
│   │   ├── MainMenu.unity
│   │   ├── TrainingScenario_Fire.unity
│   │   └── TrainingScenario_Medical.unity
│   ├── Scripts/
│   │   ├── Core/
│   │   ├── Interactions/
│   │   ├── AI/
│   │   └── UI/
│   ├── Prefabs/
│   │   ├── Player/
│   │   ├── Equipment/
│   │   └── Environment/
│   ├── Materials/
│   ├── Models/
│   └── Audio/
├── Packages/
└── ProjectSettings/
```

---

## 🔥 PHASE 2: Basic VR Scene (Next Prompt)

After Unity is set up, we'll create:
- XR Origin (player rig)
- Basic environment
- Grabbable objects
- Teleportation locomotion

---

## 🤖 PHASE 3: Computer Vision Integration (Later)

We'll integrate object detection for:
- Emergency vehicle detection
- Fire/smoke detection
- PPE detection

---

## 📦 PHASE 4: Meta XR Simulator (Optional)

For Quest-like testing without hardware:
1. Download Meta XR Simulator: https://developer.oculus.com/downloads/package/meta-xr-simulator/
2. Set as active OpenXR runtime
3. Test Quest-specific features on PC

---

## 📚 Resources

- [XR Interaction Toolkit Docs](https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@latest)
- [XR Device Simulator Guide](https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@2.5/manual/xr-device-simulator.html)
- [Meta XR Simulator](https://developer.oculus.com/documentation/unity/xrsim-intro/)
- [OpenXR Plugin](https://docs.unity3d.com/Packages/com.unity.xr.openxr@latest)

