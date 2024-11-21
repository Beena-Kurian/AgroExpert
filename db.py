# db.py
import sqlite3
from sqlite3 import Error

def create_connection():
    try:
        conn = sqlite3.connect('data/agroexpert.db')
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None
def init_database():
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            
            # Create Users table
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    email TEXT UNIQUE,
                    phone TEXT,
                    status TEXT DEFAULT 'active'
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS expert_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    scope TEXT,
                    specialization TEXT,
                    commodity TEXT,
                    region TEXT,
                    city TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            # Create Diseases table
            c.execute('''
                CREATE TABLE IF NOT EXISTS diseases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    symptoms TEXT,
                    treatment TEXT
                )
            ''')

            # Create Disease Predictions table
            c.execute('''
                CREATE TABLE IF NOT EXISTS disease_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    image_path TEXT,
                    disease_name TEXT,
                    confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            # Create NEW Consultations table with image_path included
            c.execute('''
                CREATE TABLE IF NOT EXISTS consultations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    farmer_id INTEGER,
                    expert_id INTEGER,
                    description TEXT,
                    image_path TEXT,
                    plant_name TEXT,
                    symptoms TEXT,
                    region TEXT,
                    date_noticed DATE,
                    treatments TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (farmer_id) REFERENCES users (id),
                    FOREIGN KEY (expert_id) REFERENCES users (id)
                )
            ''')

            # Create Consultation Responses table
            c.execute('''
                CREATE TABLE IF NOT EXISTS consultation_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    consultation_id INTEGER,
                    expert_id INTEGER,
                    expert_response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (consultation_id) REFERENCES consultations (id),
                    FOREIGN KEY (expert_id) REFERENCES users (id)
                )
            ''')

            # Create Rewards table
            c.execute('''
                CREATE TABLE IF NOT EXISTS rewards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    points INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            # Create Reward Transactions table
            c.execute('''
                CREATE TABLE IF NOT EXISTS reward_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT,
                    points INTEGER,
                    description TEXT,
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            # Create News table
            c.execute('''
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # For tracking ML model versions
            c.execute('''
                CREATE TABLE IF NOT EXISTS model_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_path TEXT NOT NULL,
                    version_number TEXT NOT NULL,
                    accuracy REAL,
                    total_classes INTEGER,
                    training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 0
                )
            ''')

            # For tracking unknown diseases
            c.execute('''
                CREATE TABLE IF NOT EXISTS unknown_diseases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reported_by_farmer_id INTEGER,
                    verified_by_expert_id INTEGER,
                    initial_image_path TEXT,
                    samples_folder_path TEXT,
                    description TEXT,
                    symptoms TEXT,
                    date_reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending', -- pending, samples_requested, samples_received, verified, training_in_progress, completed
                    admin_notes TEXT,
                    FOREIGN KEY (reported_by_farmer_id) REFERENCES users (id),
                    FOREIGN KEY (verified_by_expert_id) REFERENCES users (id)
                )
            ''')

            # For tracking disease samples collection
            c.execute('''
                CREATE TABLE IF NOT EXISTS disease_samples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unknown_disease_id INTEGER,
                    farmer_id INTEGER,
                    samples_zip_path TEXT,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending', -- pending, verified, rejected
                    expert_notes TEXT,
                    FOREIGN KEY (unknown_disease_id) REFERENCES unknown_diseases (id),
                    FOREIGN KEY (farmer_id) REFERENCES users (id)
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS model_classes (
                    class_index INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_name TEXT NOT NULL UNIQUE,
                    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            print("Database initialized successfully")
        except Error as e:
            print(f"Error creating tables: {e}")
        finally:
            conn.close()
    else:
        print("Error: Could not establish database connection")

def init_first_model():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Check if model version already exists
            cursor.execute('SELECT COUNT(*) FROM model_versions')
            count = cursor.fetchone()[0]
            
            if count == 0:  # Only insert if no model versions exist
                cursor.execute('''
                    INSERT INTO model_versions 
                    (model_path, version_number, accuracy, total_classes, 
                     description, is_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    "D:\Conestoga\prog_for_bigdata\PDD\AgroExpert\models\model_version1.h5",
                    "1.0",
                    0.95,  # Initial model accuracy
                    35,    # Initial model classes
                    "Initial model with 35 plant diseases",
                    1
                ))
                conn.commit()
                print("Initial model version recorded in database")
        except Exception as e:
            print(f"Error initializing model version: {e}")
        finally:
            conn.close()

def init_model_classes():
    # List of initial classes
    initial_classes = [
        'Apple___Apple_scab',
        'Apple___Cedar_apple_rust',
        'Apple___healthy',
        'Blueberry___healthy',
        'Cherry_(including_sour)___Powdery_mildew',
        'Cherry_(including_sour)___healthy',
        'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
        'Corn_(maize)___Common_rust_',
        'Corn_(maize)___Northern_Leaf_Blight',
        'Corn_(maize)___healthy',
        'Grape___Esca_(Black_Measles)',
        'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
        'Grape___healthy',
        'Orange___Haunglongbing_(Citrus_greening)',
        'Peach___healthy',
        'Pepper,_bell___Bacterial_spot',
        'Pepper,_bell___healthy',
        'Potato___Early_blight',
        'Potato___Late_blight',
        'Potato___healthy',
        'Raspberry___healthy',
        'Soybean___healthy',
        'Squash___Powdery_mildew',
        'Strawberry___Leaf_scorch',
        'Strawberry___healthy',
        'Tomato___Bacterial_spot',
        'Tomato___Early_blight',
        'Tomato___Late_blight',
        'Tomato___Leaf_Mold',
        'Tomato___Septoria_leaf_spot',
        'Tomato___Spider_mites Two-spotted_spider_mite',
        'Tomato___Target_Spot',
        'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
        'Tomato___Tomato_mosaic_virus',
        'Tomato___healthy'
    ]
    
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Check if classes already exist
            cursor.execute('SELECT COUNT(*) FROM model_classes')
            if cursor.fetchone()[0] == 0:
                # Insert initial classes
                for class_name in initial_classes:
                    cursor.execute('''
                        INSERT INTO model_classes (class_name) 
                        VALUES (?)
                    ''', (class_name,))
                
                conn.commit()
                print(f"Initialized {len(initial_classes)} classes in database")
            else:
                print("Classes already initialized in database")
                
        except Exception as e:
            print(f"Error initializing model classes: {e}")
            conn.rollback()
        finally:
            conn.close()

def verify_database():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Check model_classes table
            cursor.execute('SELECT COUNT(*) FROM model_classes')
            class_count = cursor.fetchone()[0]
            print(f"\nFound {class_count} classes in model_classes table")
            
            if class_count > 0:
                cursor.execute('SELECT class_name FROM model_classes')
                sample_classes = cursor.fetchall()
                print("Sample classes:", [c[0] for c in sample_classes])
            
            # Check model_versions table
            cursor.execute('SELECT * FROM model_versions WHERE is_active = 1')
            active_model = cursor.fetchone()
            if active_model:
                print(f"\nActive model found:")
                print(f"Path: {active_model[1]}")
                print(f"Version: {active_model[2]}")
                print(f"Classes: {active_model[4]}")
            else:
                print("\nNo active model found in database")
            
        except Exception as e:
            print(f"Verification error: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    import os
    init_database()
    init_model_classes() 
    init_first_model()
    verify_database()

