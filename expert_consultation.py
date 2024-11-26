from db import create_connection
from datetime import datetime
from PIL import Image
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from rewards import RewardSystem, ExpertRewards, FarmerRewards
from disease_identification import *

class ExpertConsultation:
    def __init__(self, disease_identifier, expert_rewards):
        """
        Initializes the ExpertConsultation class.

        Args:
            disease_identifier (DiseaseIdentification): Instance of the DiseaseIdentification class.
            reward_system (ExpertRewards): Instance of the ExpertRewards class for handling rewards.
        """
        self.disease_identifier = disease_identifier
        self.expert_rewards = expert_rewards

    def notify_farmer_replies(self, farmer_id):
        conn = create_connection()  # Assuming you have a create_connection function
        if conn:
            try:
                cursor = conn.cursor()

                # Get the last login time for the farmer
                cursor.execute('''
                    SELECT last_login 
                    FROM users 
                    WHERE id = ?
                ''', (farmer_id,))
                last_login = cursor.fetchone()

                if last_login:
                    last_login_time = last_login[0]

                    # Fetch count of replies after the last login timestamp
                    cursor.execute('''
                        SELECT COUNT(*) 
                        FROM consultation_responses cr
                        INNER JOIN consultations c
                        ON cr.consultation_id = c.id
                        WHERE c.farmer_id = ? 
                        AND cr.created_at > ?
                    ''', (farmer_id, last_login_time))

                    reply_count = cursor.fetchone()[0]

                    if reply_count > 0:
                        print(f"You have received {reply_count} new reply/replies since your last login.")
                    else:
                        print("No new replies since your last login.")
                else:
                    print("Unable to fetch last login time for the farmer.")
            except Exception as e:
                print(f"Error fetching notifications: {e}")
            finally:
                conn.close()

    def notify_expert_new_messages(self, expert_id):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Fetch new messages for the expert
                cursor.execute('''
                    SELECT COUNT(*) 
                    FROM consultations 
                    WHERE status = 'pending'
                ''')
                count = cursor.fetchone()[0]
                # Debug: check the count value
                # print(f"Fetched count: {count}")
                if count > 0:
                    print(f"\nYou have {count} new consultation message(s) from farmers.")
                else:
                    print("\nNo new messages from farmers.")
            finally:
                conn.close()


    def create_new_consultation(self, farmer_id):
        print("\n=== Create New Consultation ===")
        
        def get_valid_date_input(prompt):
            while True:
                date_str = input(prompt).strip()
                try:
                    # Parse the date string
                    valid_date = datetime.strptime(date_str, "%Y-%m-%d")
                    return date_str
                except ValueError:
                    print("Invalid date format. Please enter a valid date in YYYY-MM-DD format.")
        # Validation for non-empty and alphabetic fields
        def get_valid_input(prompt, field_name):
            while True:
                value = input(prompt).strip()
                if not value:
                    print(f"{field_name} cannot be empty!")
                elif not value.isalpha():
                    print(f"{field_name} must contain only letters!")
                else:
                    return value

        # Get inputs with validation
        plant_name = get_valid_input("Enter plant name: ", "Plant name")
        symptoms = get_valid_input("Enter observed symptoms: ", "Symptoms")
        region = get_valid_input("Enter your region: ", "Region")

        # Date validation
        date_noticed = get_valid_date_input("Enter date when symptoms were first noticed (YYYY-MM-DD): ")

        # Allow treatments to be empty, no validation needed here
        treatments = input("Enter any treatments already attempted (if any): ").strip()

        # Path validation (basic check for non-empty value)
        image_path = input("Enter path to plant image (or press Enter to skip): ").strip('"').strip("'")

        # Generate description
        description = f"{plant_name} - {symptoms} (Region: {region})"
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO consultations 
                    (farmer_id, image_path, plant_name, symptoms, region, date_noticed, treatments, status, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)
                ''', (farmer_id, image_path if image_path else None, plant_name, symptoms, region, date_noticed, treatments, 'pending',description))
                conn.commit()
                print("\nConsultation request created successfully!")

                # Add points for consultation request
                self.add_consultation_points(farmer_id)

            except Exception as e:
                print(f"Error creating consultation: {e}")
            finally:
                conn.close()


    def get_non_empty_and_alpha_input(self, prompt, error_message):
        """Ensure input is not empty and contains only alphabetic characters."""
        value = input(prompt).strip()
        while not value or not value.isalpha():
            print(error_message)
            value = input(prompt).strip()
        return value

    def get_valid_date_input(self, prompt):
        """Ensure valid date format YYYY-MM-DD."""
        while True:
            date_input = input(prompt).strip()
            if not date_input:
                print("Date cannot be empty!")
                continue
            try:
                # Validate if the input is a correct date
                datetime.strptime(date_input, '%Y-%m-%d')
                return date_input
            except ValueError:
                print("Invalid date format. Please enter a valid date in YYYY-MM-DD format.")

    # Points for farmer for putting consultation request
    def add_consultation_points(self, farmer_id):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Add 10 points for consultation request(for farmer)
                cursor.execute('''
                    UPDATE rewards 
                    SET points = points + 10 
                    WHERE user_id = ?
                ''', (farmer_id,))
                
                # Log the transaction
                cursor.execute('''
                    INSERT INTO reward_transactions 
                    (user_id, action, points, description)
                    VALUES (?, ?, ?, ?)
                ''', (farmer_id, 'consultation_request', 10, 'Points for creating consultation request'))
                
                conn.commit()
            except Exception as e:
                print(f"Error adding reward points: {e}")
            finally:
                conn.close()

    # view for farmer
    def view_farmer_consultations(self, farmer_id):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, description, status, created_at 
                    FROM consultations 
                    WHERE farmer_id = ?
                    ORDER BY created_at DESC
                ''', (farmer_id,))
                consultations = cursor.fetchall()
                
                if not consultations:
                    print("\nNo consultations found.")
                    return
                
                print("\n=== Your Consultations ===")
                for cons in consultations:
                    print(f"\nConsultation ID: {cons[0]}")
                    print(f"Details:\n{cons[1]}")
                    print(f"Status: {cons[2]}")
                    print(f"Created: {cons[3]}")
                    
                    # If consultation is completed, show expert response
                    if cons[2].lower() == 'completed':
                        cursor.execute('''
                            SELECT expert_response 
                            FROM consultation_responses 
                            WHERE consultation_id = ?
                        ''', (cons[0],))
                        response = cursor.fetchone()
                        if response:
                            print(f"Expert Response: {response[0]}")
                    print("-" * 50)
            finally:
                conn.close()

    # view for expert for pending consultations 
    def view_pending_consultations(self, expert_id):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT c.id, u.username, c.description, c.image_path, c.created_at,
                        c.plant_name, c.symptoms, c.region, c.date_noticed, c.treatments 
                    FROM consultations c
                    JOIN users u ON c.farmer_id = u.id
                    WHERE c.status = 'pending'
                    ORDER BY c.created_at
                ''')
                consultations = cursor.fetchall()
                
                if not consultations:
                    print("\nNo pending consultations.")
                    return

                print("\n=== Pending Consultations ===")
                for cons in consultations:
                    print(f"\nConsultation ID: {cons[0]}")
                    print(f"Farmer: {cons[1]}")
                    print(f"Plant: {cons[5]}")
                    print(f"Symptoms: {cons[6]}")
                    print(f"Region: {cons[7]}")
                    print(f"Date Noticed: {cons[8]}")
                    print(f"Treatments Attempted: {cons[9] if cons[9] else 'None'}")
                    print(f"Created: {cons[4]}")
                    
                    if cons[3]:  # if image path exists
                        print("\nWould you like to view the image? (y/n)")
                        if input().lower() == 'y':
                            self.disease_identifier.display_image(cons[3])
                    print("-" * 50)
                
                # Option to respond to a consultation
                while True:
                    cons_id = input("\nEnter consultation ID to respond (or press Enter to skip): ")
                    if not cons_id:
                        break
                    try:
                        cons_id = int(cons_id)
                        # Check if this ID was in the list of pending consultations
                        if cons_id in [c[0] for c in consultations]:
                            self.respond_to_consultation(expert_id, cons_id)
                            break
                        else:
                            print("Error: Please enter a valid consultation ID from the list above.")
                    except ValueError:
                        print("Error: Please enter a valid number.")
            finally:
                conn.close()

    # for expert to respond to consultation requests
    def respond_to_consultation(self, expert_id, consultation_id):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, status, farmer_id 
                    FROM consultations 
                    WHERE id = ?
                ''', (consultation_id,))
                consultation = cursor.fetchone()
                
                if not consultation:
                    print("\nError: Consultation ID does not exist!")
                    return
                
                if consultation[1] != 'pending':
                    print("\nError: This consultation has already been responded to!")
                    return

                print("\n=== Respond to Consultation ===")
                print("1. Provide diagnosis and treatment")
                print("2. Request more images (Unknown Disease)")
                choice = input("Enter your choice (1-2): ")

                if choice == "1":
                    # Normal consultation response
                    diagnosis = input("Enter your diagnosis: ")
                    treatment = input("Enter recommended treatment: ")
                    additional_notes = input("Enter any additional notes: ")
                    
                    response = f"Diagnosis: {diagnosis}\nRecommended Treatment: {treatment}\n"
                    if additional_notes:
                        response += f"Additional Notes: {additional_notes}"
                    
                    # Update consultation status
                    cursor.execute('''
                        UPDATE consultations 
                        SET status = 'completed', expert_id = ? 
                        WHERE id = ?
                    ''', (expert_id, consultation_id))
                    
                    # Store expert response
                    cursor.execute('''
                        INSERT INTO consultation_responses 
                        (consultation_id, expert_id, expert_response) 
                        VALUES (?, ?, ?)
                    ''', (consultation_id, expert_id, response))
                    
                elif choice == "2":
                    # Request for more images - Unknown Disease
                    description = input("Enter description of what you observe: ")
                    symptoms = input("Enter specific symptoms to look for: ")
                    
                    # Create unknown disease record
                    cursor.execute('''
                        INSERT INTO unknown_diseases 
                        (reported_by_farmer_id, verified_by_expert_id, description, 
                        symptoms, status)
                        VALUES (?, ?, ?, ?, 'samples_requested')
                    ''', (consultation[2], expert_id, description, symptoms))
                    
                    unknown_disease_id = cursor.lastrowid
                    
                    # Update consultation status
                    cursor.execute('''
                        UPDATE consultations 
                        SET status = 'awaiting_samples', expert_id = ? 
                        WHERE id = ?
                    ''', (expert_id, consultation_id))
                    
                    # Store expert request
                    response = f"UNKNOWN DISEASE DETECTED\nDescription: {description}\n" \
                            f"Observed Symptoms: {symptoms}\n" \
                            f"Action Required: Please provide more image samples " \
                            f"(minimum 50 images) as a zip file."
                    
                    cursor.execute('''
                        INSERT INTO consultation_responses 
                        (consultation_id, expert_id, expert_response) 
                        VALUES (?, ?, ?)
                    ''', (consultation_id, expert_id, response))
                    
                    print("\nRequest for more samples submitted successfully!")
                    print("Farmer will be notified to provide more images.")
                
                # Calculate response time if needed
                cursor.execute('''
                    SELECT created_at FROM consultations WHERE id = ?
                ''', (consultation_id,))
                created_at = cursor.fetchone()[0]
                response_time = self.calculate_response_time(created_at)

                conn.commit()
                print("Response saved successfully.")
                # Award points for the completed consultation
                if self.expert_rewards.award_consultation_completion(expert_id, response_time):
                    print("Reward points successfully awarded to the expert.")
                
            except Exception as e:
                print(f"Error submitting response: {e}")
                conn.rollback()
            finally:
                conn.close()

    @staticmethod
    def calculate_response_time(created_at):
        """
        Calculate the response time in hours.

        Args:
            created_at (str): The timestamp when the consultation was created.

        Returns:
            int: Response time in hours.
        """
        from datetime import datetime
        created_time = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()
        response_time = (current_time - created_time).total_seconds() / 3600
        return int(response_time)
    
    # for famer to submit
    def submit_disease_samples(self, farmer_id, unknown_disease_id, samples_path):
        """
        Submit samples for an unknown disease
        """
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Store samples information
                cursor.execute('''
                    INSERT INTO disease_samples 
                    (unknown_disease_id, farmer_id, samples_zip_path) 
                    VALUES (?, ?, ?)
                ''', (unknown_disease_id, farmer_id, samples_path))
                
                # Update unknown disease status
                cursor.execute('''
                    UPDATE unknown_diseases 
                    SET status = 'samples_received' 
                    WHERE id = ?
                ''', (unknown_disease_id,))
                
                conn.commit()
                print("\nSamples submitted successfully!")
                
                # Add reward points for submitting samples
                self.add_sample_submission_points(farmer_id)
                
            except Exception as e:
                print(f"Error submitting samples: {e}")
                conn.rollback()
            finally:
                conn.close()

    # for farmer reward
    def add_sample_submission_points(self, farmer_id):
        """
        Add points for submitting disease samples
        """
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Add 500 points for submitting samples (50 images)
                cursor.execute('''
                    UPDATE rewards 
                    SET points = points + 500 
                    WHERE user_id = ?
                ''', (farmer_id,))
                
                # Log the transaction
                cursor.execute('''
                    INSERT INTO reward_transactions 
                    (user_id, action, points, description)
                    VALUES (?, ?, ?, ?)
                ''', (farmer_id, 'sample_submission', 500, 
                    'Points for submitting unknown disease samples'))
                
                conn.commit()
            except Exception as e:
                print(f"Error adding reward points: {e}")
                conn.rollback()
            finally:
                conn.close()

    # bug fixing needed - view farmer
    def view_unknown_disease_requests(self, farmer_id):
        """
        View requests for additional samples for unknown diseases
        """
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT ud.id, ud.description, ud.symptoms, 
                        c.id as consultation_id
                    FROM unknown_diseases ud
                    JOIN consultations c ON ud.reported_by_farmer_id = c.farmer_id
                    WHERE ud.reported_by_farmer_id = ? 
                    AND ud.status = 'samples_requested'
                ''', (farmer_id,))
                requests = cursor.fetchall()
                
                if not requests:
                    print("\nNo pending requests for disease samples.")
                    return
                
                print("\n=== Pending Sample Requests ===")
                for req in requests:
                    print(f"\nRequest ID: {req[0]}")
                    print(f"Description: {req[1]}")
                    print(f"Symptoms to Document: {req[2]}")
                    print(f"Related Consultation: {req[3]}")
                    print("-" * 50)
                    
                # Option to submit samples
                req_id = input("\nEnter request ID to submit samples (or press Enter to skip): ")
                if req_id:
                    samples_path = input("Enter path to samples zip file: ").strip('"').strip("'")
                    if os.path.exists(samples_path):
                        self.submit_disease_samples(farmer_id, int(req_id), samples_path)
                    else:
                        print("Error: File not found!")
                        
            finally:
                conn.close()

