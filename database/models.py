from .db_connection import db
import hashlib

class User:
    @staticmethod
    def create(username, password, email, role='user'):
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        query = """
        INSERT INTO users (username, password, email, role)
        VALUES (%s, %s, %s, %s)
        """
        params = (username, hashed_password, email, role)
        return db.insert(query, params)
    
    @staticmethod
    def get_by_id(user_id):
        query = "SELECT * FROM users WHERE id = %s"
        return db.fetch_one(query, (user_id,))
    
    @staticmethod
    def get_by_username(username):
        query = "SELECT * FROM users WHERE username = %s"
        return db.fetch_one(query, (username,))
    
    @staticmethod
    def get_by_email(email):
        query = "SELECT * FROM users WHERE email = %s"
        return db.fetch_one(query, (email,))
    
    @staticmethod
    def authenticate(username, password):
        # Hardcoded admin credentials
        if username == 'onkar' and password == 'onkar123':
            # Return a dummy admin user
            return {
                'id': 1,
                'username': 'admin',
                'role': 'admin',
                'email': 'admin@warehouse.com'
            }
            
        # For regular users, check the database
        query = "SELECT * FROM users WHERE username = %s"
        user = db.fetch_one(query, (username,))
        
        if not user:
            return None
            
        # Hash the provided password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Check if the password matches the hashed version
        if user['password'] == hashed_password:
            return user
            
        return None
    
    @staticmethod
    def get_all_users():
        query = "SELECT id, username, email, role, created_at FROM users"
        return db.fetch_all(query)
    
    @staticmethod
    def update_email(user_id, email):
        query = "UPDATE users SET email = %s WHERE id = %s"
        return db.update(query, (email, user_id))
    
    @staticmethod
    def update_password(user_id, password):
        # Hash the new password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        query = "UPDATE users SET password = %s WHERE id = %s"
        return db.update(query, (hashed_password, user_id))
    
    @staticmethod
    def verify_password(user_id, password):
        # Get the user
        user = User.get_by_id(user_id)
        if not user:
            return False
        
        # Hash the provided password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Check if the password matches the hashed version
        return user['password'] == hashed_password
    
    @staticmethod
    def update_role(user_id, role):
        query = "UPDATE users SET role = %s WHERE id = %s"
        return db.update(query, (role, user_id))


