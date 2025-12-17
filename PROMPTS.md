# Development Prompts - Copy & Paste These One at a Time

Use these prompts after completing the previous phase. Each builds on the last.

---

## ✅ PROMPT 1 (CURRENT) - Initial Setup
You've already done this! Follow the README.md to:
1. Install Unity Hub + Unity 2022.3 LTS
2. Create new 3D (URP) project named "VR_FirstResponder"
3. Install XR Interaction Toolkit via Package Manager
4. Import Starter Assets + XR Device Simulator samples

**When done, come back and paste PROMPT 2.**

---

## 📋 PROMPT 2 - Create VR Player Rig & Basic Scene

```
I've installed Unity with XR Interaction Toolkit and imported the samples.

Now help me:
1. Create a basic VR scene with XR Origin (player rig)
2. Set up XR Device Simulator so I can test with keyboard/mouse
3. Add a ground plane and some basic grabbable objects (cubes)
4. Set up teleportation locomotion

Give me step-by-step Unity Editor instructions + any scripts needed.
The project is at: c:\Users\SafaaSalman\Desktop\Uni\Thesis\Code\VR_FirstResponder
```

---

## 📋 PROMPT 3 - First Responder Equipment & Interactions

```
My VR scene works with XR Device Simulator. I can teleport and grab objects.

Now help me add first responder training elements:
1. Create an equipment station with tools (fire extinguisher, first aid kit, radio)
2. Make each tool have specific interactions (spray, open, talk button)
3. Add UI tooltips when looking at objects
4. Create a simple scenario flow (start → get equipment → reach victim → complete)

Project: c:\Users\SafaaSalman\Desktop\Uni\Thesis\Code\VR_FirstResponder
```

---

## 📋 PROMPT 4 - Emergency Environment & Hazards

```
I have basic equipment interactions working.

Now help me create an emergency scenario environment:
1. Building interior with fire/smoke particle effects
2. Victim NPCs that need assistance
3. Hazard zones (fire spread, structural danger indicators)
4. Audio feedback (alarms, radio chatter, ambient sounds)
5. Simple AI for fire spread over time

Project: c:\Users\SafaaSalman\Desktop\Uni\Thesis\Code\VR_FirstResponder
```

---

## 📋 PROMPT 5 - Computer Vision Dataset Preparation

```
My VR training scenario is playable.

Now help me prepare for AI/computer vision integration:
1. Set up a Python environment for ML (conda or venv)
2. Download and organize these datasets:
   - Emergency vehicle detection (from Roboflow)
   - Fire/smoke detection (from Kaggle)
3. Create a simple YOLOv8 training script
4. Export model for Unity (ONNX format)

Working directory: c:\Users\SafaaSalman\Desktop\Uni\Thesis\Code
```

---

## 📋 PROMPT 6 - Unity + AI Integration

```
I have a trained ONNX model for fire/smoke detection.

Now help me integrate it into Unity:
1. Install Unity Barracuda (neural network inference)
2. Create a script that captures VR camera view
3. Run inference on the captured image
4. Display detection results in VR (bounding boxes, labels)
5. Trigger events based on detections (e.g., "Fire detected ahead!")

Project: c:\Users\SafaaSalman\Desktop\Uni\Thesis\Code\VR_FirstResponder
```

---

## 📋 PROMPT 7 - Meta XR Simulator Testing

```
My VR app works well with XR Device Simulator.

Now help me set up Meta XR Simulator for Quest-like testing:
1. Download and install Meta XR Simulator
2. Configure Unity to use it as OpenXR runtime
3. Test Quest-specific features (hand tracking, passthrough)
4. Document any issues for real headset testing later

Project: c:\Users\SafaaSalman\Desktop\Uni\Thesis\Code\VR_FirstResponder
```

---

## 📋 PROMPT 8 - Training Metrics & Scoring

```
I want to add training assessment to my VR simulation.

Help me create:
1. Performance tracking (time, accuracy, procedure order)
2. Scoring system based on first responder protocols
3. Session recording and playback
4. Results summary UI
5. Export training data to CSV/JSON

Project: c:\Users\SafaaSalman\Desktop\Uni\Thesis\Code\VR_FirstResponder
```

---

## 📋 PROMPT 9 - Polish & Build

```
My VR first responder training is feature complete.

Help me polish and build:
1. Add menu system (start, settings, quit)
2. Optimize performance for Quest 2/3
3. Build for Windows (Oculus Link)
4. Build for Android (Quest standalone)
5. Create user documentation

Project: c:\Users\SafaaSalman\Desktop\Uni\Thesis\Code\VR_FirstResponder
```

---

## Notes

- **Skip prompts** if you don't need certain features
- **Modify prompts** to match your specific thesis requirements
- **Ask clarifying questions** in any prompt if something is unclear
- Each prompt assumes the previous one is complete

