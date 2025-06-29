# Face Anti-Spoofing Attendance System - Minimal Version

A lightweight, ready-to-run attendance system with face recognition and liveness detection.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the System
```bash
python run.py
```

### 3. Open Browser
Go to: http://localhost:5000

## 📁 Project Structure
```
face-attendance-minimal/
├── app.py              # Main Flask application
├── run.py              # Startup script
├── requirements.txt    # Python dependencies
├── templates/          # Web interface
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── mark_attendance.html
│   └── attendance_records.html
└── models/
    └── slip_model.py   # AI model architecture
```

## 🎯 Features
- ✅ Face recognition for student identification
- ✅ Liveness detection (anti-spoofing)
- ✅ Real-time camera processing
- ✅ Modern web interface
- ✅ SQLite database
- ✅ Ready to run immediately

## 📱 Usage
1. **Register Students**: Upload photos with liveness detection
2. **Mark Attendance**: Use camera for automatic attendance
3. **View Records**: Check attendance history and statistics

## 🔧 Requirements
- Python 3.8+
- Webcam/camera
- Modern web browser

## 📝 Notes
- The system will work without the trained model file
- Database is created automatically on first run
- Camera permissions required in browser

---
**For full documentation and training scripts, see the complete repository.**
