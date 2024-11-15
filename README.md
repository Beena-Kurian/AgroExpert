# AgroExpert
AgroExpert is a project designed to help farmers identify plant diseases through leaf images and receive expert guidance on agricultural concerns.

# STEPS TO FOLLOW:
# Download the dataset for training
1. Dataset
To train the model, download the dataset from Kaggle:
Dataset Link: [Plant Village Dataset on Kaggle](https://www.kaggle.com/datasets/mohitsingh1804/plantvillage/data)
This dataset includes: 
* 54,305 images of diseased and healthy plant leaves across 14 crop species.
* Coverage of 17 basic diseases, including bacterial, viral, and mold-based diseases.


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
    
     `pip install tensorflow`

2. NumPy:
   - Required for numerical operations, especially with TensorFlow and Keras models.
   - **Installation**:

     `pip install numpy`


3. Matplotlib and Pillow (PIL):
   - `matplotlib`: For plotting and visualizing data.
   - `Pillow (PIL)`: For image processing.
   - Installation:
    
     `pip install matplotlib pillow`

   
### Project Structure
- config.py: Contains configurations for database paths, model paths, and other constants.
- main.py: The primary file for managing Farmer and Expert access and functionality. Handles role-based menus and user authentication.
- admin_functions.py: Manages administrative tasks, such as: User management, Model activation and training, Viewing system statistics.
- auth.py:Handles user authentication, login, and registration with hashed passwords.
- db.py: Sets up database connections and includes functions for initializing models and user data.

### AgroExpert System Setup
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