class WarehouseSlot:
    @staticmethod
    def create(slot_name, location, capacity):
        try:
            print(f"Creating slot: {slot_name}, {location}, {capacity}")
            
            # First check if a slot with the same name already exists
            check_query = "SELECT id FROM warehouse_slots WHERE slot_name = %s"
            existing_slot = db.fetch_one(check_query, (slot_name,))
            
            if existing_slot:
                print(f"Slot with name '{slot_name}' already exists with ID: {existing_slot['id']}")
                return None
            
            # Create the new slot
            query = """
            INSERT INTO warehouse_slots (slot_name, location, capacity, is_full, status)
            VALUES (%s, %s, %s, %s, %s)
            """
            params = (slot_name, location, int(capacity), False, 'available')
            
            # Make sure we have a fresh connection
            if not db.connection or not db.connection.is_connected():
                db.connect()
                
            slot_id = db.insert(query, params)
            
            if slot_id:
                print(f"Successfully created slot with ID: {slot_id}")
                return slot_id
            else:
                print("Failed to create slot: No ID returned")
                return None
        except Exception as e:
            print(f"Error creating slot: {e}")
            return None
    
    @staticmethod
    def get_by_id(slot_id):
        query = "SELECT * FROM warehouse_slots WHERE id = %s"
        return db.fetch_one(query, (slot_id,))
    
    @staticmethod
    def get_all_slots():
        query = "SELECT * FROM warehouse_slots"
        return db.fetch_all(query)
    
    @staticmethod
    def get_available_slots():
        query = "SELECT * FROM warehouse_slots WHERE is_full = FALSE"
        return db.fetch_all(query)
    
    @staticmethod
    def update_status(slot_id, is_full, status='available'):
        try:
            query = """
            UPDATE warehouse_slots 
            SET is_full = %s, status = %s
            WHERE id = %s
            """
            params = (is_full, status, slot_id)
            result = db.update(query, params)
            print(f"Updated slot {slot_id} status: {result} rows affected")
            return result
        except Exception as e:
            print(f"Error updating slot status: {e}")
            return 0
    
    @staticmethod
    def update_capacity(slot_id, capacity):
        try:
            # Validate capacity
            if int(capacity) <= 0:
                print("Capacity must be a positive number")
                return 0
                
            query = """
            UPDATE warehouse_slots 
            SET capacity = %s
            WHERE id = %s
            """
            params = (int(capacity), slot_id)
            result = db.update(query, params)
            print(f"Updated slot {slot_id} capacity to {capacity}: {result} rows affected")
            return result
        except Exception as e:
            print(f"Error updating slot capacity: {e}")
            return 0
    
    @staticmethod
    def increase_capacity(slot_id, amount=1):
        try:
            # Get current capacity
            slot = WarehouseSlot.get_by_id(slot_id)
            if not slot:
                print(f"Slot with ID {slot_id} not found")
                return 0
                
            # Calculate new capacity
            new_capacity = slot['capacity'] + int(amount)
            
            # Update capacity
            return WarehouseSlot.update_capacity(slot_id, new_capacity)
        except Exception as e:
            print(f"Error increasing slot capacity: {e}")
            return 0
    
    @staticmethod
    def decrease_capacity(slot_id, amount=1):
        try:
            # Get current capacity
            slot = WarehouseSlot.get_by_id(slot_id)
            if not slot:
                print(f"Slot with ID {slot_id} not found")
                return 0
                
            # Calculate new capacity
            new_capacity = slot['capacity'] - int(amount)
            
            # Ensure capacity doesn't go below 1
            if new_capacity < 1:
                print(f"Cannot decrease capacity below 1")
                return 0
                
            # Update capacity
            return WarehouseSlot.update_capacity(slot_id, new_capacity)
        except Exception as e:
            print(f"Error decreasing slot capacity: {e}")
            return 0
    
    @staticmethod
    def delete(slot_id):
        query = "DELETE FROM warehouse_slots WHERE id = %s"
        return db.update(query, (slot_id,))


class SlotRequest:
    @staticmethod
    def create(user_id, slot_id, start_date, end_date, notes=None):
        query = """
        INSERT INTO slot_requests (user_id, slot_id, start_date, end_date, notes)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (user_id, slot_id, start_date, end_date, notes)
        return db.insert(query, params)
    
    @staticmethod
    def get_by_id(request_id):
        query = "SELECT * FROM slot_requests WHERE id = %s"
        return db.fetch_one(query, (request_id,))
    
    @staticmethod
    def get_by_user(user_id):
        query = """
        SELECT sr.*, ws.slot_name, ws.location
        FROM slot_requests sr
        JOIN warehouse_slots ws ON sr.slot_id = ws.id
        WHERE sr.user_id = %s
        ORDER BY sr.request_date DESC
        """
        return db.fetch_all(query, (user_id,))
    
    @staticmethod
    def get_all_requests():
        query = """
        SELECT sr.*, u.username, ws.slot_name
        FROM slot_requests sr
        JOIN users u ON sr.user_id = u.id
        JOIN warehouse_slots ws ON sr.slot_id = ws.id
        ORDER BY sr.request_date DESC
        """
        return db.fetch_all(query)
    
    @staticmethod
    def get_pending_requests():
        query = """
        SELECT sr.*, u.username, ws.slot_name
        FROM slot_requests sr
        JOIN users u ON sr.user_id = u.id
        JOIN warehouse_slots ws ON sr.slot_id = ws.id
        WHERE sr.status = 'pending'
        ORDER BY sr.request_date DESC
        """
        return db.fetch_all(query)
    
    @staticmethod
    def update_status(request_id, status):
        query = """
        UPDATE slot_requests
        SET status = %s
        WHERE id = %s
        """
        params = (status, request_id)
        return db.update(query, params)
    
    @staticmethod
    def has_requests_for_slot(slot_id):
        query = "SELECT COUNT(*) as count FROM slot_requests WHERE slot_id = %s"
        result = db.fetch_one(query, (slot_id,))
        return result and result['count'] > 0 