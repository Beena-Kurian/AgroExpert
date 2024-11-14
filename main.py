from auth import Auth
from disease_identification import DiseaseIdentification
from expert_consultation import ExpertConsultation
from rewards import display_rewards_menu
from news_updates import NewsUpdates
import os

class AgroExpert:
    def __init__(self):
        self.auth = Auth()
        self.disease_identifier = DiseaseIdentification()
        self.consultation = ExpertConsultation()
        self.news = NewsUpdates()
        self.current_user = None

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
            self.display_farmer_menu()
        elif role == 'expert':
            self.display_expert_menu()
        else:
            print("Invalid role! Please try again.")
            self.current_user = None
    def display_farmer_menu(self):
        while True:
            print("\n=== Farmer Menu ===")
            print("1. Upload Image for Disease Identification")
            print("2. Request Expert Consultation")
            print("3. View My Consultations")
            print("4. View Sample Requests") 
            print("5. View My Rewards")
            print("6. View News")
            print("7. Logout")
            
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
                self.current_user = None
                break
            else:
                print("Invalid choice! Please try again.")

    def display_expert_menu(self):
        while True:
            print("\n=== Expert Menu ===")
            print("1. View Pending Consultations")
            print("2. View My Rewards")
            print("3. View News")
            print("4. Logout")
            
            choice = input("Enter your choice (1-4): ")
            
            if choice == '1':
                self.consultation.view_pending_consultations(self.current_user['id'])
            elif choice == '2':
                display_rewards_menu(self.current_user['id'], 'expert')
            elif choice == '3':
                self.news.display_news_for_user()
            elif choice == '4':
                self.current_user = None
                break
            else:
                print("Invalid choice! Please try again.")
if __name__ == "__main__":
    app = AgroExpert()
    app.display_menu()
