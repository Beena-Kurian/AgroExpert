# news_updates.py
from db import create_connection

class NewsUpdates:
    def display_news_for_user(self):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT title, content, created_at FROM news ORDER BY created_at DESC LIMIT 10')
                news_items = cursor.fetchall()
                
                if not news_items:
                    print("\nNo news items available.")
                    return
                
                print("\n=== Latest News ===")
                for item in news_items:
                    print(f"\nTitle: {item[0]}")
                    print(f"Content: {item[1]}")
                    print(f"Date: {item[2]}")
                    print("-" * 50)
            finally:
                conn.close()

    def display_news_management_menu(self):
        while True:
            print("\n=== News Management ===")
            print("1. Add News Item")
            print("2. View All News")
            print("3. Delete News Item")
            print("4. Back to Admin Menu")
            
            choice = input("Enter your choice (1-4): ")
            
            if choice == '1':
                self.add_news_item()
            elif choice == '2':
                self.display_news_for_user()
            elif choice == '3':
                self.delete_news_item()
            elif choice == '4':
                break
            else:
                print("Invalid choice! Please try again.")

    def add_news_item(self):
        print("\n=== Add News Item ===")
        title = input("Enter news title: ")
        content = input("Enter news content: ")
        
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO news (title, content) VALUES (?, ?)', (title, content))
                conn.commit()
                print("News item added successfully!")
            finally:
                conn.close()

    def delete_news_item(self):
        print("\n=== Delete News Item ===")
        self.display_news_for_user()
        news_id = input("Enter news ID to delete: ")
        
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM news WHERE id = ?', (news_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    print("News item deleted successfully!")
                else:
                    print("News item not found.")
            finally:
                conn.close()