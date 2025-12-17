# Dataset Sources & Download Links

## Emergency Vehicle Detection

### Option 1: Roboflow - Ambulance and Firefighter (Recommended)
- **URL**: https://universe.roboflow.com/ambulance-7s7u4/ambulance-and-firefighter
- **Format**: YOLO, COCO, Pascal VOC
- **Download**: Free with Roboflow account

### Option 2: Roboflow - Emergency Vehicle Detection
- **URL**: https://universe.roboflow.com/nkphan/emergency-vehicle-detection-b4e0u
- **Classes**: ambulance, police, firetruck
- **Format**: Multiple export options

### Option 3: GitHub - Emergency Vehicles (20,000 images)
- **URL**: https://github.com/sovit-123/Emergency-Vehicles-on-Road-Networks
- **Size**: ~20,000 images
- **Classes**: ambulance, police, fire truck

### Option 4: Kaggle - Ambulance Dataset
- **URL**: https://www.kaggle.com/datasets/abhisheksinghblr/ambulance-dataset
- **Use Case**: Ambulance vs non-ambulance classification

---

## Fire & Smoke Detection

### Option 1: Kaggle - Fire and Smoke Dataset (Recommended)
- **URL**: https://www.kaggle.com/datasets/dataclusterlabs/fire-and-smoke-dataset
- **Size**: 7,000+ images
- **Classes**: fire, smoke

### Option 2: Roboflow - Fire Smoke Detection
- **URL**: https://universe.roboflow.com/fire-dgsxu/fire-smoke-detection-ujxxq
- **Format**: Annotated for YOLO
- **Classes**: fire, smoke

### Option 3: Kaggle - Fire Detection Image Dataset
- **URL**: https://www.kaggle.com/datasets/phylake1337/fire-dataset
- **Use Case**: Binary fire classification

---

## PPE / Safety Gear Detection

### Option 1: Kaggle - Safety Helmet and Reflective Jacket
- **URL**: https://www.kaggle.com/datasets/mugheesahmad/safety-helmet-and-reflective-jacket-dataset
- **Classes**: helmet, vest, person

### Option 2: Ultralytics Construction PPE
- **URL**: https://docs.ultralytics.com/datasets/detect/construction-site-safety/
- **Classes**: helmet, vest, gloves, boots, goggles, missing PPE
- **Size**: Comprehensive construction site dataset

### Option 3: Roboflow - PPE Detection
- **URL**: https://universe.roboflow.com/roboflow-universe-projects/construction-site-safety
- **Format**: Ready for YOLO training

---

## Scene Images (For VR Backgrounds/Assets)

### Pixabay - Free Emergency Images
- **URL**: https://pixabay.com/images/search/emergency%20response/
- **License**: Free for commercial use (check individual images)
- **Use Case**: Reference images, VR environment textures

### Pexels - Emergency Services
- **URL**: https://www.pexels.com/search/emergency/
- **License**: Free to use

---

## Download Instructions

### For Roboflow Datasets:
1. Create free account at roboflow.com
2. Navigate to dataset URL
3. Click "Download" → Select format (YOLO v8 recommended)
4. Download ZIP and extract

### For Kaggle Datasets:
1. Create free account at kaggle.com
2. Navigate to dataset URL
3. Click "Download" button
4. Or use Kaggle CLI: `kaggle datasets download -d <dataset-path>`

### For GitHub Datasets:
1. Clone repository: `git clone <repo-url>`
2. Or download ZIP from GitHub

---

## Recommended Starting Dataset

For your thesis, I recommend starting with:

1. **Fire/Smoke**: Kaggle Fire and Smoke Dataset
   - Well-annotated, good size
   - Relevant for emergency training scenarios

2. **Emergency Vehicles**: Roboflow Emergency Vehicle Detection
   - Easy to download in YOLO format
   - Multiple vehicle types

---

## Dataset Organization

After downloading, organize like this:

```
c:\Users\SafaaSalman\Desktop\Uni\Thesis\Code\
├── datasets/
│   ├── fire_smoke/
│   │   ├── train/
│   │   │   ├── images/
│   │   │   └── labels/
│   │   ├── valid/
│   │   │   ├── images/
│   │   │   └── labels/
│   │   └── test/
│   │       ├── images/
│   │       └── labels/
│   ├── emergency_vehicles/
│   │   ├── train/
│   │   │   ├── images/
│   │   │   └── labels/
│   │   └── ...
│   └── ppe/
│       └── ...
├── models/
│   └── (trained models go here)
└── VR_FirstResponder/
    └── (Unity project)
```

