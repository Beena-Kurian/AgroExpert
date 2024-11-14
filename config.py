from auth import Auth
from db import init_database, init_model_classes, init_first_model, verify_database
import os

class AgroExpertInitialiser:
    def __init__(self):
        self.auth = Auth()

def initialize_system():
    try:
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)

        print("\nInitializing database...")
        init_database()
        
        print("\nInitializing model classes...")
        init_model_classes()
        
        print("\nInitializing model version...")
        init_first_model()
        
        print("\nVerifying database setup...")
        verify_database()
        
        return True
    except Exception as e:
        print(f"Error during system initialization: {e}")
        return False
    
if __name__ == "__main__":
    app = AgroExpertInitialiser()
    # Initialize system first
    if initialize_system():
        print("\nConfigured the AgroExpert system...")
    else:
        print("Failed to initialize system. Please check the errors above.")