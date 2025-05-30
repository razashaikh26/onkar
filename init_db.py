import mysql.connector
from mysql.connector import Error
import os
import sys
import hashlib

def init_database():
    """Initialize the database with schema from schema.sql"""
    
    # Database connection parameters
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Razashaikh@12',  # Updated password
        'auth_plugin': 'mysql_native_password'
    }
    
    connection = None
    cursor = None
    
    try:
        # Connect to MySQL server
        print("Connecting to MySQL server...")
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # First, create the database if it doesn't exist
            print("Creating database if it doesn't exist...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS warehouse_management")
            
            # Switch to the database
            cursor.execute("USE warehouse_management")
            
            # Create tables
            print("Creating tables if they don't exist...")
            
            # Users table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                role ENUM('admin', 'user') NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Warehouse slots table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS warehouse_slots (
                id INT AUTO_INCREMENT PRIMARY KEY,
                slot_name VARCHAR(50) NOT NULL,
                location VARCHAR(100),
                capacity INT NOT NULL,
                is_full BOOLEAN DEFAULT FALSE,
                status VARCHAR(20) DEFAULT 'available'
            )
            """)
            
            # Slot requests table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS slot_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                slot_id INT NOT NULL,
                request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (slot_id) REFERENCES warehouse_slots(id)
            )
            """)
            
            # Check if admin user exists
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            admin_exists = cursor.fetchone()
            
            if not admin_exists:
                # Hash the admin password
                admin_password = 'admin123'
                hashed_password = hashlib.sha256(admin_password.encode()).hexdigest()
                
                # Insert admin user with hashed password
                print("Creating admin user...")
                cursor.execute("""
                INSERT INTO users (username, password, email, role) 
                VALUES (%s, %s, %s, %s)
                """, ('admin', hashed_password, 'admin@warehouse.com', 'admin'))
            else:
                print("Admin user already exists.")
                
                # Check if admin password is hashed
                cursor.execute("SELECT password FROM users WHERE username = 'admin'")
                admin_password = cursor.fetchone()[0]
                
                if admin_password == 'admin123':
                    # Update to hashed password
                    print("Updating admin password to hashed version...")
                    hashed_password = hashlib.sha256('admin123'.encode()).hexdigest()
                    cursor.execute("UPDATE users SET password = %s WHERE username = 'admin'", (hashed_password,))
            
            # Check if sample slots exist
            cursor.execute("SELECT COUNT(*) FROM warehouse_slots")
            slot_count = cursor.fetchone()[0]
            
            if slot_count == 0:
                # Insert sample slots
                print("Creating sample warehouse slots...")
                sample_slots = [
                    ('A1', 'Section A, Floor 1', 1000, False),
                    ('A2', 'Section A, Floor 1', 1000, False),
                    ('B1', 'Section B, Floor 1', 1500, False),
                    ('B2', 'Section B, Floor 1', 1500, False),
                    ('C1', 'Section C, Floor 2', 2000, False),
                    ('C2', 'Section C, Floor 2', 2000, False)
                ]
                
                for slot in sample_slots:
                    cursor.execute("""
                    INSERT INTO warehouse_slots (slot_name, location, capacity, is_full)
                    VALUES (%s, %s, %s, %s)
                    """, slot)
            else:
                print(f"Found {slot_count} existing warehouse slots.")
            
            connection.commit()
            print("Database initialized successfully!")
            
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("MySQL connection closed.")
    
    return True

if __name__ == "__main__":
    print("Initializing Warehouse Management Database")
    print("=========================================")
    
    if not init_database():
        sys.exit(1)
    
    print("\nDatabase setup complete!")
    print("You can now run the application with: python3 app.py") 