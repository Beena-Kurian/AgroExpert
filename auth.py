# auth.py
import sqlite3
import hashlib
from db import create_connection
from getpass import getpass

class Auth:
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    def collect_expert_details(self):
        expert_details = {}
        
        # Scopes of Practice
        print("\n=== Scope of Practice ===")
        scopes = [
            "Agri-Business",
            "Communications",
            "Economics",
            "Finance & Services",
            "Agri-Food & Nutrition",
            "Agricultural Engineering",
            "Agricultural Environment & Ecology",
            "Animal Sciences",
            "Plant Sciences",
            "Soil Sciences"
        ]
        print("\nAvailable scopes:")
        for i, scope in enumerate(scopes, 1):
            print(f"{i}. {scope}")
        scope_choice = input("\nSelect your primary scope (enter number): ")
        expert_details['scope'] = scopes[int(scope_choice)-1]

        # Specialization
        print("\n=== Specialization ===")
        specializations = [
            "Feed nutrition",
            "Veterinary technician",
            "Biosecurity",
            "Entomology/Pest Management",
            "Genetics",
            "Fertility recommendations",
            "Retailer",
            "Soil/land classification",
            "Contaminated sites",
            "GIS",
            "Regulation",
            "Quality assurance",
            "On-farm processing",
            "Food science",
            "Research",
            "Education",
            "Legal",
            "Financial",
            "Succession",
            "Mediation",
            "Appraisals",
            "Marketing",
            "Communications",
            "Rural Planning",
            "Impact Assessments",
            "Policy",
            "Project management",
            "Other"
        ]
        print("\nAvailable specializations:")
        for i, spec in enumerate(specializations, 1):
            print(f"{i}. {spec}")
        spec_choice = input("\nSelect your specialization (enter number): ")
        expert_details['specialization'] = specializations[int(spec_choice)-1]

        # Commodity
        print("\n=== Commodity ===")
        commodities = [
            "Grains & oilseeds",
            "Fruit",
            "Vegetable",
            "Flowers",
            "Specialty crops",
            "Forage & pasture",
            "Horses",
            "Cattle",
            "Pork",
            "Sheep / Goats",
            "Poultry",
            "Beekeeping",
            "Aquaculture",
            "Other"
        ]
        print("\nAvailable commodities:")
        for i, comm in enumerate(commodities, 1):
            print(f"{i}. {comm}")
        comm_choice = input("\nSelect your primary commodity (enter number): ")
        expert_details['commodity'] = commodities[int(comm_choice)-1]

        # Region
        print("\n=== Region ===")
        regions = [
            "North",
            "East",
            "Central",
            "Niagara",
            "Mid-west",
            "South-west"
        ]
        print("\nAvailable regions:")
        for i, region in enumerate(regions, 1):
            print(f"{i}. {region}")
        region_choice = input("\nSelect your region (enter number): ")
        expert_details['region'] = regions[int(region_choice)-1]

        # City/Town
        expert_details['city'] = input("\nEnter your City/Town: ")

        return expert_details


    def register_user(self, username, password, role, email, phone):
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                hashed_password = self.hash_password(password)
                initial_status = 'pending' if role == 'expert' else 'active'
                
                # For experts, collect verification details
                expert_details = None
                if role == 'expert':
                    print("\nPlease provide your professional details for verification:")
                    expert_details = self.collect_expert_details()
                
                # First, insert the user
                cursor.execute('''
                    INSERT INTO users (username, password, role, email, phone, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, hashed_password, role, email, phone, initial_status))
                
                user_id = cursor.lastrowid
                
                # Initialize rewards for new user
                cursor.execute('INSERT INTO rewards (user_id) VALUES (?)', (user_id,))
                
                # Then, if it's an expert, insert their details
                if role == 'expert' and expert_details:
                    cursor.execute('''
                        INSERT INTO expert_details 
                        (user_id, scope, specialization, commodity, region, city)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        user_id,
                        expert_details['scope'],
                        expert_details['specialization'],
                        expert_details['commodity'],
                        expert_details['region'],
                        expert_details['city']
                    ))
                
                conn.commit()
                if role == 'expert':
                    print("\nRegistration successful! Your application will be reviewed by an admin.")
                    print("You will be notified once your account is approved.")
                else:
                    print("\nRegistration successful!")
                return True
                
            except sqlite3.IntegrityError:
                print("Username or email already exists!")
                return False
            except Exception as e:
                print(f"Error during registration: {e}")
                return False
            finally:
                conn.close()
        return False

    def login(self, username, password):
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                hashed_password = self.hash_password(password)
                
                cursor.execute('''
                    SELECT id, role, status FROM users 
                    WHERE username = ? AND password = ?
                ''', (username, hashed_password))
                
                user = cursor.fetchone()
                if user:
                    if user[2] == 'active':
                        return {'id': user[0], 'role': user[1]}
                    elif user[2] == 'pending':
                        print("\nYour expert account is still pending approval.")
                        print("Please wait for admin verification. Try again later.")
                        return None
                    else:
                        print("Sorry, your registration was not approved.\n")
                        print("You are not a member of Ontario Institute of Agrologists: https://oia.on.ca/search/custom.asp?id=5552")
                        print("Please contact admin.")
                        return None
                else:
                    print("Invalid username or password")
                    return None
            finally:
                conn.close()
        return None
    
    def display_registration_menu(self):
        print("\n=== User Registration ===")
        username = input("Enter username: ")
        password = getpass("Enter password: ")  # Password will be hidden
        role = input("Enter role (farmer/expert): ").lower()
        email = input("Enter email: ")
        phone = input("Enter phone number: ")
        
        if role not in ['farmer', 'expert']:
            print("Invalid role! Please choose 'farmer' or 'expert'")
            return False
            
        return self.register_user(username, password, role, email, phone)

    def display_login_menu(self):
        print("\n=== Login ===")
        username = input("Enter username: ")
        password = getpass("Enter password: ")  # Password will be hidden
        return self.login(username, password)