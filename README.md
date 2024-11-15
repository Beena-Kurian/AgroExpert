# AgroExpert
This is a project for helping farmers to know plant diseases from leaf images and for agricultural expert guidance. 

# STEPS TO FOLLOW:
# Download the dataset for training
Link - https://www.kaggle.com/datasets/mohitsingh1804/plantvillage/data
About this directory
Plant Village dataset is a public dataset of 54,305 images of diseased and healthy plant leaves collected under controlled conditions ( PlantVillage Dataset). The images cover 14 species of crops, including: apple, blueberry, cherry, grape, orange, peach, pepper, potato, raspberry, soy, squash, strawberry and tomato. It contains images of 17 basic diseases, 4 bacterial diseases, 2 diseases caused by mold (oomycete), 2 viral diseases and 1 disease caused by a mite. 12 crop species also have healthy leaf images that are not visibly affected by disease


## Requirements
This project requires the following libraries:

### Standard Libraries
- **sqlite3**: For database management to store user and model data.
- **hashlib**: For hashing passwords securely.
- **getpass**: To hide password input.
- **os**: For file and path management.
- **datetime**: To work with date and time functionalities.


### External Libraries
1. **TensorFlow and Keras**:
   - Used to manage machine learning models.
   - **Installation**:
    
     pip install tensorflow

2. **NumPy**:
   - Required for numerical operations, especially with TensorFlow and Keras models.
   - **Installation**:

     pip install numpy


3. **Matplotlib and Pillow (PIL)**:
   - `matplotlib`: For plotting and visualizing data.
   - `Pillow (PIL)`: For image processing.
   - **Installation**:
    
     pip install matplotlib pillow

   
# Project Structure
## config.py: Contains configuration settings and global constants for the project, such as database paths, model paths, and any API keys if required. This file centralizes configuration for easy modification.

## main.py: The main application file that contains logic for different user roles:
Farmer and Expert User Access: Provides specific functionalities for users in the "farmer" or "expert" roles, such as accessing model predictions and viewing consultation records.
Handles user authentication by interacting with auth.py.

## admin_functions.py: Contains functions specific to the admin role, such as:
Managing users (adding, viewing, updating, and deleting users).
Activating and managing machine learning models.
Viewing system statistics.

## auth.py: Handles user authentication, including:
Login functionality with hashed passwords.
Role-based access control (Farmer, and Expert).

## db.py: Provides database connection functions. Includes:
create_connection: A function to establish connections to the SQLite database.


# AgroExpert System Setup
The AgroExpert system includes an initialization process to set up required database structures and model information. The setup process is handled by initialize_system().

System Initialization
The initialization process ensures that all necessary data structures, classes, and model versions are set up for the system to run smoothly.

## Configuration File: config.py
The config.py file should contain configurations and paths required for the system. Ensure the following details are in place:

Database Path: Location for storing and accessing the SQLite database.
Model Paths: Path to store model files and access initial model versions.
This file centralizes project configurations, making it easier to manage paths and other constants.