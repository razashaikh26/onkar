import mysql.connector
from mysql.connector import Error
import sys

def check_mysql_connection():
    """Check if MySQL server is running and if the database exists"""
    
    # First, try to connect to MySQL server without specifying a database
    base_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Razashaikh@12',  # Set your MySQL password here
    }
    
    try:
        print("Testing connection to MySQL server...")
        connection = mysql.connector.connect(**base_config)
        
        if connection.is_connected():
            print("✅ MySQL server is running and accessible.")
            
            # Now check if the database exists
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES LIKE 'warehouse_management'")
            result = cursor.fetchone()
            
            if result:
                print("✅ 'warehouse_management' database exists.")
                
                # Try to connect directly to the database
                db_config = base_config.copy()
                db_config['database'] = 'warehouse_management'
                
                try:
                    db_connection = mysql.connector.connect(**db_config)
                    if db_connection.is_connected():
                        print("✅ Successfully connected to 'warehouse_management' database.")
                        
                        # Check if tables exist
                        db_cursor = db_connection.cursor()
                        db_cursor.execute("SHOW TABLES")
                        tables = db_cursor.fetchall()
                        
                        if tables:
                            print(f"✅ Database contains {len(tables)} tables:")
                            for table in tables:
                                print(f"  - {table[0]}")
                        else:
                            print("❌ No tables found in the database. Run init_db.py to create tables.")
                        
                        db_cursor.close()
                    db_connection.close()
                except Error as e:
                    print(f"❌ Error connecting to 'warehouse_management' database: {e}")
            else:
                print("❌ 'warehouse_management' database does not exist.")
                print("   Run the following SQL command to create it:")
                print("   CREATE DATABASE warehouse_management;")
                print("   Then run init_db.py to initialize the database schema.")
            
            cursor.close()
        connection.close()
        
    except Error as e:
        print(f"❌ Error connecting to MySQL server: {e}")
        if "Access denied" in str(e):
            print("   Check your MySQL username and password in db_connection.py")
        elif "Can't connect" in str(e):
            print("   Make sure MySQL server is running.")
        return False
    
    return True

if __name__ == "__main__":
    print("MySQL Database Connection Check")
    print("==============================")
    if not check_mysql_connection():
        sys.exit(1) 