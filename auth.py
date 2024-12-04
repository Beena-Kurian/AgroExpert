# auth.py
import sqlite3
import hashlib
from db import create_connection
from getpass import getpass
import re

class Auth:
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    def collect_expert_details(self):
        expert_details = {}

        # Scopes of Practice with validation
        print("\n=== Scope of Practice ===")
        scopes = [
            "Agri-Business", "Communications", "Economics", "Finance & Services", 
            "Agri-Food & Nutrition", "Agricultural Engineering", "Agricultural Environment & Ecology", 
            "Animal Sciences", "Plant Sciences", "Soil Sciences"
        ]
        print("\nAvailable scopes:")
        for i, scope in enumerate(scopes, 1):
            print(f"{i}. {scope}")

        while True:
            try:
                scope_choice = int(input("\nSelect your primary scope (enter number): "))
                if 1 <= scope_choice <= len(scopes):
                    expert_details['scope'] = scopes[scope_choice - 1]
                    break
                else:
                    print(f"Please select a number between 1 and {len(scopes)}.")
            except ValueError:
                print("Invalid input! Please enter a number.")

        # Specialization with validation
        print("\n=== Specialization ===")
        specializations = [
            "Feed nutrition", "Veterinary technician", "Biosecurity", "Entomology/Pest Management", 
            "Genetics", "Fertility recommendations", "Retailer", "Soil/land classification", 
            "Contaminated sites", "GIS", "Regulation", "Quality assurance", "On-farm processing", 
            "Food science", "Research", "Education", "Legal", "Financial", "Succession", "Mediation", 
            "Appraisals", "Marketing", "Communications", "Rural Planning", "Impact Assessments", 
            "Policy", "Project management", "Other"
        ]
        print("\nAvailable specializations:")
        for i, spec in enumerate(specializations, 1):
            print(f"{i}. {spec}")

        while True:
            try:
                spec_choice = int(input("\nSelect your specialization (enter number): "))
                if 1 <= spec_choice <= len(specializations):
                    expert_details['specialization'] = specializations[spec_choice - 1]
                    break
                else:
                    print(f"Please select a number between 1 and {len(specializations)}.")
            except ValueError:
                print("Invalid input! Please enter a number.")

        # Commodity with validation
        print("\n=== Commodity ===")
        commodities = [
            "Grains & oilseeds", "Fruit", "Vegetable", "Flowers", "Specialty crops", 
            "Forage & pasture", "Horses", "Cattle", "Pork", "Sheep / Goats", 
            "Poultry", "Beekeeping", "Aquaculture", "Other"
        ]
        print("\nAvailable commodities:")
        for i, comm in enumerate(commodities, 1):
            print(f"{i}. {comm}")

        while True:
            try:
                comm_choice = int(input("\nSelect your primary commodity (enter number): "))
                if 1 <= comm_choice <= len(commodities):
                    expert_details['commodity'] = commodities[comm_choice - 1]
                    break
                else:
                    print(f"Please select a number between 1 and {len(commodities)}.")
            except ValueError:
                print("Invalid input! Please enter a number.")

        # Region with validation
        print("\n=== Region ===")
        regions = [
            "North", "East", "Central", "Niagara", "Mid-west", "South-west"
        ]
        print("\nAvailable regions:")
        for i, region in enumerate(regions, 1):
            print(f"{i}. {region}")

        while True:
            try:
                region_choice = int(input("\nSelect your region (enter number): "))
                if 1 <= region_choice <= len(regions):
                    expert_details['region'] = regions[region_choice - 1]
                    break
                else:
                    print(f"Please select a number between 1 and {len(regions)}.")
            except ValueError:
                print("Invalid input! Please enter a number.")

        # City/Town with validation (ensure it's not empty)
        while True:
            city = input("\nEnter your City/Town: ").strip()
            if city:
                expert_details['city'] = city
                break
            else:
                print("City/Town cannot be empty! Please enter a valid city or town.")

        return expert_details

    
    def check_existing_user(self, field, value):
        """
        Check if a user with the given field (username or email) exists in the database.
        """
        conn = create_connection()  # Create a database connection
        if conn is not None:
            try:
                cursor = conn.cursor()
                query = f"SELECT COUNT(*) FROM users WHERE {field} = ?"
                cursor.execute(query, (value,))
                result = cursor.fetchone()
                return result[0] > 0
            except sqlite3.Error as e:
                print(f"Database error: {e}")
                return False
            finally:
                conn.close()  # Ensure the connection is closed after use
        else:
            print("Failed to establish a database connection.")
            return False


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
    
    def validate_password(self,password):
        """
        Validate a password against defined criteria.
        """
        # Check for minimum length
        if len(password) < 7:
            print("Password must be at least 7 characters long.")
            return False
        # Add other validation checks as needed (uppercase, lowercase, etc.)
        return True
    
    def display_registration_menu(self):
        print("\n=== User Registration ===")
        
        # Check if username exists and validate length
        while True:
            username = input("Enter username: ").strip()  # .strip() to remove any leading/trailing spaces

            # Check if username length is at least 7 characters
            if len(username) < 7:
                print("Username must be at least 7 characters long.")
            
            # Check if the username already exists
            elif self.check_existing_user(field='username', value=username):
                print("Username already exists! Please choose a different username.")
            
            else:
                break  # Exit the loop if both conditions are satisfied

        
            # Validate password
        while True:
            password = getpass("Enter password: ")
            if self.validate_password(password):
                break
            print("Please try again.")

        print("Password accepted!")
        
        # Validate role using numeric selection
        role = None
        while True:
            print("Select role:")
            print("1. Farmer")
            print("2. Expert")
            role_choice = input("Enter your choice (1 or 2): ")
            if role_choice == '1':
                role = 'farmer'
                break
            elif role_choice == '2':
                role = 'expert'
                break
            else:
                print("Invalid choice! Please select 1 for Farmer or 2 for Expert.")

        # Check if email exists
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        while True:
            email = input("Enter email: ")
            if not re.match(email_pattern, email):
                print("Invalid email! Please enter a valid email address. Try again.")
            elif self.check_existing_user(field='email', value=email):
                print("Email already exists! Please use a different email.")
            else:
                break

        # Validate phone number
        phone_pattern = r'^\d{10}$'  # Assuming a 10-digit phone number format
        while True:
            phone = input("Enter phone number: ")
            if not re.match(phone_pattern, phone):
                print("Invalid phone number! Please enter a 10-digit number. Try again.")
            elif self.check_existing_user(field='phone', value=phone):
                print("Phone already exists! Please use a different phone number.")
            else:
                break


        # Register user if all validations pass
        return self.register_user(username, password, role, email, phone)

    def display_login_menu(self):
        print("\n=== Login ===")
        username = input("Enter username: ")
        password = getpass("Enter password: ")  # Password will be hidden
        return self.login(username, password)