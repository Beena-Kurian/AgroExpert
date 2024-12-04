from db import create_connection
import re
from datetime import datetime

class DiseaseOutbreak:
    def create_alert(self):
        print("\n=== Create Disease Outbreak Alert ===")
        
        # Validate disease name
        disease_name = input("Enter disease name: ").strip()
        if not disease_name or not re.match("^[A-Za-z\s]+$", disease_name):
            print("Invalid input! Disease name should only contain alphabets and spaces.")
            return
        
        # Validate affected crop
        affected_crop = input("Enter affected crop: ").strip()
        if not affected_crop or not re.match("^[A-Za-z\s]+$", affected_crop):
            print("Invalid input! Affected crop should only contain alphabets and spaces.")
            return
        
        # Validate affected region
        region = input("Enter affected region: ").strip()
        if not region or not re.match("^[A-Za-z\s]+$", region):
            print("Invalid input! Region should only contain alphabets and spaces.")
            return
        
        # Validate description
        description = input("Enter alert description: ").strip()
        if not description:
            print("Invalid input! Description cannot be empty.")
            return
        
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO disease_alerts (disease_name, affected_crop, region, description)
                    VALUES (?, ?, ?, ?)
                ''', (disease_name, affected_crop, region, description))
                conn.commit()
                alert_id = cursor.lastrowid
                print(f"Alert created successfully with ID: {alert_id}")
                self.notify_farmers(alert_id, affected_crop)
            except Exception as e:
                print(f"Error creating alert: {e}")
            finally:
                conn.close()
    
    def notify_farmers(self, alert_id, affected_crop):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Query to select farmers with the affected crop (ignores region)
                cursor.execute('''
                    SELECT DISTINCT u.id, u.username, u.email
                    FROM users u
                    JOIN crops c ON u.id = c.user_id
                    WHERE LOWER(c.crop_name) = LOWER(?)
                ''', (affected_crop,))  # Case-insensitive crop name search
                affected_farmers = cursor.fetchall()
                
                if not affected_farmers:
                    print("No farmers found for the specified crop.")
                    return

                for farmer in affected_farmers:
                    # Notify farmers (In a real system, this would send an email or notification)
                    print(f"Notifying farmer: {farmer[1]} (Email: {farmer[2]})")
                    
                    # Insert a notification for the farmer with viewed set to 0 (unviewed)
                    cursor.execute('''
                        INSERT INTO farmer_notifications (user_id, alert_id, viewed)
                        VALUES (?, ?, 0)
                    ''', (farmer[0], alert_id))
                
                conn.commit()
                print(f"Notified {len(affected_farmers)} farmers about the outbreak.")
            except Exception as e:
                print(f"Error notifying farmers: {e}")
            finally:
                conn.close()

    def view_alerts_for_admin(self):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, disease_name, affected_crop, region, description, created_at
                    FROM disease_alerts
                    ORDER BY created_at DESC
                ''')
                alerts = cursor.fetchall()

                if alerts:
                    print("\n=== Disease Outbreak Alerts ===")
                    for alert in alerts:
                        print(f"\nAlert ID: {alert[0]}")
                        print(f"Disease: {alert[1]}")
                        print(f"Affected Crop: {alert[2]}")
                        print(f"Region: {alert[3]}")
                        print(f"Description: {alert[4]}")
                        print(f"Created At: {alert[5]}")
                        print("-" * 50)
                else:
                    print("No disease outbreak alerts found.")
            except Exception as e:
                print(f"Error viewing alerts: {e}")
            finally:
                conn.close()

    def view_alerts_for_farmer(self, user_id):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Fetch unviewed notifications for this user
                cursor.execute('''
                    SELECT da.disease_name, da.affected_crop, da.region, da.description, fn.notified_at, fn.id
                    FROM farmer_notifications fn
                    JOIN disease_alerts da ON fn.alert_id = da.id
                    WHERE fn.user_id = ? AND fn.viewed = 0  -- Only fetch unviewed notifications
                    ORDER BY fn.notified_at DESC
                ''', (user_id,))
                alerts = cursor.fetchall()

                if alerts:
                    print("\n=== Your Disease Outbreak Alerts ===")
                    for alert in alerts:
                        # Format the notified_at date for better readability
                        notified_at = datetime.strptime(alert[4], "%Y-%m-%d %H:%M:%S")  # Adjust format as needed
                        print(f"Disease: {alert[0]}")
                        print(f"Affected Crop: {alert[1]}")
                        print(f"Region: {alert[2]}")
                        print(f"Description: {alert[3]}")
                        print(f"Notified At: {notified_at.strftime('%b %d, %Y %H:%M:%S')}")
                        print("-" * 50)

                    # Ask if the farmer wants to mark the notifications as viewed
                    user_input = input("Do you want to mark all notifications as viewed? (y/n): ")
                    if user_input.lower() == 'y':
                        self.mark_all_notifications_as_viewed(user_id)

                else:
                    print("You have no new disease alerts.")
            except Exception as e:
                print(f"Error fetching alerts: {e}")
            finally:
                conn.close()

    def mark_all_notifications_as_viewed(self, user_id):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Update all unviewed notifications for the farmer
                cursor.execute('''
                    UPDATE farmer_notifications
                    SET viewed = 1
                    WHERE user_id = ? AND viewed = 0
                ''', (user_id,))
                conn.commit()
                print(f"All notifications marked as viewed for user {user_id}.")
            except Exception as e:
                print(f"Error updating notifications: {e}")
            finally:
                conn.close()
