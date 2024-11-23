import os
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from db import create_connection
from gift_card import *

class AdminFunctions:

    def display_admin_menu(self):
        while True:
            print("\n=== Admin Menu ===")
            print("1. User Management")
            print("2. Manage News")
            print("3. View System Statistics")
            print("4. Model Management")
            print("5. Gift Card Management")  
            print("6. Logout")
            
            choice = input("Enter your choice (1-5): ")
            
            if choice == '1':
                self.user_management_menu()  
            elif choice == '2':
                self.manage_news()
            elif choice == '3':
                self.view_system_statistics()  
            elif choice == '4':
                self.model_management_menu()  
            elif choice == '5':
                self.gift_card_management_menu()
            elif choice == '6':    
                self.current_user = None
                break
            else:
                print("Invalid choice! Please try again.")
    def user_management_menu(self):
        while True:
            print("\n=== User Management ===")
            print("1. View All Users")
            print("2. Approve/Reject Expert Registrations")
            print("3. Back to Admin Menu")

            choice = input("\nEnter your choice (1-3): ")

            if choice == '1':
                self.view_all_users()
            elif choice == '2':
                self.manage_expert_registrations()
            elif choice == '3':
                break
    def view_all_users(self):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, role, email, status 
                    FROM users 
                    ORDER BY role, username
                ''')
                users = cursor.fetchall()
                
                print("\n=== All Users ===")
                if not users:
                    print("No users found.")
                else:
                    for user in users:
                        print(f"\nID: {user[0]}")
                        print(f"Username: {user[1]}")
                        print(f"Role: {user[2]}")
                        print(f"Email: {user[3]}")
                        print(f"Status: {user[4]}")
                        print("-" * 30)
            finally:
                conn.close()

    def manage_expert_registrations(self):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, email 
                    FROM users 
                    WHERE role = 'expert' AND status = 'pending'
                ''')
                pending_experts = cursor.fetchall()

                if not pending_experts:
                    print("\nNo pending expert registrations.")
                    return

                print("\n=== Pending Expert Registrations ===")
                for expert in pending_experts:
                    print(f"\nID: {expert[0]}")
                    print(f"Username: {expert[1]}")
                    print(f"Email: {expert[2]}")
                    
                    while True:
                        choice = input("Approve or Reject? (A/R): ").upper()
                        if choice in ['A', 'R']:
                            new_status = 'active' if choice == 'A' else 'rejected'
                            cursor.execute('''
                                UPDATE users 
                                SET status = ? 
                                WHERE id = ?
                            ''', (new_status, expert[0]))
                            break
                
                conn.commit()
                print("Expert registrations processed successfully!")
            finally:
                conn.close()
    def model_management_menu(self):
        while True:
            print("\n=== Model Management ===")
            print("1. Train New Model")
            print("2. View Model Versions")
            print("3. View Current Classes")
            print("4. Activate Model") 
            print("5. Back")

            choice = input("\nEnter your choice (1-5): ")

            if choice == '1':
                self.train_new_model()
            elif choice == '2':
                self.view_model_versions()
            elif choice == '3':
                self.view_model_classes()
            elif choice == '4':
                self.activate_model()  
            elif choice == '5':
                break

    def view_model_versions(self):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT version_number, accuracy, total_classes, 
                        training_date, description, is_active 
                    FROM model_versions 
                    ORDER BY training_date DESC
                ''')
                versions = cursor.fetchall()
                
                print("\n=== Model Versions ===")
                for version in versions:
                    print(f"\nVersion: {version[0]}")
                    print(f"Accuracy: {version[1]*100:.2f}%")
                    print(f"Total Classes: {version[2]}")
                    print(f"Training Date: {version[3]}")
                    print(f"Description: {version[4]}")
                    print(f"Active: {'Yes' if version[5] else 'No'}")
                    print("-" * 30)
            finally:
                conn.close()

    def view_system_statistics(self):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Get user statistics
                cursor.execute('''
                    SELECT role, COUNT(*) 
                    FROM users 
                    GROUP BY role
                ''')
                user_stats = cursor.fetchall()
                
                # Get consultation statistics
                cursor.execute('''
                    SELECT status, COUNT(*) 
                    FROM consultations 
                    GROUP BY status
                ''')
                consultation_stats = cursor.fetchall()
                
                # Get disease prediction statistics
                cursor.execute('''
                    SELECT disease_name, COUNT(*) 
                    FROM disease_predictions 
                    GROUP BY disease_name 
                    ORDER BY COUNT(*) DESC 
                    LIMIT 5
                ''')
                disease_stats = cursor.fetchall()

                print("\n=== System Statistics ===")

                # User statistics
                print("\nUser Statistics:")
                if user_stats:
                    for role, count in user_stats:
                        print(f"{role.capitalize()}: {count}")
                else:
                    print("No user statistics available.")

                # Consultation statistics
                print("\nConsultation Statistics:")
                if consultation_stats:
                    for status, count in consultation_stats:
                        print(f"{status.capitalize()}: {count}")
                else:
                    print("No consultation statistics available.")

                # Disease statistics
                print("\nTop 5 Identified Diseases:")
                if disease_stats:
                    for disease, count in disease_stats:
                        print(f"{disease}: {count} times")
                else:
                    print("No disease prediction statistics available.")

            finally:
                conn.close()


    def manage_news(self):
        while True:
            print("\n=== News Management ===")
            print("1. Add News")
            print("2. View All News")
            print("3. Delete News")
            print("4. Back")

            choice = input("\nEnter your choice (1-4): ")

            if choice == '1':
                title = input("Enter news title: ")
                print("Enter news content (press Enter twice to finish):")
                content_lines = []
                while True:
                    line = input()
                    if line == "":
                        break
                    content_lines.append(line)
                content = "\n".join(content_lines)
                self.add_news(title, content)
            elif choice == '2':
                self.view_all_news()
            elif choice == '3':
                self.delete_news()
            elif choice == '4':
                break

    def add_news(self, title, content):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO news (title, content, created_at)
                    VALUES (?, ?, datetime('now'))
                ''', (title, content))
                conn.commit()
                print("\nNews added successfully!")
            except Exception as e:
                print(f"Error adding news: {e}")
            finally:
                conn.close()

    def view_all_news(self):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT id, title, content, created_at FROM news ORDER BY created_at DESC')
                news_items = cursor.fetchall()
                
                if not news_items:
                    print("\nNo news items found.")
                    return
                
                print("\n=== All News Items ===")
                for item in news_items:
                    print(f"\nID: {item[0]}")
                    print(f"Title: {item[1]}")
                    print(f"Content: {item[2]}")
                    print(f"Date: {item[3]}")
                    print("-" * 50)
            finally:
                conn.close()

    def delete_news(self):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT id, title FROM news')
                news_items = cursor.fetchall()
                
                if not news_items:
                    print("\nNo news items found to delete.")
                    return
                
                print("\n=== All News ===")
                for news in news_items:
                    print(f"ID: {news[0]}, Title: {news[1]}")
                
                news_id = input("\nEnter the ID of the news to delete (or 'back'): ")
                if news_id.lower() == 'back':
                    return
                
                cursor.execute('DELETE FROM news WHERE id = ?', (news_id,))
                if cursor.rowcount > 0:
                    conn.commit()
                    print("\nNews deleted successfully!")
                else:
                    print("\nNews item not found!")
            finally:
                conn.close()

    def get_valid_path(self, prompt):
        while True:
            path = input(prompt).strip()

            if not path:
                print("Invalid path: Path cannot be empty.")
                continue

            if not os.path.exists(path):
                print(f"Invalid path: Path '{path}' does not exist.")
                continue

            if not os.path.isdir(path):
                print(f"Invalid path: '{path}' is not a directory.")
                continue

            return path

    def get_valid_basepath(self):
        return self.get_valid_path("Enter path to base dataset: ")
    def get_valid_dataset_path(self):
        return self.get_valid_path("\nEnter the path of the trained dataset: ")    
    def get_new_disease_dataset_path(self):
        return self.get_valid_path("Enter path to new disease folders: ")
    def test_model_predictions(self, model, test_ds, class_names, num_samples=5):
        """
        Test model predictions on sample images and save results
        """
        # Create a large figure for displaying multiple images
        plt.figure(figsize=(20, 4))
        
        # Get one batch of test images
        for images, labels in test_ds.take(1):  # take 1 batch
            # Display predictions for num_samples images
            for i in range(min(num_samples, len(images))):
                # Create subplot for each image
                plt.subplot(1, num_samples, i+1)
                
                # Display the image
                img = images[i].numpy().astype('uint32')
                plt.imshow(img)
                plt.axis('off')
                
                # Get actual label
                actual = class_names[labels[i]]
                
                # Get prediction
                img_expanded = tf.expand_dims(images[i], 0)  # Add batch dimension
                prediction = model.predict(img_expanded)
                predicted_class_idx = np.argmax(prediction)
                predict = class_names[predicted_class_idx]
                
                # Set title with actual and predicted labels
                # Use green if correct, red if wrong
                color = 'green' if actual == predict else 'red'
                plt.title(f'Actual: {actual}\nPredicted: {predict}', 
                        color=color, 
                        fontsize=10)
        
        # Adjust layout and save plot
        plt.tight_layout()
        plt.savefig('plots/prediction_samples.png')
        plt.close()
        return 'plots/prediction_samples.png'
    
    def get_validated_input(self, prompt, default_value, min_value=None, max_value=None, parameter=None):
        while True:
            user_input = input(prompt)
            if not user_input:
                return default_value

            try:
                if parameter == "epoch":
                    value = int(user_input)  # Ensure integer input for epochs
                    if value < min_value:
                        print(f"Value must be greater than or equal to {min_value}")
                    elif value > max_value:
                        print(f"Value must be less than or equal to {max_value}")
                    else:
                        return value
                if parameter == "lr":
                    value = float(user_input)  
                    if value < min_value:
                        print(f"Value must be greater than or equal to {min_value}")
                    elif value > max_value:
                        print(f"Value must be less than or equal to {max_value}")
                    else:
                        return value
            except ValueError:
                print("Invalid input..")

    def train_new_model(self):
        from model_training import ModelTrainer

        print("\n=== Train New Model ===")
        print("1. Train with existing classes")
        print("2. Train with existing classes + new disease classes")
        choice = input("Enter choice (1-2): ")

        # Get training parameters
        epochs = self.get_validated_input("Enter number of epochs (default 15): ", 15, 1, 50, "epoch")
        learning_rate = self.get_validated_input("Enter learning rate (default 0.001): ", 0.001, 0.0001, 0.1,"lr")
        base_path = self.get_valid_basepath()
        trainer = ModelTrainer()
        
        if choice == "2":
            new_disease_path = self.get_new_disease_dataset_path()
            trainer.prepare_dataset(base_path, new_disease_path)
        else:
            trainer.prepare_dataset(base_path)

        # Build and train model
        num_classes = len(trainer.class_names)
        model = trainer.build_model(num_classes)
        print("\nModel architecture:")
        model.summary()

        print("\nStarting training...")
        history = trainer.train_model(epochs=epochs, learning_rate=learning_rate)

        # Evaluate model
        accuracy = trainer.evaluate_model()
        print(f"\nTest Accuracy: {accuracy*100:.2f}%")

        # Plot results
        acc_plot, loss_plot = trainer.plot_training_results()
        print(f"\nTraining plots saved to: {acc_plot} and {loss_plot}")

        # Test predictions
    
        pred_plot = self.test_model_predictions(trainer.model, trainer.test_ds, trainer.class_names)

        print(f"Prediction samples saved to: {pred_plot}")

        # Save model if accuracy is good
        if accuracy > 0.7:  # You can adjust this threshold
            version = input("\nEnter version number for new model: ")
            description = input("Enter model description: ")
            model_path = trainer.save_model(version, description)
            
            # Record in database
            conn = create_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO model_versions 
                        (model_path, version_number, accuracy, total_classes, 
                        description, is_active)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (model_path, version, accuracy, num_classes, description, 0))
                    conn.commit()
                    print("\nModel saved and recorded in database successfully!")
                except Exception as e:
                    print(f"Error recording model version: {e}")
                finally:
                    conn.close()
        else:
            print("\nModel accuracy too low. Consider adjusting parameters and training again.")
    def view_model_classes(self):
        try:
            conn = create_connection() 
            if conn:
                cursor = conn.cursor()
                # Execute query to fetch all model classes
                cursor.execute("SELECT class_index, class_name, date_added FROM model_classes")
                rows = cursor.fetchall()
                
                if rows:
                    print("\n=== Model Classes ===")
                    print("Class Index | Class Name     | Date Added")
                    print("-" * 50)  
                    for row in rows:
                        formatted_date = row[2] if isinstance(row[2], str) else row[2].strftime('%Y-%m-%d')
                        print(f"{row[0]:<12} | {row[1]:<15} | {formatted_date}")
                else:
                    print("No model classes found.")
                
                # Close the database connection and cursor
                cursor.close()
                conn.close()

        except Exception as e:
            print(f"Error accessing the database: {e}")
    import os



    def activate_model(self):
        print("\n=== Activate Model ===")
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Show all model versions
                cursor.execute('''
                    SELECT id, version_number, accuracy, total_classes, 
                        training_date, description, is_active, model_path
                    FROM model_versions
                    ORDER BY training_date DESC
                ''')
                versions = cursor.fetchall()
                ids = []
                print("\nAvailable Model Versions:")
                for version in versions:
                    print(f"\nID: {version[0]}")
                    ids.append(version[0])
                    print(f"Version: {version[1]}")
                    print(f"Accuracy: {version[2]*100:.2f}%")
                    print(f"Classes: {version[3]}")
                    print(f"Date: {version[4]}")
                    print(f"Description: {version[5]}")
                    print(f"Active: {'Yes' if version[6] else 'No'}")
                    print("-" * 30)
                
                # get model id to activate
                model_id = input("\nEnter the ID of the model to activate (or 'back' to return): ").strip()
                if model_id.lower() == 'back':
                    return
                #  Check if the model ID exists before getting dataset path
                cursor.execute("SELECT * FROM model_versions WHERE id = ?", (model_id,))
                model_info = cursor.fetchone()
                if not model_info:
                    print(f"Model with ID {model_id} not found.")
                    return
                # get the dataset path to get class information
                dataset_path = self.get_valid_dataset_path()

                if model_id.lower() != 'back':
                    try:
                        # Get model details including path
                        cursor.execute('''
                            SELECT model_path, total_classes 
                            FROM model_versions 
                            WHERE id = ?
                        ''', (model_id,))
                        model_info = cursor.fetchone()
                        
                        if model_info:
                            model_path = model_info[0]
                            total_classes = model_info[1]
                            
                            # Load the model to get class names
                            model = tf.keras.models.load_model(model_path)
                                                       
                            if os.path.exists(dataset_path):
                                temp_ds = tf.keras.utils.image_dataset_from_directory(
                                    dataset_path,
                                    image_size=(224, 224),
                                    batch_size=32
                                )
                                new_classes = temp_ds.class_names
                                
                                # First deactivate all models
                                cursor.execute('UPDATE model_versions SET is_active = 0')
                                
                                # Activate selected model
                                cursor.execute('''
                                    UPDATE model_versions 
                                    SET is_active = 1 
                                    WHERE id = ?
                                ''', (model_id,))
                                
                                # Update model classes
                                cursor.execute('DELETE FROM model_classes')  # Clear existing classes
                                
                                # Insert new classes
                                for class_name in new_classes:
                                    cursor.execute('''
                                        INSERT INTO model_classes (class_name)
                                        VALUES (?)
                                    ''', (class_name,))
                                
                                conn.commit()
                                print("\nModel activated and classes updated successfully!")
                                print(f"\nNew classes added: {len(new_classes)}")
                                print("Use 'View Current Classes' to see the updated list.")
                            else:
                                print(f"\nError: Dataset directory not found  {dataset_path}")
                    except Exception as e:
                        print(f"\nError activating model: {e}")
                        conn.rollback()
            finally:
                conn.close()

    def gift_card_management_menu(self):
        """Menu for managing gift cards."""
        while True:
            print("\n=== Gift Card Management ===")
            print("1. Add a Single Gift Card")
            print("2. Add Multiple Gift Cards")
            print("3. View All Gift Cards")
            print("4. Deactivate a Gift Card")
            print("5. Back to Admin Menu")
            
            choice = input("Enter your choice (1-5): ")
            
            if choice == '1':
                try:
                    value = int(input("Enter the value of the gift card: "))
                    days_valid = int(input("Enter the number of days the gift card is valid: "))
                    add_coupon(value, days_valid)
                except ValueError:
                    print("Invalid input! Please enter numerical values.")
            elif choice == '2':
                try:
                    value = int(input("Enter the value of the gift cards: "))
                    days_valid = int(input("Enter the number of days the gift cards are valid: "))
                    count = int(input("Enter the number of gift cards to generate: "))
                    add_multiple_coupons(value, days_valid, count)
                except ValueError:
                    print("Invalid input! Please enter numerical values.")
            elif choice == '3':
                view_coupons()
            elif choice == '4':
                try:
                    coupon_id = int(input("Enter the ID of the gift card to deactivate: "))
                    deactivate_coupon(coupon_id)
                except ValueError:
                    print("Invalid input! Please enter a valid gift card ID.")
            elif choice == '5':
                break
            else:
                print("Invalid choice! Please try again.")
                
if __name__ == "__main__":
    admin = AdminFunctions()
    admin.display_admin_menu()