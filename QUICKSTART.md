# Quick Start Checklist

## Phase 1: Setup (Do This Now) ⬇️

### Step 1: Install Unity Hub
- [ ] Download from: https://unity.com/download
- [ ] Install Unity Hub
- [ ] Sign in with Unity account (free)

### Step 2: Install Unity Editor
- [ ] In Unity Hub → Installs → Install Editor
- [ ] Choose **Unity 2022.3 LTS** (Long Term Support)
- [ ] Add modules:
  - [ ] Windows Build Support (IL2CPP)
  - [ ] Android Build Support (for Quest later)
  - [ ] Android SDK & NDK Tools
  - [ ] OpenJDK

### Step 3: Create VR Project
- [ ] Unity Hub → Projects → New Project
- [ ] Template: **3D (URP)** (Universal Render Pipeline)
- [ ] Project Name: `VR_FirstResponder`
- [ ] Location: `c:\Users\SafaaSalman\Desktop\Uni\Thesis\Code\VR_FirstResponder`
- [ ] Click Create Project

### Step 4: Install XR Packages (In Unity Editor)
- [ ] Window → Package Manager
- [ ] Change dropdown from "Packages: In Project" to "Unity Registry"
- [ ] Search and install:
  - [ ] **XR Interaction Toolkit** (click Install)
  - [ ] **XR Plugin Management** (usually auto-installed)
  - [ ] **OpenXR Plugin**
  
### Step 5: Import XR Samples
- [ ] In Package Manager, find XR Interaction Toolkit
- [ ] Expand "Samples" section
- [ ] Click "Import" next to:
  - [ ] **Starter Assets**
  - [ ] **XR Device Simulator**

### Step 6: Configure XR Settings
- [ ] Edit → Project Settings
- [ ] Left panel: XR Plug-in Management
- [ ] Windows tab: Check **OpenXR**
- [ ] Click the ⚠️ warning icon if any, fix issues
- [ ] Under OpenXR → Interaction Profiles, add:
  - [ ] Oculus Touch Controller Profile

### Step 7: Test XR Device Simulator
- [ ] In Project window, search for "XR Device Simulator"
- [ ] Drag the prefab into your Hierarchy
- [ ] Press Play
- [ ] Use WASD to move, mouse to look
- [ ] Press T or Y to toggle controller simulation
- [ ] 🎉 You're simulating VR!

---

## When Done With Phase 1

Open `PROMPTS.md` and copy **PROMPT 2** to continue building your VR scene.

---

## Estimated Time

| Step | Time |
|------|------|
| Download & Install Unity Hub | 5 min |
| Install Unity Editor + modules | 20-40 min |
| Create project & install packages | 10 min |
| Configure XR & test simulator | 10 min |
| **Total** | **~1 hour** |

---

## Troubleshooting

### "XR Interaction Toolkit not found"
→ Make sure you're looking in "Unity Registry" not "In Project"

### "OpenXR initialization failed"
→ Normal without headset! XR Device Simulator bypasses this.

### "XR Device Simulator controls not working"
→ Make sure the prefab is in your scene and Play mode is active
→ Click in the Game view to give it focus

### "Project takes forever to create"
→ First project setup imports many assets. This is normal.

