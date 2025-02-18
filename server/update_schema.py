import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from zkp.password_zkp import PasswordZKP

def update_database_schema(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Add ZKP column if not exists
        cursor.execute('''
        ALTER TABLE AUTH ADD COLUMN zkp_public_key TEXT DEFAULT NULL;
        ''')

        # Set up ZKP for admin account
        zkp = PasswordZKP()
        admin_password = "admin"  # Default admin password
        _, public_key = zkp.generate_keypair(admin_password)

        # Update admin account with ZKP public key
        cursor.execute('''
        UPDATE AUTH
        SET zkp_public_key = ?
        WHERE account_num = 0;
        ''', (str(public_key),))

        conn.commit()
        conn.close()
        print(f"Successfully updated schema for {db_path}")
        return True
    except sqlite3.Error as e:
        if 'duplicate column' not in str(e):
            print(f"Error updating {db_path}: {e}")
        return False

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_paths = [
        os.path.join(current_dir, 'database1.db'),
        os.path.join(current_dir, 'database2.db')
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            update_database_schema(db_path)
        else:
            print(f"Database not found: {db_path}")

if __name__ == "__main__":
    main()
