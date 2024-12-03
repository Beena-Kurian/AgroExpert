from auth import Auth
from disease_identification import DiseaseIdentification
from expert_consultation import ExpertConsultation
from rewards import *
from news_updates import NewsUpdates
from update_profile import update_contact_information
import os
from crop_management import *


class AgroExpert:
    def __init__(self):
        self.auth = Auth()
        self.current_user = None
        self.disease_identifier = DiseaseIdentification()
        self.news = NewsUpdates()
        # Initialize the appropriate reward system based on user role
        self.farmer_rewards = FarmerRewards()  # For Farmer-specific rewards
        self.expert_rewards = ExpertRewards()  # For Expert-specific rewards
        self.consultation = ExpertConsultation(self.disease_identifier, self.expert_rewards)
        self.crop_management = CropManagement()

        
    def display_menu(self):
        while True:
            if not self.current_user:
                print("\n=== AgroExpert System ===")
                print("1. Login")
                print("2. Register")
                print("3. Exit")
                
                choice = input("Enter your choice (1-3): ")
                
                if choice == '1':
                    self.current_user = self.auth.display_login_menu()
                elif choice == '2':
                    self.auth.display_registration_menu()
                elif choice == '3':
                    print("Thank you for using AgroExpert!")
                    break
                else:
                    print("Invalid choice! Please try again.")
            else:
                self.display_user_menu()

    def display_user_menu(self):
        role = self.current_user['role']
        if role == 'farmer':
            # # Notify farmer about replies
            print("----------------------Notifications---------------:\n")
            self.consultation.notify_farmer_replies(self.current_user['id'])
            self.display_farmer_menu()
        elif role == 'expert':
            # Notify expert about new messages
            print("----------------------Notifications---------------:\n")
            self.consultation.notify_expert_new_messages(self.current_user['id'])
            self.display_expert_menu()
        else:
            print("Invalid role! Please try again.")
            self.current_user = None

    def display_farmer_menu(self):
        while True:
            print("\n=== Farmer Menu ===")
            print("1. Upload Image for Disease Identification")
            print("2. Request Expert Consultation")
            print("3. View My Consultation Responses")
            print("4. View Sample Requests") 
            print("5. View My Rewards")
            print("6. View News")
            print("7. Update Profile")
            print("8. Manage My Crops")
            print("9. Logout")
            
            choice = input("Enter your choice (1-7): ")
            
            if choice == '1':
                self.disease_identifier.handle_image_upload(self.current_user['id'])
            elif choice == '2':
                self.consultation.create_new_consultation(self.current_user['id'])
            elif choice == '3':
                self.consultation.view_farmer_consultations(self.current_user['id'])
            elif choice == '4':
                self.consultation.view_unknown_disease_requests(self.current_user['id'])  
            elif choice == '5':
                display_rewards_menu(self.current_user['id'], 'farmer')
            elif choice == '6':
                self.news.display_news_for_user()
            elif choice == '7':
                update_contact_information(self.current_user['id'])
            elif choice == '8':
                self.manage_crops()
            elif choice == '9':
                self.current_user = None
                break
            else:
                print("Invalid choice! Please try again.")
    
    def manage_crops(self):
        while True:
            print("\n=== Crop Management ===")
            print("1. View My Crops")
            print("2. Add New Crop")
            print("3. Edit Crop")
            print("4. Delete Crop")
            print("5. Back to Farmer Menu")
            choice = input("Enter your choice (1-5): ")
            if choice == '1':
                self.crop_management.view_crops(self.current_user['id'])
            elif choice == '2':
                self.crop_management.add_crop(self.current_user['id'])
            elif choice == '3':
                self.crop_management.edit_crop(self.current_user['id'])
            elif choice == '4':
                self.crop_management.delete_crop(self.current_user['id'])
            elif choice == '5':
                break
            else:
                print("Invalid choice! Please try again.")
                
    def display_expert_menu(self):
        while True:
            print("\n=== Expert Menu ===")
            print("1. View Pending Consultations")
            print("2. View My Rewards")
            print("3. View News")
            print("4. Update Profile")
            print("5. Logout")
            
            choice = input("Enter your choice (1-4): ")
            
            if choice == '1':
                self.consultation.view_pending_consultations(self.current_user['id'])
            elif choice == '2':
                display_rewards_menu(self.current_user['id'], 'expert')
            elif choice == '3':
                self.news.display_news_for_user()
            elif choice == '4':
                update_contact_information(self.current_user['id'])
            elif choice == '5':
                self.current_user = None
                break
            else:
                print("Invalid choice! Please try again.")
if __name__ == "__main__":
    app = AgroExpert()
    app.display_menu()
