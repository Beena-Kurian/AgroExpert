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
1. TensorFlow and Keras:
   - Used to manage machine learning models.
   - Installation:
    
     pip install tensorflow

2. NumPy:
   - Required for numerical operations, especially with TensorFlow and Keras models.
   - **Installation**:

     pip install numpy


3. Matplotlib and Pillow (PIL):
   - `matplotlib`: For plotting and visualizing data.
   - `Pillow (PIL)`: For image processing.
   - Installation:
    
     pip install matplotlib pillow

   
## Project Structure
### config.py: Contains configuration settings and global constants for the project, such as database paths, model paths, and any API keys if required. This file centralizes configuration for easy modification.

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

## AgroExpert System Setup
The AgroExpert system includes an initialization process to set up required database structures and model information. The setup process is handled by initialize_system().

Prerequite: clone the repository using the following command.
git clone https://github.com/Beena-Kurian/AgroExpert.git

### Step 1: Run `config.py` for initialisation
Navigate to the AgroExpert Folder, then run
`python config.py`
The config.py file will initialise DB, model classes,model version, and it will verify the database by importing functions from db.py
from db import init_database, init_model_classes, init_first_model, verify_database

### Step 2: Run `main.py` for Expert and Farmer
`python main.py`
This includes farmer and expert registration and Logins.
1. Login
2. Register
3. Exit
Once the user login as Farmer/Expert, the dashbboard for them can be accessed to do the intended operations.
Once farmer is registered, he can login to do different functionalities.

Farmer can perform operations like:
1. Upload Image for Disease Identification
2. Request Expert Consultation
3. View My Consultations
4. View Sample Requests
5. View My Rewards
6. View News
7. Logout
Once Expert is registered, he needs to wait until he got verified by admin. Once the admin Accepted his registration, he can login.

Expert can perform operations like(once he got approved by admin): 
1. View Pending Consultations
      1. Provide diagnosis and treatment
      2. Request more images (Unknown Disease)
3. View My Rewards
4. View News
5. Logout
   
### Step 3: Run `admin_functions.py`
`python admin_functions.py`
Admin dashboard can be viewed by running the above code. 

Admin can perform operations like: 
1. User Management
      1. View All Users
      2. Approve/Reject Expert Registrations
      3. Back to Admin Menu
3. Manage News
      1. Add News
      2. View All News
      3. Delete News
      4. Back
5. View System Statistics
6. Model Management
      1. Train New Model
           1. Train with existing classes
           2. Train with existing classes + new disease classes
      3. View Model Versions
      4. View Current Classes
      5. Activate Model
      6. Back
7. Logout


