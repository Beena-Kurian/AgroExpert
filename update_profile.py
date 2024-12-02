import re
from db import create_connection

def check_existing_user(field, value):
    """
    Check if a user with the given field (username or email) exists in the database.
    """
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        query = f"SELECT COUNT(*) FROM users WHERE {field} = ?"
        cursor.execute(query, (value,))
        result = cursor.fetchone()
        return result[0] > 0

def get_user_contact_info(user_id):
    """
    Fetch the current email and phone number for a user.
    """
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT email, phone FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        return result  # Returns (email, phone)

def update_contact_information(user_id):
    """
    Allow the user to update their email or phone number.
    """
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            print("\n=== Update Contact Information ===")
            
            # Fetch current contact information
            current_email, current_phone = get_user_contact_info(user_id)
            print(f"Current Email: {current_email}")
            print(f"Current Phone: {current_phone}")
            
            while True:
                print("\n1. Update Email")
                print("2. Update Phone Number")
                print("3. Go Back")
                update_choice = input("Enter your choice (1-3): ")
                
                if update_choice == '1':
                    # Update email
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    new_email = input(f"Enter new email : ")
                    
                    # Check if new email is different from the current one
                    if new_email == current_email:
                        print("The new email is the same as the current email. No changes made.")
                        continue
                    
                    # Validate email format
                    if not re.match(email_pattern, new_email):
                        print("Invalid email format! Please try again.")
                        continue
                    
                    # Check if the new email already exists
                    if check_existing_user(field='email', value=new_email):
                        print("Email already exists! Please use a different email.")
                        continue
                    
                    # Update email in the database
                    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
                    conn.commit()
                    print("Email updated successfully!")
                
                elif update_choice == '2':
                    # Update phone number
                    phone_pattern = r'^\d{10}$'
                    new_phone = input(f"Enter new phone number: ")
                    
                    # Check if new phone number is different from the current one
                    if new_phone == current_phone:
                        print("The new phone number is the same as the current phone number. No changes made.")
                        continue
                    
                    # Validate phone number format
                    if not re.match(phone_pattern, new_phone):
                        print("Invalid phone number! Please enter a 10-digit number.")
                        continue
                    
                    # Check if the new phone number already exists
                    if check_existing_user(field='phone', value=new_phone):
                        print("Phone number already exists! Please use a different phone number.")
                        continue
                    
                    # Update phone number in the database
                    cursor.execute("UPDATE users SET phone = ? WHERE id = ?", (new_phone, user_id))
                    conn.commit()
                    print("Phone number updated successfully!")
                
                elif update_choice == '3':
                    break
                else:
                    print("Invalid choice! Please try again.")
        
        except Exception as e:
            print(f"An error occurred while updating contact information: {e}")
        finally:
            conn.close()
