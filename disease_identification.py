# Description: This file contains the DiseaseIdentification class which is responsible for identifying plant diseases using a pre-trained model and storing the results in a database. It also provides a method to display information about the detected disease.
# disease_identification.py
import os
from db import create_connection
import tensorflow as tf
from PIL import Image
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

import numpy as np

class DiseaseIdentification:
    def __init__(self):
        self.confidence_threshold = 0.7
        self.model = None
        self.classes = []
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        self.load_latest_model()
        
    
    def load_latest_model(self):
        """Load the latest active model and its classes from the database"""
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # First load classes
                cursor.execute('SELECT class_name FROM model_classes ORDER BY class_index')
                self.classes = [row[0] for row in cursor.fetchall()]
                
                if not self.classes:
                    print("No classes found in database!")
                    return

                # Get the latest active model
                cursor.execute('''
                    SELECT model_path 
                    FROM model_versions 
                    WHERE is_active = 1 
                    ORDER BY training_date DESC 
                    LIMIT 1
                ''')
                result = cursor.fetchone()
                
                if result:
                    model_path = result[0]
                    if not os.path.exists(model_path):
                        print(f"Model file not found at: {model_path}")
                        return
                        
                    try:
                        self.model = tf.keras.models.load_model(model_path)
                        print(f"Model loaded successfully with {len(self.classes)} classes!")
                        print("\nAvailable classes:")
                        for i, class_name in enumerate(self.classes, 1):
                            print(f"{i}. {class_name}")
                    except Exception as e:
                        print(f"Error loading model: {e}")
                        self.model = None
                else:
                    print("No active model found in database!")
            except Exception as e:
                print(f"Database error: {e}")
            finally:
                conn.close()
    
    def verify_model_loaded(self):
        """Verify if model and classes are properly loaded"""
        if self.model is None:
            print("Error: Model not loaded!")
            return False
        if not self.classes:
            print("Error: No classes loaded!")
            return False
        return True
    def img_to_pred(self, image_path):
        try:
            new_size = (224, 224)
            image = Image.open(image_path)
            image = image.resize(new_size)
            image = np.asarray(image)
            image = tf.expand_dims(image, 0)
            return image
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None

    def predict_disease(self, preprocessed_image):
        try:
            # Make prediction
            predictions = self.model.predict(preprocessed_image)
            # Get the index of the highest confidence prediction
            predicted_class_index = np.argmax(predictions)
            # Get the confidence score
            confidence = float(predictions[0][predicted_class_index])
            
            return {
                "name": self.classes[predicted_class_index],
                "confidence": confidence,
                "all_predictions": {self.classes[i]: float(predictions[0][i]) 
                                  for i in range(len(self.classes))}
            }
        except Exception as e:
            print(f"Error making prediction: {e}")
            return None
    def process_image(self, image_path, user_id):
        if not self.verify_model_loaded():
            return {"error": "Model or classes not loaded properly"}

        if not os.path.exists(image_path):
            return {"error": "Image file not found"}

        # Preprocess the image
        processed_image = self.img_to_pred(image_path) 
        if processed_image is None:
            return {"error": "Error preprocessing image"}

        # Get prediction
        prediction = self.predict_disease(processed_image)
        if prediction is None:
            return {"error": "Error making prediction"}

        # Store the result in database
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO disease_predictions 
                    (user_id, image_path, disease_name, confidence)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, image_path, prediction['name'], prediction['confidence']))
                conn.commit()
            finally:
                conn.close()

        return prediction

    def display_disease_info(self, disease_name):
        # Extract crop and disease from the prediction
        parts = disease_name.split('___')
        crop = parts[0].replace('_', ' ')
        condition = parts[1].replace('_', ' ')
        
        print(f"\nDisease Information:")
        print(f"Crop: {crop}")
        print(f"Condition: {condition}")
        
        if 'healthy' in condition.lower():
            print("Status: The plant appears to be healthy!")
            print("Recommendation: Continue with regular care and maintenance.")
        else:
            print("Status: Disease detected!")
            print(f"Disease: {condition}")
            # print("Recommendation: Consider consulting with an agricultural expert for treatment options.")

    def display_image(self, image_path):
        try:
            # Read and display the image using matplotlib
            img = mpimg.imread(image_path)
            plt.figure(figsize=(10, 8))
            plt.imshow(img)
            plt.axis('off')  # Hide axes
            plt.title('Uploaded Image')
            plt.show()
        except Exception as e:
            print(f"Error displaying image: {e}")
            
    def check_model_file(self, model_path):
        """Check if model file exists and is accessible"""
        if not os.path.exists(model_path):
            print(f"Error: Model file not found at {model_path}")
            return False
        try:
            # Try to open the file to verify permissions
            with open(model_path, 'rb') as f:
                pass
            return True
        except Exception as e:
            print(f"Error accessing model file: {e}")
            return False
    def handle_image_upload(self, user_id):
        
        print("\n=== Disease Identification ===")
        # Verify model and classes are loaded
        if not self.verify_model_loaded():
            print("Please contact administrator. System not properly initialized.")
            return
            
        print(f"Model ready with {len(self.classes)} classes")
        while True:
            image_path = input("Enter the path to your image file (or 'q' to quit): ").strip('"').strip("'")
            if image_path.lower() == 'q':
                return
            
            if not os.path.exists(image_path):
                print("File not found. Please enter a valid path.")
                continue

            # Display the image
            print("\nDisplaying uploaded image...")
            self.display_image(image_path)

            print("\nProcessing image...")
            prediction = self.process_image(image_path, user_id)
            
            if "error" in prediction:
                print(f"Error: {prediction['error']}")
                continue
            
            print(f"\nPrediction Results:")
            print(f"Disease: {prediction['name']}")
            print(f"Confidence: {prediction['confidence'] * 100:.2f}%")
            
            # Display top 3 predictions
            print("\nTop 3 Possibilities:")
            sorted_predictions = sorted(prediction['all_predictions'].items(), 
                                     key=lambda x: x[1], reverse=True)[:3]
            for disease, conf in sorted_predictions:
                print(f"{disease}: {conf * 100:.2f}%")
            
            if prediction['confidence'] < self.confidence_threshold:
                print("\nWarning: Low confidence prediction.")
                print("The AI system is uncertain about this plant disease diagnosis. \n Recommendation: Please consult an Expert.")
                return
            else:
                self.display_disease_info(prediction['name'])
            
            print("\nWould you like to process another image? (y/n)")
            if input().lower() != 'y':
                break


