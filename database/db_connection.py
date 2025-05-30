import mysql.connector
from mysql.connector import Error
import os

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'Razashaikh@12',  # Updated password
            'database': 'warehouse_management'
        }
    
    def connect(self):
        try:
            # Close any existing connection first
            self.disconnect()
                
            self.connection = mysql.connector.connect(
                **self.config,
                autocommit=True,  # Enable autocommit
                consume_results=True  # Automatically consume unread results
            )
            if self.connection.is_connected():
                print("Database connection established successfully")
                return True
            else:
                print("Failed to establish database connection")
                return False
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
        
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            try:
                # Consume any unread results
                cursor = self.connection.cursor()
                while self.connection.unread_result:
                    cursor.fetchall()
                cursor.close()
                
                # Close the connection
                self.connection.close()
                print("Database connection closed")
            except Error as e:
                print(f"Error disconnecting from MySQL: {e}")
    
    def execute_query(self, query, params=None):
        cursor = None
        try:
            # If connection doesn't exist or is not connected, try to connect
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    print("Failed to establish database connection in execute_query")
                    return None
            
            # Consume any unread results
            self._consume_unread_results()
            
            # Print query for debugging
            print(f"Executing query: {query}")
            if params:
                print(f"With parameters: {params}")
                
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            return cursor
        except Error as e:
            print(f"Error executing query: {e}")
            # Try to reconnect once if the connection was lost
            if "MySQL Connection not available" in str(e) or "Not connected" in str(e) or "Unread result" in str(e):
                print("Connection issue detected, attempting to reconnect...")
                if self.connect():
                    print("Reconnected successfully, retrying query...")
                    return self.execute_query(query, params)
            return None
        except Exception as e:
            print(f"Unexpected error in execute_query: {e}")
            return None
    
    def _consume_unread_results(self):
        """Helper method to consume any unread results"""
        try:
            if self.connection and self.connection.is_connected() and hasattr(self.connection, 'unread_result') and self.connection.unread_result:
                print("Consuming unread results...")
                temp_cursor = self.connection.cursor()
                temp_cursor.fetchall()
                temp_cursor.close()
        except Error as e:
            print(f"Error consuming unread results: {e}")
    
    def fetch_all(self, query, params=None):
        cursor = self.execute_query(query, params)
        if cursor:
            try:
                result = cursor.fetchall()
                cursor.close()
                return result
            except Error as e:
                print(f"Error fetching results: {e}")
                cursor.close()
        return []
    
    def fetch_one(self, query, params=None):
        cursor = self.execute_query(query, params)
        if cursor:
            try:
                result = cursor.fetchone()
                # Fetch any remaining rows to avoid unread result errors
                if cursor.with_rows and cursor.fetchall():
                    pass  # Just consume the results
                cursor.close()
                return result
            except Error as e:
                print(f"Error fetching result: {e}")
                cursor.close()
        return None
    
    def insert(self, query, params=None):
        cursor = self.execute_query(query, params)
        if cursor:
            try:
                last_id = cursor.lastrowid
                # Fetch any remaining rows to avoid unread result errors
                if cursor.with_rows and cursor.fetchall():
                    pass  # Just consume the results
                cursor.close()
                return last_id
            except Error as e:
                print(f"Error getting lastrowid: {e}")
                cursor.close()
        return None
    
    def update(self, query, params=None):
        cursor = self.execute_query(query, params)
        if cursor:
            try:
                affected_rows = cursor.rowcount
                # Fetch any remaining rows to avoid unread result errors
                if cursor.with_rows and cursor.fetchall():
                    pass  # Just consume the results
                cursor.close()
                return affected_rows
            except Error as e:
                print(f"Error getting rowcount: {e}")
                cursor.close()
        return 0

# Singleton instance
db = DatabaseConnection() 