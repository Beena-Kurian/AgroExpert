
import random
from db import create_connection
from datetime import datetime, timedelta


def generate_coupon_code():
    """Generate a unique coupon code."""
    characters = 'BCDFGHJKLMNPQRSTVWXYZ23456789'
    code_parts = [''.join(random.choices(characters, k=4)) for _ in range(3)]
    return '-'.join(code_parts)

def add_coupon(value, days_valid):
    """Generate and add a new gift card with validation."""
    MINIMUM_VALUE = 10  # Minimum gift card value
    MINIMUM_EXPIRY = 30  # Minimum expiration period in days
    DEFAULT_EXPIRY = 30  # Default expiration period if not specified

    # Validate the value
    if value < MINIMUM_VALUE or value % 10 != 0:
        print(f"Error: Value must be at least ${MINIMUM_VALUE} and a multiple of 10.")
        return

    # Validate the expiry period
    if days_valid < MINIMUM_EXPIRY:
        print(f"Error: Validity period must be at least {MINIMUM_EXPIRY} days.")
        return

    # Insert the coupon into the database
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            code = generate_coupon_code()
            expiration_date = datetime.now() + timedelta(days=days_valid)

            cursor.execute('''
                INSERT INTO coupons (code, value, expiration_date)
                VALUES (?, ?, ?)
            ''', (code, value, expiration_date))

            conn.commit()
            print(f"Coupon created: {code}, Value: ${value}, Expires: {expiration_date}")
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            conn.close()




