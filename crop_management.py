from db import create_connection
import re
from datetime import datetime

class CropManagement:
    def add_crop(self, farmer_id):
        print("\n=== Add New Crop ===")
        
        # Validate crop name: Only alphabetic characters and spaces
        while True:
            crop_name = input("Enter crop name: ").strip()
            if re.match("^[A-Za-z ]+$", crop_name):  # Matches only alphabets and spaces
                break
            else:
                print("Error: Crop name can only contain alphabetic characters and spaces.")
        
        # Validate variety: Only alphabetic characters and spaces (optional)
        while True:
            variety = input("Enter variety (if any): ").strip()
            if variety == "" or re.match("^[A-Za-z ]+$", variety):  # Allows empty or alphabetic characters and spaces
                break
            else:
                print("Error: Variety can only contain alphabetic characters and spaces.")
        
        # Date validation: ensure the entered date is not in the future
        while True:
            planting_date = input("Enter planting date (YYYY-MM-DD): ").strip()
            try:
                # Try to parse the date
                planting_date_obj = datetime.strptime(planting_date, "%Y-%m-%d")
                
                # Check if the planting date is in the future
                if planting_date_obj > datetime.now():
                    print("Error: Planting date cannot be in the future. Please enter a valid date.")
                else:
                    break  # Valid date entered, exit the loop
            except ValueError:
                print("Error: Invalid date format. Please enter the date in YYYY-MM-DD format.")
        
        # Validate notes: Only alphabetic characters and spaces
        while True:
            notes = input("Enter any additional notes: ").strip()
            if re.match("^[A-Za-z ]*$", notes):  # Allows alphabetic characters and spaces, empty is allowed
                break
            else:
                print("Error: Notes can only contain alphabetic characters and spaces.")

        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO crops (user_id, crop_name, variety, planting_date, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (farmer_id, crop_name, variety, planting_date, notes))
                conn.commit()
                print("Crop added successfully!")
            except Exception as e:
                print(f"Error adding crop: {e}")
            finally:
                conn.close()

    def view_crops(self, farmer_id):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, crop_name, variety, planting_date, notes
                    FROM crops
                    WHERE user_id = ?
                ''', (farmer_id,))
                crops = cursor.fetchall()
                if crops:
                    print("\n=== Your Crops ===")
                    for crop in crops:
                        print(f"\nCrop ID: {crop[0]}")
                        print(f"Crop Name: {crop[1]}")
                        print(f"Variety: {crop[2]}")
                        print(f"Planting Date: {crop[3]}")
                        print(f"Notes: {crop[4]}")
                        print("-" * 50)
                else:
                    print("You have no crops.")
            except Exception as e:
                print(f"Error fetching crops: {e}")
            finally:
                conn.close()

    def edit_crop(self, farmer_id):
        self.view_crops(farmer_id)
        crop_id = input("\nEnter Crop ID to edit (or 'back' to return): ").strip()
        if crop_id.lower() == 'back':
            return
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, crop_name, variety, planting_date, notes
                    FROM crops
                    WHERE id = ? AND user_id = ?
                ''', (crop_id, farmer_id))
                crop = cursor.fetchone()
                if crop:
                    print("\nLeave a field empty to keep the current value.")
                    crop_name = input(f"Enter new crop name (current: {crop[1]}): ").strip()
                    variety = input(f"Enter new variety (current: {crop[2]}): ").strip()
                    planting_date = input(f"Enter new planting date (YYYY-MM-DD) (current: {crop[3]}): ").strip()
                    notes = input(f"Enter new notes (current: {crop[4]}): ").strip()

                    # If a field is empty, keep the old value
                    crop_name = crop_name if crop_name else crop[1]
                    variety = variety if variety else crop[2]
                    planting_date = planting_date if planting_date else crop[3]
                    notes = notes if notes else crop[4]

                    cursor.execute('''
                        UPDATE crops
                        SET crop_name = ?, variety = ?, planting_date = ?, notes = ?
                        WHERE id = ? AND user_id = ?
                    ''', (crop_name, variety, planting_date, notes, crop_id, farmer_id))
                    conn.commit()
                    print("Crop updated successfully!")
                else:
                    print("Crop not found.")
            except Exception as e:
                print(f"Error editing crop: {e}")
            finally:
                conn.close()

    def delete_crop(self, farmer_id):
        self.view_crops(farmer_id)
        crop_id = input("\nEnter Crop ID to delete (or 'back' to return): ").strip()
        if crop_id.lower() == 'back':
            return
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM crops
                    WHERE id = ? AND user_id = ?
                ''', (crop_id, farmer_id))
                if cursor.rowcount > 0:
                    conn.commit()
                    print("Crop deleted successfully!")
                else:
                    print("Crop not found or you do not have permission to delete it.")
            except Exception as e:
                print(f"Error deleting crop: {e}")
            finally:
                conn.close()

