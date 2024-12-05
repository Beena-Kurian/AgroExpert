
# rewards.py
from db import create_connection
from gift_card import redeem_coupon
from datetime import datetime

class RewardSystem:
    def __init__(self):
        # Point structure for farmers
        self.farmer_points = {
            'consultation_image': 10,  # High-quality image upload for consultation
            'new_disease_images': 500  # 50 images of new disease
            # 'forum_post': 5,  # Points for each post
            # 'forum_comment': 1  # Points for each comment
        }
        
        # Point structure for experts
        self.expert_points = {
            'consultation_completed': 20,  # For each consultation
            'fast_response': 5  # Bonus for < 24h response
            # 'high_rating': 10,  # Bonus for 4-5 star rating
            # 'article': 30,  # Published article
            # 'forum_post': 20,  # Added post
            # 'forum_reply': 5  # Replies to farmers posts
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

    # def add_points(self, user_id, points):
    #     try:
    #         conn = create_connection()
    #         cursor = conn.cursor()
    #         # Use UPSERT for atomic insert/update operation
    #         cursor.execute('''
    #             INSERT INTO rewards (user_id, points) 
    #             VALUES (?, ?)
    #             ON CONFLICT(user_id) DO UPDATE SET points = points + excluded.points;
    #         ''', (user_id, points))
    #         conn.commit()
    #         return True
    #     except Exception as e:
    #         print(f"Unexpected error: {e}")
    #         return False
    #     finally:
    #         if conn:
    #             conn.close()
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

    # def add_points(self, user_id, points):
    #     conn = create_connection()
    #     if conn:
    #         try:
    #             cursor = conn.cursor()
    #             # First try to update existing record
    #             cursor.execute('''
    #                 INSERT OR REPLACE INTO rewards (user_id, points) 
    #                 VALUES (?, COALESCE((SELECT points + ? FROM rewards WHERE user_id = ?), ?))
    #             ''', (user_id, points, user_id, points))
    #             conn.commit()
    #             return True
    #         except Exception as e:
    #             print(f"Error adding points: {e}")
    #             return False
    #         finally:
    #             conn.close()
    #     return False


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
    # def award_consultation_image(self, farmer_id):
    #     points = self.farmer_points['consultation_image']
    #     if self.add_points(farmer_id, points):
    #         self.log_reward_transaction(
    #             farmer_id, 
    #             'consultation_image', 
    #             points, 
    #             'Points awarded for high-quality consultation image'
    #         )
    #         return True
    #     return False

    def award_new_disease_images(self, farmer_id, image_count):
        if image_count >= 50:
            points = self.farmer_points['new_disease_images']
            if self.add_points(farmer_id, points):
                self.log_reward_transaction(
                    farmer_id,
                    'new_disease_images',
                    points,
                    f'Points awarded for submitting {image_count} images of new disease'
                )
                return True
        return False

    # def award_forum_activity(self, farmer_id, activity_type):
    #     points = self.farmer_points[activity_type]
    #     if self.add_points(farmer_id, points):
    #         self.log_reward_transaction(
    #             farmer_id,
    #             activity_type,
    #             points,
    #             f'Points awarded for forum {activity_type}'
    #         )
    #         return True
    #     return False

    # def redeem_reward(self, farmer_id, points_to_redeem):
    #     if points_to_redeem % 1000 != 0:
    #         return False, "Points must be redeemed in multiples of 1000"
        
    #     # Calculate the reward amount
    #     reward_amount = (points_to_redeem / 1000) * 10  # $10 for every 1000 points
        
    #     # Check if there are available gift cards
    #     conn = create_connection()
    #     cursor = conn.cursor()
    #     # if conn:
    #     #     conn.execute('PRAGMA journal_mode=WAL')
    #     cursor.execute('''
    #         SELECT id, code 
    #         FROM coupons
    #         WHERE value = ? AND is_active = 1
    #         LIMIT 1
    #     ''', (reward_amount,))
    #     gift_card = cursor.fetchone()

    #     if not gift_card:
    #         conn.close()
    #         return False, f"No available gift cards for ${reward_amount}. Check after few days..!"

    #     gift_card_id, gift_card_code = gift_card

    #     # Proceed with points deduction if a gift card is available
    #     if self.deduct_points(farmer_id, points_to_redeem):
    #         try:
    #             # Mark gift card as redeemed and assign to farmer
    #             cursor.execute('''
    #                 INSERT INTO coupon_usage (coupon_id, user_id, redemption_date)
    #                 VALUES (?, ?, ?)
    #             ''', (gift_card_id, farmer_id, datetime.now()))
    #             cursor.execute('''
    #                 UPDATE coupons
    #                 SET is_active = 0
    #                 WHERE id = ?
    #             ''', (gift_card_id,))

    #             # Log the reward transaction
    #             self.log_reward_transaction(
    #                 farmer_id,
    #                 'redemption',
    #                 -points_to_redeem,
    #                 f'Redeemed points for gift card {gift_card_code}'
    #             )

    #             conn.commit()
    #             conn.close()
    #             return True, f"Successfully redeemed {points_to_redeem} points for gift card {gift_card_code} (${reward_amount})."
    #         except Exception as e:
    #             conn.rollback()
    #             conn.close()
    #             return False, f"An error occurred during redemption: {str(e)}"
    #         finally:
    #             conn.close()
    #     else:
    #         conn.close()
    #         return False, "Insufficient points"
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
                SELECT id, code 
                FROM coupons
                WHERE value = ? AND is_active = 1
                LIMIT 1
            ''', (reward_amount,))
            gift_card = cursor.fetchone()

            if not gift_card:
                return False, f"No available gift cards for ${reward_amount}. Check back later."

            gift_card_id, gift_card_code = gift_card

            # Deduct points from farmer's account
            if not self.deduct_points(farmer_id, points_to_redeem):
                return False, "Insufficient points to redeem."

            # Mark the gift card as redeemed and assign to the farmer
            cursor.execute('''
                INSERT INTO coupon_usage (coupon_id, user_id, redemption_date)
                VALUES (?, ?, ?)
            ''', (gift_card_id, farmer_id, datetime.now()))

            cursor.execute('''
                UPDATE coupons
                SET is_active = 0
                WHERE id = ?
            ''', (gift_card_id,))

            # Log the reward transaction
            self.log_reward_transaction(
                farmer_id,
                'redemption',
                -points_to_redeem,
                f'Redeemed points for gift card {gift_card_code}'
            )
            conn.commit()
            
            return True, f"Successfully redeemed {points_to_redeem} points for gift card {gift_card_code} (${reward_amount})."

        except Exception as e:
            conn.rollback()
            return False, f"An error occurred during redemption: {str(e)}"
        
        finally:
            conn.close()

class ExpertRewards(RewardSystem):
    # def award_consultation_completion(self, expert_id, response_time=None):
    #     points = self.expert_points['consultation_completed']
        
    #     # Add fast response bonus if applicable
    #     if response_time and response_time <= 24:  # response time in hours
    #         points += self.expert_points['fast_response']
        
    #     if self.add_points(expert_id, points):
    #         self.log_reward_transaction(
    #             expert_id,
    #             'consultation_completed',
    #             points,
    #             'Points awarded for completing consultation'
    #         )
    #         return True
    #     return False

    # def award_high_rating(self, expert_id):
    #     points = self.expert_points['high_rating']
    #     if self.add_points(expert_id, points):
    #         self.log_reward_transaction(
    #             expert_id,
    #             'high_rating',
    #             points,
    #             'Bonus points for high rating'
    #         )
    #         return True
    #     return False

    # def award_content_contribution(self, expert_id, contribution_type):
    #     points = self.expert_points[contribution_type]
    #     if self.add_points(expert_id, points):
    #         self.log_reward_transaction(
    #             expert_id,
    #             contribution_type,
    #             points,
    #             f'Points awarded for {contribution_type}'
    #         )
    #         return True
    #     return False

    def redeem_reward(self, expert_id, points_to_redeem):
        if points_to_redeem % 1000 != 0:
            return False, "Points must be redeemed in multiples of 1000"
        
        if self.deduct_points(expert_id, points_to_redeem):
            reward_amount = (points_to_redeem / 1000) * 10  # $10 for every 1000 points
            self.log_reward_transaction(
                expert_id,
                'redemption',
                -points_to_redeem,
                f'Redeemed points for ${reward_amount} gift card'
            )
            return True, f"Successfully redeemed {points_to_redeem} points for ${reward_amount} gift card"
        return False, "Insufficient points"

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

