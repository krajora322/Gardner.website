
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from PIL import Image
import io
import logging
from datetime import datetime
import os
# Install required packages
import subprocess
import sys

def install_requirements():
    packages = [
        'tensorflow',
        'opencv-python',
        'pillow',
        'numpy'
    ]
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}")

# Run installation
install_requirements()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('plant_diagnosis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load environment variables
MODEL_PATH = os.getenv('MODEL_PATH', 'plant_disease_model.h5')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load the model only once at startup
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    model = None

DISEASE_CLASSES = [
    'Healthy',
    'Bacterial Leaf Blight',
    'Leaf Spot', 
    'Powdery Mildew',
    'Rust',
    'Early Blight',
    'Late Blight'
]

class PlantDiagnosisError(Exception):
    """Custom exception for plant diagnosis errors"""
    pass

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_bytes, target_size=(224, 224)):
    """
    Preprocess the uploaded image for model prediction
    
    Args:
        image_bytes: Raw image bytes
        target_size: Target size for model input (default: 224x224)
        
    Returns:
        Preprocessed numpy array ready for model prediction
    """
    try:
        # Convert bytes to image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert RGBA to RGB if necessary
        if image.mode == 'RGBA':
            image = image.convert('RGB')
            
        # Resize to model input size
        image = image.resize(target_size, Image.LANCZOS)
        
        # Convert to numpy array and normalize
        img_array = np.array(image) / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
        
    except Exception as e:
        logger.error(f"Image preprocessing error: {str(e)}")
        raise PlantDiagnosisError("Failed to process image")

@app.route('/api/diagnose', methods=['POST'])
def diagnose_plant():
    """
    Endpoint for plant disease diagnosis
    
    Returns:
        JSON response with diagnosis results or error message
    """
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file uploaded'}), 400
            
        image_file = request.files['image']
        
        if not image_file.filename or not allowed_file(image_file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
            
        # Read and preprocess image
        image_bytes = image_file.read()
        processed_image = preprocess_image(image_bytes)
        
        # Save original image
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_path = os.path.join(UPLOAD_FOLDER, f'plant_{timestamp}.jpg')
        with open(save_path, 'wb') as f:
            f.write(image_bytes)
        
        # Get model prediction
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
            
        predictions = model.predict(processed_image)
        predicted_class_idx = np.argmax(predictions[0])
        predicted_class = DISEASE_CLASSES[predicted_class_idx]
        confidence = float(np.max(predictions[0]))
        
        # Get treatment recommendations
        recommendations = get_treatment_recommendations(predicted_class)
        
        # Log the diagnosis
        logger.info(f"Diagnosis complete - Disease: {predicted_class}, Confidence: {confidence:.2f}")
        
        return jsonify({
            'diagnosis': predicted_class,
            'confidence': confidence,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        })
        
    except PlantDiagnosisError as e:
        logger.error(f"Diagnosis error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

def get_treatment_recommendations(disease):
    """
    Get detailed treatment recommendations based on diagnosed disease
    
    Args:
        disease: Diagnosed plant disease
        
    Returns:
        List of treatment recommendations
    """
    recommendations = {
        'Healthy': [
            'Continue regular maintenance and monitoring',
            'Water plants at soil level during morning hours',
            'Maintain proper spacing between plants',
            'Regular pruning to improve air circulation',
            'Monitor for early signs of pest infestation'
        ],
        'Bacterial Leaf Blight': [
            'Immediately remove and destroy infected plant material',
            'Apply copper-based bactericide according to instructions',
            'Improve air circulation between plants',
            'Avoid overhead watering and working with wet plants',
            'Sanitize gardening tools after use'
        ],
        'Leaf Spot': [
            'Remove and dispose of infected leaves properly',
            'Apply appropriate fungicide treatment',
            'Maintain proper plant spacing',
            'Water at soil level to keep leaves dry',
            'Improve air circulation around plants'
        ],
        'Powdery Mildew': [
            'Apply sulfur-based fungicide at first sign of infection',
            'Increase air circulation around plants',
            'Reduce humidity levels if possible',
            'Remove severely infected plant parts',
            'Consider resistant varieties for future planting'
        ],
        'Rust': [
            'Remove and destroy infected plant material',
            'Apply appropriate fungicide treatment',
            'Improve air circulation between plants',
            'Avoid overhead watering',
            'Clean and disinfect gardening tools'
        ],
        'Early Blight': [
            'Remove infected leaves and dispose properly',
            'Apply fungicide preventively',
            'Maintain proper plant spacing',
            'Use mulch to prevent soil splash',
            'Rotate crops in future seasons'
        ],
        'Late Blight': [
            'Remove and destroy all infected plant material',
            'Apply protective fungicide before infection',
            'Improve soil drainage',
            'Avoid overhead irrigation',
            'Consider resistant varieties for future planting'
        ]
    }
    
    return recommendations.get(disease, ['Please consult a plant specialist for accurate diagnosis and treatment'])

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000))
    )

