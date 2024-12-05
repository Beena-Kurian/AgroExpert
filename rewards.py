from db import create_connection
from gift_card import redeem_coupon
from datetime import datetime

class RewardSystem:
    def __init__(self):
        # Point structure for farmers
        self.farmer_points = {
            'consultation_image': 10,  # High-quality image upload for consultation
            'new_disease_images': 500  # 50 images of new disease
        }
        
        # Point structure for experts
        self.expert_points = {
            'consultation_completed': 20,  # For each consultation
            'fast_response': 5  # Bonus for < 24h response
        }

    def get_user_points(self, user_id):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT SUM(points) FROM rewards WHERE user_id = ?', (user_id,))
                result = cursor.fetchone()
                return result[0] if result else 0
            finally:
                conn.close()
        return 0

    def add_points(self, user_id, points):
        """
        Adds points to the user's account. If the user does not exist, creates a new record.
        """
        conn = create_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()

            # Check if the user already has points in the rewards table
            cursor.execute('''
                SELECT points
                FROM rewards
                WHERE user_id = ?
            ''', (user_id,))
            current_points = cursor.fetchone()

            if current_points:
                # Update the existing points
                cursor.execute('''
                    UPDATE rewards
                    SET points = points + ?
                    WHERE user_id = ?
                ''', (points, user_id))
            else:
                # Insert a new row if the user does not exist
                cursor.execute('''
                    INSERT INTO rewards (user_id, points)
                    VALUES (?, ?)
                ''', (user_id, points))

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            print(f"Error adding points: {e}")
            return False
        finally:
            conn.close()

    def deduct_points(self, user_id, points):
        current_points = self.get_user_points(user_id)
        if current_points >= points:
            return self.add_points(user_id, -points)
        return False

    def log_reward_transaction(self, user_id, action, points, description):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO reward_transactions 
                    (user_id, action, points, description, transaction_date)
                    VALUES (?, ?, ?, ?, datetime('now'))
                ''', (user_id, action, points, description))
                conn.commit()
                return True
            finally:
                conn.close()
        return False

class FarmerRewards(RewardSystem):
    def redeem_reward(self, farmer_id, points_to_redeem):
        # Points must be in multiples of 1000
        if points_to_redeem % 1000 != 0:
            return False, "Points must be redeemed in multiples of 1000."

        # Calculate reward amount
        reward_amount = (points_to_redeem / 1000) * 10  # $10 for every 1000 points

        # Connect to the database
        conn = create_connection()
        if not conn:
            return False, "Database connection failed."

        try:
            cursor = conn.cursor()

            # Check for available gift cards
            cursor.execute('''
                SELECT code
                FROM coupons
                WHERE value = ? AND is_active = 1
                LIMIT 1
            ''', (reward_amount,))
            gift_card = cursor.fetchone()

            if not gift_card:
                return False, f"No available gift cards for ${reward_amount}. Check back later."

            gift_card_code = gift_card[0]
            # print("Debug- gift_card_code: ", gift_card_code)

            # Deduct points from farmer's account
            if not self.deduct_points(farmer_id, points_to_redeem):
                return False, "Insufficient points to redeem."

            # Use the `redeem_coupon` function to handle coupon redemption
            redeem_coupon(farmer_id, gift_card_code)

            # Log the reward transaction
            self.log_reward_transaction(
                farmer_id,
                'redemption',
                -points_to_redeem,
                f'Redeemed points for gift card {gift_card_code} (${reward_amount}).'
            )

            return True, f"Successfully redeemed {points_to_redeem} points for gift card {gift_card_code} (${reward_amount})."

        except Exception as e:
            conn.rollback()
            return False, f"An error occurred during redemption: {str(e)}"

        finally:
            conn.close()

class ExpertRewards(RewardSystem):

    # def redeem_reward(self, expert_id, points_to_redeem):
    #     if points_to_redeem % 1000 != 0:
    #         return False, "Points must be redeemed in multiples of 1000"
        
    #     if self.deduct_points(expert_id, points_to_redeem):
    #         reward_amount = (points_to_redeem / 1000) * 10  # $10 for every 1000 points
    #         self.log_reward_transaction(
    #             expert_id,
    #             'redemption',
    #             -points_to_redeem,
    #             f'Redeemed points for ${reward_amount} gift card'
    #         )
    #         return True, f"Successfully redeemed {points_to_redeem} points for ${reward_amount} gift card"
    #     return False, "Insufficient points"
    def redeem_reward(self, expert_id, points_to_redeem):
        # Points must be in multiples of 1000
        if points_to_redeem % 1000 != 0:
            return False, "Points must be redeemed in multiples of 1000."

        # Calculate reward amount
        reward_amount = (points_to_redeem / 1000) * 10  # $10 for every 1000 points

        # Connect to the database
        conn = create_connection()
        if not conn:
            return False, "Database connection failed."

        try:
            cursor = conn.cursor()

            # Check for available gift cards
            cursor.execute('''
                SELECT code
                FROM coupons
                WHERE value = ? AND is_active = 1
                LIMIT 1
            ''', (reward_amount,))
            gift_card = cursor.fetchone()

            if not gift_card:
                return False, f"No available gift cards for ${reward_amount}. Check back later."

            gift_card_code = gift_card[0]
            # print("Debug- gift_card_code: ", gift_card_code)

            # Deduct points from farmer's account
            if not self.deduct_points(expert_id, points_to_redeem):
                return False, "Insufficient points to redeem."

            # Use the `redeem_coupon` function to handle coupon redemption
            redeem_coupon(expert_id, gift_card_code)

            # Log the reward transaction
            self.log_reward_transaction(
                expert_id,
                'redemption',
                -points_to_redeem,
                f'Redeemed points for gift card {gift_card_code} (${reward_amount}).'
            )

            return True, f"Successfully redeemed {points_to_redeem} points for gift card {gift_card_code} (${reward_amount})."

        except Exception as e:
            conn.rollback()
            return False, f"An error occurred during redemption: {str(e)}"

        finally:
            conn.close()

def display_rewards_menu(user_id, user_role):
    if user_role == 'farmer':
        rewards = FarmerRewards()
    else:
        rewards = ExpertRewards()

    while True:
        print("\n=== Rewards Menu ===")
        print(f"Current Points: {rewards.get_user_points(user_id)}")
        print("\n1. View Points History")
        print("2. Redeem Points")
        print("3. Back to Main Menu")

        choice = input("\nEnter your choice (1-3): ")

        if choice == '1':
            display_points_history(user_id)
        elif choice == '2':
            handle_point_redemption(user_id, rewards)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

def display_points_history(user_id):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT action, points, description, transaction_date 
                FROM reward_transactions 
                WHERE user_id = ? 
                ORDER BY transaction_date DESC
                LIMIT 10
            ''', (user_id,))
            transactions = cursor.fetchall()
            
            print("\n=== Recent Points History ===")
            for trans in transactions:
                print(f"\nAction: {trans[0]}")
                print(f"Points: {trans[1]}")
                print(f"Description: {trans[2]}")
                print(f"Date: {trans[3]}")
        finally:
            conn.close()

def handle_point_redemption(user_id, rewards):
    current_points = rewards.get_user_points(user_id)
    print(f"\nYou have {current_points} points available.")
    print("Points can be redeemed in multiples of 1000 (1000 points = $10 gift card)")
    
    if current_points < 1000:
        print("You need at least 1000 points to redeem rewards.")
        return

    while True:
        try:
            points_to_redeem = int(input("\nEnter points to redeem (multiple of 1000): "))
            if points_to_redeem % 1000 != 0:
                print("Points must be redeemed in multiples of 1000.")
                continue
            
            success, message = rewards.redeem_reward(user_id, points_to_redeem)
            print(message)
            break
        except ValueError:
            print("Please enter a valid number.")