def view_coupons():
    """List all coupons and deactivate expired ones."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # First, check if any coupon has expired and update its status
            cursor.execute('''
                UPDATE coupons
                SET is_active = 0
                WHERE expiration_date < ?
            ''', (datetime.now(),))  # Deactivate expired coupons
            conn.commit()

            # Now, fetch and display all coupons
            cursor.execute('SELECT id, code, value, expiration_date, is_active FROM coupons')
            coupons = cursor.fetchall()
            if not coupons:
                print("\nNo coupons available...!")
            else:
                print("=== Coupon List ===")
                for coupon in coupons:
                    print(f"ID: {coupon[0]}, Code: {coupon[1]}, Value: ${coupon[2]}, Expires: {coupon[3]}, Active: {bool(coupon[4])}")
                
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            conn.close()


def deactivate_coupon():
    """Deactivate a coupon after displaying all available coupons."""
    conn = create_connection()
    if conn:
        try:
            # Display the list of coupons
            
            cursor = conn.cursor()
            cursor.execute('SELECT id, code, value, expiration_date, is_active FROM coupons')
            coupons = cursor.fetchall()

            if not coupons:
                print("\nNo coupons available..!")
                return
            print("\n=== Available Coupons ===")
            for coupon in coupons:
                status = "Active" if coupon[4] else "Inactive"
                print(f"ID: {coupon[0]}, Code: {coupon[1]}, Value: ${coupon[2]}, Expires: {coupon[3]}, Status: {status}")

            # Prompt the user for the ID of the coupon to deactivate
            coupon_id = input("\nEnter the ID of the coupon to deactivate: ")

            # Check if the ID is valid
            cursor.execute('SELECT id FROM coupons WHERE id = ? AND is_active = 1', (coupon_id,))
            if cursor.fetchone() is None:
                print(f"Error: Coupon ID {coupon_id} does not exist or is already inactive.")
                return

            # Deactivate the coupon
            cursor.execute('UPDATE coupons SET is_active = 0 WHERE id = ?', (coupon_id,))
            conn.commit()
            print(f"Coupon ID {coupon_id} has been deactivated.")
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            conn.close()


def add_multiple_coupons(value, days_valid, count):
    """Generate and add multiple gift cards."""
    conn = create_connection()
    expiration_date = datetime.now() + timedelta(days=days_valid)
    coupons = []

    for _ in range(count):
        code = generate_coupon_code()
        coupons.append((code, value, expiration_date))

    conn.executemany('''
        INSERT INTO coupons (code, value, expiration_date)
        VALUES (?, ?, ?)
    ''', coupons)

    conn.commit()
    conn.close()

    print(f"{count} gift cards of value ${value} created. All expire on {expiration_date}.")

# def generate_gift_cards():
#     """Generate a unique gift card code."""
#     characters = 'BCDFGHJKLMNPQRSTVWXYZ23456789'
#     code_parts = [''.join(random.choices(characters, k=4)) for _ in range(3)]
#     return '-'.join(code_parts)

# def add_coupon(value, days_valid):
#     """Generate and add a new coupon."""
#     conn = create_connection()
#     if conn:
#         try:
#             cursor = conn.cursor()
#             code = generate_gift_cards()
#             expiration_date = datetime.now() + timedelta(days=days_valid)

#             cursor.execute('''
#                 INSERT INTO coupons (code, value, expiration_date)
#                 VALUES (?, ?, ?)
#             ''', (code, value, expiration_date))

#             conn.commit()
#             print(f"Coupon created: {code}, Value: ${value}, Expires: {expiration_date}")
#         except Exception as e:
#             print(f"Database error: {e}")
#         finally:
#             conn.close()

# def view_coupons():
#     """List all coupons."""
#     conn = create_connection()
#     if conn:
#         try:
#             cursor = conn.cursor()
#             cursor.execute('SELECT id, code, value, expiration_date, is_active FROM coupons')
#             coupons = cursor.fetchall()

#             print("=== Coupon List ===")
#             for coupon in coupons:
#                 print(f"ID: {coupon[0]}, Code: {coupon[1]}, Value: ${coupon[2]}, Expires: {coupon[3]}, Active: {bool(coupon[4])}")
#         except Exception as e:
#             print(f"Database error: {e}")
#         finally:
#             conn.close()

# def deactivate_coupon(coupon_id):
#     """Deactivate a coupon."""
#     conn = create_connection()
#     if conn:
#         try:
#             cursor = conn.cursor()
#             cursor.execute('UPDATE coupons SET is_active = 0 WHERE id = ?', (coupon_id,))
#             conn.commit()
#             print(f"Coupon ID {coupon_id} deactivated.")
#         except Exception as e:
#             print(f"Database error: {e}")
#         finally:
#             conn.close()
# def add_multiple_coupons(value, days_valid, count):
#     """Generate and add multiple gift cards."""
#     conn = create_connection()
    
#     expiration_date = datetime.now() + timedelta(days=days_valid)
#     coupons = []

#     for _ in range(count):
#         code = generate_gift_cards()
#         coupons.append((code, value, expiration_date))

#     conn.executemany('''
#         INSERT INTO coupons (code, value, expiration_date)
#         VALUES (?, ?, ?)
#     ''', coupons)

#     conn.commit()
#     conn.close()

#     print(f"{count} gift cards of value ${value} created. All expire on {expiration_date}.")

# def redeem_coupon(user_id, code):
#     """Redeem a coupon for a user."""
#     conn = create_connection()
#     # conn.execute('PRAGMA journal_mode=WAL')
#     if conn:
#         try:
#             cursor = conn.cursor()
#             # Check if the coupon is valid
#             cursor.execute('''
#                 SELECT id, value, is_active, expiration_date
#                 FROM coupons
#                 WHERE code = ?
#             ''', (code,))
#             coupon = cursor.fetchone()

#             if not coupon:
#                 print("Invalid coupon code.")
#                 return
#             elif not coupon[2]:
#                 print("Coupon is inactive.")
#                 return
#             elif datetime.strptime(coupon[3], '%Y-%m-%d %H:%M:%S.%f') < datetime.now():
#                 print("Coupon has expired.")
#                 return

#             # Mark coupon as redeemed
#             coupon_id = coupon[0]
#             cursor.execute('''
#                 INSERT INTO coupon_usage (coupon_id, user_id, redemption_date)
#                 VALUES (?, ?, ?)
#             ''', (coupon_id, user_id, datetime.now()))

#             # Deactivate the coupon
#             cursor.execute('UPDATE coupons SET is_active = 0 WHERE id = ?', (coupon_id,))
#             conn.commit()

#             # print(f"Coupon {code} redeemed successfully for User ID {user_id}, Value: ${coupon[1]}")
#         except Exception as e:
#             print(f"Database error: {e}")
#         finally:
#             conn.close()
def redeem_coupon(user_id, code):
    """Redeem a coupon for a user."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Check if the coupon is valid
            cursor.execute('''
                SELECT id, value, is_active, expiration_date
                FROM coupons
                WHERE code = ?
            ''', (code,))
            coupon = cursor.fetchone()

            if not coupon:
                print("Invalid coupon code.")
                return
            elif not coupon[2]:
                print("Coupon is inactive.")
                return
            elif datetime.strptime(coupon[3], '%Y-%m-%d %H:%M:%S.%f') < datetime.now():
                print("Coupon has expired.")
                return

            # Mark coupon as redeemed
            coupon_id = coupon[0]
            redemption_time = datetime.now()

            # Insert into coupon_usage table
            cursor.execute('''
                INSERT INTO coupon_usage (coupon_id, user_id, redemption_date)
                VALUES (?, ?, ?)
            ''', (coupon_id, user_id, redemption_time))

            # Deactivate the coupon
            cursor.execute('UPDATE coupons SET is_active = 0 WHERE id = ?', (coupon_id,))

            conn.commit()  # Commit transaction

            # Provide feedback on successful redemption
            print(f"Coupon {code} redeemed successfully for User ID {user_id}. Value: ${coupon[1]}")

        except Exception as e:
            print(f"Database error: {e}")
            conn.rollback()  # Rollback in case of an error
        finally:
            conn.close()
