from db import create_connection
from datetime import datetime
from PIL import Image
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from rewards import RewardSystem, ExpertRewards, FarmerRewards
from disease_identification import *
import zipfile
import shutil
import os
from PIL import Image
import glob
import random


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
        conn = create_connection()  
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
    def notify_expert_new_sample_submissions(self, expert_id):
        """
        Notify expert about new sample submissions by farmers with status 'pending'.
        """
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT ds.id
                    FROM disease_samples ds
                    JOIN unknown_diseases ud ON ds.unknown_disease_id = ud.id
                    WHERE ds.status = 'pending'  -- Only show pending submissions
                    AND ud.verified_by_expert_id = ?
                ''', (expert_id,))
                submissions = cursor.fetchall()

                if submissions:
                    print(f"\nYou have {len(submissions)} new sample submission(s) from farmers.")
                else:
                    print("\nYou have no new sample submissions.")
            finally:
                conn.close()

    def extract_zip(self, zip_path, extract_folder):
        """ Extract files from a zip file, handling nested folders. """
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)       
        print(f"Extracted files to {extract_folder}")


    def review_sample_submissions(self, expert_id):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''SELECT ds.id, ud.description, ds.samples_zip_path 
                                FROM disease_samples ds
                                JOIN unknown_diseases ud ON ds.unknown_disease_id = ud.id
                                WHERE ds.status = 'pending' AND ud.verified_by_expert_id = ?''', (expert_id,))
                submissions = cursor.fetchall()

                if submissions:
                    print("Pending Sample Submissions:")

                    # Clean up the 'temp' folder before processing new submissions
                    self.clean_temp_folder()

                    for submission in submissions:
                        print(f"- Sample ID: {submission[0]}, Disease: {submission[1]}, Samples Path: {submission[2]}")
                        # Extract the zip file
                        zip_path = submission[2]
                        extract_folder = os.path.join("Farmer_uploads", "temp", f"sample_{submission[0]}")
                        os.makedirs(extract_folder, exist_ok=True)
                        self.extract_zip(zip_path, extract_folder)

                        # Check if any images exist after extraction
                        image_files = [f for f in os.listdir(extract_folder) if f.endswith(('.jpg', '.jpeg', '.png', '.JPG'))]
                        total_images = len(image_files)

                        # Ensure there are images to review
                        if total_images == 0:
                            print(f"No images found in the extracted folder for Sample ID {submission[0]}.")
                            continue

                        # Ask expert how many images to review
                        num_images = int(input(f"How many images do you want to review (1 to {total_images}): "))

                        # Ensure the requested number is within the available images
                        if num_images > total_images:
                            print(f"Error: Requested more images than available. Only {total_images} images are available.")
                            continue

                        # Display images one by one
                        self.display_samples_one_at_a_time(extract_folder, num_images)

                        # After reviewing all images, ask the expert for decision on the entire submission
                        submission_decision = input("Do you approve this entire submission? (approve/reject/pending): ").lower()

                        if submission_decision == 'approve':
                            # Get crop and disease name from expert input
                            crop_name = input("Enter the crop name: ").strip()
                            disease_name = input("Enter the disease name: ").strip()

                            # Normalize the folder name (ensure no spaces, use underscores)
                            disease_name = disease_name.replace(" ", "_")  # Replace spaces with underscores
                            approved_folder = os.path.join("Farmer_uploads", f"{crop_name}__{disease_name}")

                            # Check if the folder already exists
                            if not os.path.exists(approved_folder):
                                os.makedirs(approved_folder, exist_ok=True)
                                print(f"Created new folder for {crop_name}__{disease_name}.")
                            else:
                                print(f"Folder {approved_folder} already exists. Merging images.")

                            # Move the new images to the existing/created folder
                            for image_file in image_files:
                                shutil.move(os.path.join(extract_folder, image_file), os.path.join(approved_folder, image_file))

                            self.update_sample_status(submission[0], status='verified')
                            print(f"Sample ID {submission[0]} has been approved and images are moved to {approved_folder}.")
                            self.remove_folder(extract_folder)
                        elif submission_decision == 'reject':
                            # If rejected, remove the folder
                            self.remove_folder(extract_folder)
                            self.update_sample_status(submission[0], status='rejected')
                            print(f"Sample ID {submission[0]} has been rejected.")
                        elif submission_decision == 'pending':
                            # Mark as pending and remove the temp folder
                            self.remove_folder(extract_folder)
                            self.update_sample_status(submission[0], status='pending')
                            print(f"Sample ID {submission[0]} is marked as pending.")
                        else:
                            print("Invalid input. Please enter 'approve', 'reject', or 'pending'.")
                else:
                    print("\nNo pending sample submissions to review.")
            except Exception as e:
                print(f"Error: {e}")
            finally:
                self.clean_temp_folder()
                conn.close()

    def remove_folder(self, folder_path):
        """ Removes a folder and all its contents """
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"Temporary folder {folder_path} has been removed.")

    def clean_temp_folder(self):
        """ Cleans the temp folder """
        temp_folder_path = os.path.join("Farmer_uploads", "temp")
        if os.path.exists(temp_folder_path):
            shutil.rmtree(temp_folder_path)
            print(f"Temp folder {temp_folder_path} has been removed.")
    
    def display_samples_one_at_a_time(self, extract_folder, num_images):
        # List all files in the extracted folder
        image_files = [f for f in os.listdir(extract_folder) if f.endswith(('.jpg', '.jpeg', '.png', '.JPG'))]

        # Ensure the requested number of images doesn't exceed the total number available
        total_images = len(image_files)
        if num_images > total_images:
            print(f"Error: Requested more images than available. Only {total_images} images are uploaded.")
            num_images = total_images

        # Randomly select the images to review
        selected_images = random.sample(image_files, num_images)

        # Display the images one by one
        for img in selected_images:
            img_path = os.path.join(extract_folder, img)
            print(f"Displaying image: {img_path}")

            # Open and display the image
            with Image.open(img_path) as img_obj:
                img_obj.show()

            # Wait for the user to acknowledge before showing the next image
            input("Press Enter to view the next image...")

        print("\n")

    def update_sample_status(self, sample_id, status='verified'):
        """
        Update the status of the sample after it has been reviewed by the expert.
        
        Args:
            sample_id (int): The ID of the sample being updated.
            status (str): The new status of the sample (e.g., 'verified', 'rejected').
        """
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Update the sample status in the database
                cursor.execute('''UPDATE disease_samples SET status = ? WHERE id = ?''', (status, sample_id))
                conn.commit()
                print(f"Sample ID {sample_id} status updated to '{status}'")
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

    import os

    # Path validation with detailed checks
    def validate_image_path(self):
        while True:
            image_path = input("Enter path to plant image (or press Enter to skip): ").strip('"').strip("'")

            # Allow skipping
            if image_path == "":
                print("No image path provided. Skipping.")
                return None

            # Check if path exists
            if not os.path.exists(image_path):
                print("Error: The path does not exist. Please enter a valid path.")
                continue

            # Check if it's a file
            if not os.path.isfile(image_path):
                print("Error: The path is not a file. Please enter a valid file path.")
                continue

            # Validate file extension
            valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif")
            if not image_path.lower().endswith(valid_extensions):
                print("Error: The file is not a valid image. Supported formats are: .jpg, .jpeg, .png, .bmp, .gif")
                continue

            # If all validations pass
            print("Valid image path provided.")
            return image_path

    def create_new_consultation(self, farmer_id):
        print("\n=== Create New Consultation ===")
        
        def get_valid_date_input(prompt):
            """Ensure valid date format YYYY-MM-DD and that it's not a future date."""
            while True:
                date_input = input(prompt).strip()
                
                if not date_input:
                    print("Date cannot be empty!")
                    continue
                
                try:
                    # Validate if the input is a correct date
                    input_date = datetime.strptime(date_input, '%Y-%m-%d')
                    
                    # Ensure the date is not in the future
                    if input_date > datetime.now():
                        print("Date cannot be in the future! Please enter a valid date.")
                        continue
                    
                    return date_input
                
                except ValueError:
                    print("Invalid date format. Please enter a valid date in YYYY-MM-DD format.")
        def get_valid_input(prompt, field_name):
            while True:
                value = input(prompt).strip()
                if not value:
                    print(f"{field_name} cannot be empty!")
                elif not all(char.isalpha() or char.isspace() for char in value):
                    print(f"{field_name} must contain only letters and spaces!")
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


        # # Path validation (basic check for non-empty value)
        image_path = self.validate_image_path()
        if image_path:
            print(f"Processing image: {image_path}")
        else:
            print("No image will be processed.")

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
                self.add_consultation_request_points(farmer_id)

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
        """Ensure valid date format YYYY-MM-DD and that it's not a future date."""
        while True:
            date_input = input(prompt).strip()
            
            if not date_input:
                print("Date cannot be empty!")
                continue
            
            try:
                # Validate if the input is a correct date
                input_date = datetime.strptime(date_input, '%Y-%m-%d')
                
                # Ensure the date is not in the future
                if input_date > datetime.now():
                    print("Date cannot be in the future! Please enter a valid date.")
                    continue
                
                return date_input
            
            except ValueError:
                print("Invalid date format. Please enter a valid date in YYYY-MM-DD format.")


    # Points for farmer for putting consultation request
    def add_consultation_request_points(self, farmer_id):
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
    def add_consultation_response_points(self, expert_id, response_time):
        conn = create_connection()
        if conn:
            try:
                # conn.execute("PRAGMA busy_timeout = 5000")  # Wait up to 5 seconds for the lock
                cursor = conn.cursor()

                # Add fast response bonus if applicable
                if response_time and response_time <= 24:  # response time in hours
                    additional_points = 25
                else:
                    additional_points = 20

                # Update points for the expert
                cursor.execute('''
                    UPDATE rewards 
                    SET points = points + ?
                    WHERE user_id = ?
                ''', (additional_points, expert_id))

                # Log the transaction
                cursor.execute('''
                    INSERT INTO reward_transactions 
                    (user_id, action, points, description)
                    VALUES (?, ?, ?, ?)
                ''', (expert_id, 'consultation_completed', additional_points, 
                    'Points for completing consultation'))

                conn.commit()
            except Exception as e:
                print(f"Error adding reward points: {e}")
            finally:
                conn.close()

    # Function to allow an expert to respond to consultation requests
    def respond_to_consultation(self, expert_id, consultation_id):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Fetch consultation details
                cursor.execute('''
                    SELECT id, status, farmer_id, created_at 
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

                created_at = consultation[3]

                # # User choice
                # print("\n=== Respond to Consultation ===")
                # print("1. Provide diagnosis and treatment")
                # print("2. Request more images (Unknown Disease)")
                # choice = input("Enter your choice (1-2): ")

                # if choice == "1":
                #     # Diagnosis and treatment
                #     diagnosis = input("Enter your diagnosis: ").strip()
                #     treatment = input("Enter recommended treatment: ").strip()
                #     additional_notes = input("Enter any additional notes: ").strip()
                # User choice
                while True:
                    print("\n=== Respond to Consultation ===")
                    print("1. Provide diagnosis and treatment")
                    print("2. Request more images (Unknown Disease)")
                    choice = input("Enter your choice (1-2): ").strip()

                    if choice in ["1", "2"]:
                        break  # Valid choice, exit loop
                    else:
                        print("Invalid choice. Please enter 1 or 2.")

                if choice == "1":
                    # Diagnosis and treatment
                    while True:
                        diagnosis = input("Enter your diagnosis: ").strip()
                        if diagnosis:
                            break
                        else:
                            print("Diagnosis cannot be empty. Please provide a valid diagnosis.")

                    while True:
                        treatment = input("Enter recommended treatment: ").strip()
                        if treatment:
                            break
                        else:
                            print("Treatment cannot be empty. Please provide a valid treatment.")

                    additional_notes = input("Enter any additional notes (optional): ").strip()
                    response = f"Diagnosis: {diagnosis}\nRecommended Treatment: {treatment}\n"
                    if additional_notes:
                        response += f"Additional Notes: {additional_notes}"

                    # Update consultation and store response
                    cursor.execute('''
                        UPDATE consultations 
                        SET status = 'completed', expert_id = ? 
                        WHERE id = ?
                    ''', (expert_id, consultation_id))

                    cursor.execute('''
                        INSERT INTO consultation_responses 
                        (consultation_id, expert_id, expert_response) 
                        VALUES (?, ?, ?)
                    ''', (consultation_id, expert_id, response))
                    print("\nResponse saved successfully.")

                elif choice == "2":
                    # Request more images
                    description = input("Enter description of what you observe: ").strip()
                    symptoms = input("Enter specific symptoms to look for: ").strip()

                    cursor.execute('''
                        INSERT INTO unknown_diseases 
                        (reported_by_farmer_id, verified_by_expert_id, description, 
                        symptoms, status)
                        VALUES (?, ?, ?, ?, 'samples_requested')
                    ''', (consultation[2], expert_id, description, symptoms))

                    cursor.execute('''
                        UPDATE consultations 
                        SET status = 'awaiting_samples', expert_id = ? 
                        WHERE id = ?
                    ''', (expert_id, consultation_id))

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

                else:
                    print("\nInvalid choice! Please try again.")
                    return
                conn.commit()
                # Calculate response time
                response_time = self.calculate_response_time(created_at)

                # Award points to expert
                if self.add_consultation_response_points(expert_id, response_time):
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


    def view_unknown_disease_requests(self, farmer_id):
        """
        View requests for additional samples for unknown diseases.
        """
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Fetch pending sample requests
                cursor.execute('''
                    SELECT ud.id, ud.description, ud.symptoms, 
                        ud.related_consultation_id
                    FROM unknown_diseases ud
                    WHERE ud.reported_by_farmer_id = ? 
                    AND ud.status = 'samples_requested'
                ''', (farmer_id,))
                requests = cursor.fetchall()

                if not requests:
                    print("\nNo pending requests for disease samples.")
                    return

                # Display pending requests
                print("\n=== Pending Sample Requests ===")
                for req in requests:
                    print(f"\nRequest ID: {req[0]}")
                    print(f"Description: {req[1]}")
                    print(f"Symptoms to Document: {req[2]}")
                    print("-" * 50)

                # Input request ID
                while True:
                    req_id = input("\nEnter request ID to submit samples (or press Enter to skip): ").strip()
                    if not req_id:
                        print("No request selected. Returning to the menu.")
                        return
                    elif req_id.isdigit():
                        req_id = int(req_id)
                        if any(req[0] == req_id for req in requests):
                            break
                        else:
                            print("Error: Invalid Request ID. Please try again.")
                    else:
                        print("Error: Request ID must be a number. Please try again.")

                # Input sample file path
                while True:
                    samples_path = input("Enter path to samples zip file: ").strip('"').strip("'")
                    if os.path.exists(samples_path):
                        break
                    else:
                        print("Error: File not found. Please provide a valid path.")

                # Submit disease samples
                self.submit_disease_samples(farmer_id, req_id, samples_path)

            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                conn.close()



