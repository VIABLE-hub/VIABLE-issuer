#!/usr/bin/env python3
"""
Create Veritas Admin User
This script creates an admin user for the Veritas tenant directly in the database
"""
import sqlite3
import os
from datetime import datetime

def create_veritas_admin():
    """Create a Veritas admin user directly in the database"""
    
    # Admin credentials
    username = "admin@veritas.edu"
    password = "VeritasAdmin2024!"
    
    # Database path for Veritas tenant
    db_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'src', 
        'tenants', 
        'instances', 
        'veritas', 
        'database.db'
    )
    db_path = os.path.abspath(db_path)
    
    # Generate password hash (werkzeug's generate_password_hash equivalent)
    from werkzeug.security import generate_password_hash
    hashed_password = generate_password_hash(password)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(150),
                password_hash VARCHAR(150),
                creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if user already exists
        cursor.execute("SELECT * FROM user WHERE name = ?", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"✅ User '{username}' already exists!")
            print(f"\n{'='*60}")
            print(f"  VERITAS ADMIN CREDENTIALS")
            print(f"{'='*60}")
            print(f"  Tenant:   Veritas University")
            print(f"  URL:      http://localhost:5005/veritas")
            print(f"  Username: {username}")
            print(f"  Password: {password}")
            print(f"{'='*60}")
            print(f"\n⚠️  If you need to reset the password, delete the user first.")
            conn.close()
            return
        
        # Create new admin user
        print(f"🔧 Creating Veritas admin user...")
        creation_date = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO user (name, password_hash, creation_date)
            VALUES (?, ?, ?)
        """, (username, hashed_password, creation_date))
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Veritas Admin User Created Successfully!")
        print(f"\n{'='*60}")
        print(f"  VERITAS ADMIN CREDENTIALS")
        print(f"{'='*60}")
        print(f"  Tenant:   Veritas University")
        print(f"  URL:      http://localhost:5005/veritas")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print(f"{'='*60}")
        print(f"  Database: {db_path}")
        print(f"{'='*60}")
        print(f"\n📝 Keep these credentials secure!")
        print(f"🌐 Access the login page at: http://localhost:5005/veritas/login")
        print(f"\n💡 You can also create additional users via the registration page")
        print(f"   (if DEBUG mode is enabled)")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_veritas_admin()

