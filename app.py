from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import face_recognition
import cv2
import numpy as np
import os
import torch
import torch.nn.functional as F
from PIL import Image
import torchvision.transforms as transforms
from models.slip_model import SLIPNet
import base64
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
db = SQLAlchemy(app)

# Initialize liveness detection model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
liveness_model = None
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                       std=[0.229, 0.224, 0.225])
])

def load_liveness_model():
    global liveness_model
    if liveness_model is None:
        model_path = 'best_liveness_model.pth'
        if os.path.exists(model_path):
            liveness_model = SLIPNet(num_classes=2)
            if torch.cuda.is_available():
                liveness_model.load_state_dict(torch.load(model_path))
            else:
                liveness_model.load_state_dict(torch.load(model_path, map_location='cpu'))
            liveness_model.to(device)
            liveness_model.eval()
            print("Liveness detection model loaded successfully")
        else:
            print("Warning: Liveness detection model not found")
    return liveness_model

def check_liveness(image_data):
    """Check if the face in the image is live or spoof"""
    model = load_liveness_model()
    if model is None:
        return True, 1.0  # Assume live if model not available
    
    try:
        # Convert base64 to PIL Image
        if isinstance(image_data, str):
            # Remove data URL prefix if present
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        else:
            image = Image.fromarray(image_data).convert('RGB')
        
        # Preprocess image
        input_tensor = transform(image)
        if not isinstance(input_tensor, torch.Tensor):
            input_tensor = torch.from_numpy(np.array(input_tensor)).float()
        input_tensor = input_tensor.unsqueeze(0).to(device)
        
        # Run inference
        with torch.no_grad():
            outputs, _ = model(input_tensor)
            probabilities = F.softmax(outputs, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0, int(predicted_class)].item()
        
        # Class 0 is live, Class 1 is spoof
        is_live = predicted_class == 0
        return is_live, confidence
        
    except Exception as e:
        print(f"Error in liveness detection: {e}")
        return True, 0.5  # Assume live on error

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    face_encoding = db.Column(db.PickleType, nullable=False)
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    liveness_score = db.Column(db.Float, nullable=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'photo' not in data or 'name' not in data:
            return jsonify({'error': 'Missing photo or name'}), 400
        
        try:
            # Decode base64 image
            image_data = data['photo'].split(',')[1] if ',' in data['photo'] else data['photo']
            image_bytes = base64.b64decode(image_data)
            
            # Check liveness
            image = Image.open(io.BytesIO(image_bytes))
            is_live, liveness_score = check_liveness(np.array(image))
            
            if not is_live:
                return jsonify({'error': 'Spoof detected! Please use a real face.'}), 400
            
            # Convert to numpy array for face recognition
            image_np = np.array(image)
            
            # Get face encoding
            face_encodings = face_recognition.face_encodings(image_np)
            
            if not face_encodings:
                return jsonify({'error': 'No face detected in the image'}), 400
            
            # Create new student record
            student = Student()
            student.name = data['name']
            student.face_encoding = face_encodings[0]
            db.session.add(student)
            db.session.commit()
            
            return jsonify({'message': f'Student {data["name"]} registered successfully!'})
            
        except Exception as e:
            return jsonify({'error': f'Registration failed: {str(e)}'}), 400
    
    return render_template('register.html')

@app.route('/mark_attendance', methods=['GET', 'POST'])
def mark_attendance():
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'photo' not in data:
            return jsonify({'error': 'No photo uploaded'}), 400
        
        try:
            # Decode base64 image
            image_data = data['photo'].split(',')[1] if ',' in data['photo'] else data['photo']
            image_bytes = base64.b64decode(image_data)
            
            # Check liveness
            image = Image.open(io.BytesIO(image_bytes))
            is_live, liveness_score = check_liveness(np.array(image))
            
            if not is_live:
                return jsonify({'error': 'Spoof detected! Please use a real face.'}), 400
            
            # Convert to numpy array for face recognition
            image_np = np.array(image)
            
            # Get face encoding
            face_encodings = face_recognition.face_encodings(image_np)
            
            if not face_encodings:
                return jsonify({'error': 'No face detected in the image'}), 400
            
            # Get all students
            students = Student.query.all()
            known_face_encodings = [student.face_encoding for student in students]
            
            if not known_face_encodings:
                return jsonify({'error': 'No students registered in the system'}), 400
            
            # Compare faces
            matches = face_recognition.compare_faces(known_face_encodings, face_encodings[0])
            
            if True in matches:
                # Get the first matching student
                student_idx = matches.index(True)
                student = students[student_idx]
                
                # Check if attendance already marked for today
                today = datetime.utcnow().date()
                existing_attendance = Attendance.query.filter(
                    Attendance.student_id == student.id,
                    db.func.date(Attendance.date) == today
                ).first()
                
                if not existing_attendance:
                    # Mark attendance
                    attendance = Attendance()
                    attendance.student_id = student.id
                    attendance.liveness_score = liveness_score
                    db.session.add(attendance)
                    db.session.commit()
                    return jsonify({
                        'message': f'Attendance marked for {student.name}',
                        'student_name': student.name,
                        'liveness_score': liveness_score
                    })
                else:
                    return jsonify({
                        'message': f'Attendance already marked for {student.name} today',
                        'student_name': student.name
                    })
            else:
                return jsonify({'error': 'Face not recognized. Please register first.'}), 400
                
        except Exception as e:
            return jsonify({'error': f'Attendance marking failed: {str(e)}'}), 400
    
    return render_template('mark_attendance.html')

@app.route('/attendance_records')
def attendance_records():
    records = db.session.query(Attendance, Student).join(Student).order_by(Attendance.date.desc()).all()
    return render_template('attendance_records.html', records=records)

@app.route('/api/students')
def get_students():
    students = Student.query.all()
    return jsonify([{'id': s.id, 'name': s.name} for s in students])

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    with app.app_context():
        db.create_all()
    
    # Load liveness model on startup
    load_liveness_model()
    
    app.run(debug=True, host='0.0.0.0', port=5000) 