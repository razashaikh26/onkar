#cd warehouse_management && python3 app.py

from flask import Flask, render_template, request, redirect, url_for, flash, session
from database.models import User, WarehouseSlot, SlotRequest
from database.db_connection import db
from datetime import datetime
import os
import sys

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize database connection
if not db.connect():
    print("WARNING: Could not connect to the database with default credentials.")
    print("Please check the following:")
    print("1. Make sure MySQL server is running")
    print("2. Verify the database 'warehouse_management' exists")
    print("3. Check your MySQL username and password")
    print("4. Run python check_db.py for diagnostic information")
    
    # Set environment variables for credentials
    os.environ['MYSQL_USER'] = input("MySQL username (default: root): ") or 'root'
    os.environ['MYSQL_PASSWORD'] = input("MySQL password: ")
    
    # Try connecting again
    if not db.connect():
        print("ERROR: Still unable to connect to the database. Exiting.")
        sys.exit(1)

# Ensure database connection is closed when the application exits
@app.teardown_appcontext
def close_db_connection(exception):
    db.disconnect()

# Login required decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Admin required decorator
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        
        # Check if user is admin directly from session
        if session.get('role') != 'admin':
            flash('You do not have permission to access this page', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            # Ensure database connection
            if not db.connection or not db.connection.is_connected():
                db.connect()
                
            user = User.authenticate(username, password)
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                flash(f'Welcome back, {username}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'error')
            print(f"Error during login: {str(e)}")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            email = request.form.get('email')
            
            # Validate input
            if not username or not password or not confirm_password or not email:
                flash('All fields are required', 'error')
                return render_template('register.html')
            
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return render_template('register.html')
            
            # Check if username or email already exists
            existing_user = User.get_by_username(username)
            if existing_user:
                flash('Username already exists', 'error')
                return render_template('register.html')
            
            existing_email = User.get_by_email(email)
            if existing_email:
                flash('Email already exists', 'error')
                return render_template('register.html')
            
            # Ensure database connection is fresh
            db.disconnect()
            db.connect()
            
            user_id = User.create(username, password, email)
            if user_id:
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Registration failed', 'error')
        except Exception as e:
            flash(f'Error during registration: {str(e)}', 'error')
            print(f"Exception in register: {e}")
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Use session role directly instead of fetching user again
    if session.get('role') == 'admin':
        pending_requests = SlotRequest.get_pending_requests()
        all_slots = WarehouseSlot.get_all_slots()
        return render_template('admin_dashboard.html', 
                              pending_requests=pending_requests,
                              all_slots=all_slots)
    else:
        user_id = session['user_id']
        user_requests = SlotRequest.get_by_user(user_id)
        available_slots = WarehouseSlot.get_available_slots()
        return render_template('user_dashboard.html', 
                              user_requests=user_requests,
                              available_slots=available_slots)

@app.route('/profile')
@login_required
def profile():
    user_id = session['user_id']
    user = User.get_by_id(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Don't pass password to template
    if 'password' in user:
        del user['password']
    
    return render_template('profile.html', user=user)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    try:
        user_id = session['user_id']
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Get current user
        user = User.get_by_id(user_id)
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('profile'))
        
        # Update email if provided
        if email and email != user['email']:
            # Check if email already exists
            existing_email = User.get_by_email(email)
            if existing_email and existing_email['id'] != user_id:
                flash('Email already exists', 'error')
                return redirect(url_for('profile'))
            
            User.update_email(user_id, email)
            flash('Email updated successfully', 'success')
        
        # Update password if provided
        if current_password and new_password and confirm_password:
            # Verify current password
            if not User.verify_password(user_id, current_password):
                flash('Current password is incorrect', 'error')
                return redirect(url_for('profile'))
            
            # Check if new passwords match
            if new_password != confirm_password:
                flash('New passwords do not match', 'error')
                return redirect(url_for('profile'))
            
            # Update password
            User.update_password(user_id, new_password)
            flash('Password updated successfully', 'success')
        
        return redirect(url_for('profile'))
    except Exception as e:
        flash(f'Error updating profile: {str(e)}', 'error')
        print(f"Exception in update_profile: {e}")
        return redirect(url_for('profile'))

# User routes
@app.route('/request_slot', methods=['GET', 'POST'])
@login_required
def request_slot():
    if request.method == 'POST':
        try:
            slot_id = request.form.get('slot_id')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            notes = request.form.get('notes')
            
            # Validate input
            if not slot_id or not start_date or not end_date:
                flash('Slot, start date, and end date are required', 'error')
                available_slots = WarehouseSlot.get_available_slots()
                return render_template('request_slot.html', available_slots=available_slots)
            
            # Ensure database connection is fresh
            db.disconnect()
            db.connect()
            
            request_id = SlotRequest.create(session['user_id'], slot_id, start_date, end_date, notes)
            if request_id:
                flash('Slot request submitted successfully', 'success')
                return redirect(url_for('my_requests'))
            else:
                flash('Failed to submit slot request', 'error')
        except Exception as e:
            flash(f'Error requesting slot: {str(e)}', 'error')
            print(f"Exception in request_slot: {e}")
    
    available_slots = WarehouseSlot.get_available_slots()
    return render_template('request_slot.html', available_slots=available_slots)

@app.route('/my_requests')
@login_required
def my_requests():
    user_requests = SlotRequest.get_by_user(session['user_id'])
    return render_template('my_requests.html', user_requests=user_requests)

@app.route('/cancel_request/<int:request_id>', methods=['POST'])
@login_required
def cancel_request(request_id):
    try:
        # Get the request
        slot_request = SlotRequest.get_by_id(request_id)
        if not slot_request:
            flash('Request not found', 'error')
            return redirect(url_for('my_requests'))
        
        # Check if the request belongs to the user
        if slot_request['user_id'] != session['user_id']:
            flash('You do not have permission to cancel this request', 'error')
            return redirect(url_for('my_requests'))
        
        # Check if the request is pending (can only cancel pending requests)
        if slot_request['status'] != 'pending':
            flash('Can only cancel pending requests', 'error')
            return redirect(url_for('my_requests'))
        
        # Cancel the request
        result = SlotRequest.update_status(request_id, 'cancelled')
        if result:
            flash('Request cancelled successfully', 'success')
        else:
            flash('Failed to cancel request', 'error')
    except Exception as e:
        flash(f'Error cancelling request: {str(e)}', 'error')
        print(f"Exception in cancel_request: {e}")
    
    return redirect(url_for('my_requests'))

# Admin routes
@app.route('/admin/slots')
@admin_required
def admin_slots():
    all_slots = WarehouseSlot.get_all_slots()
    return render_template('admin_slots.html', slots=all_slots)

@app.route('/admin/add_slot', methods=['GET', 'POST'])
@admin_required
def add_slot():
    if request.method == 'POST':
        try:
            slot_name = request.form.get('slot_name')
            location = request.form.get('location')
            capacity = request.form.get('capacity')
            
            # Validate input
            if not slot_name or not location or not capacity:
                flash('All fields are required', 'error')
                return render_template('add_slot.html')
            
            # Convert capacity to integer
            try:
                capacity = int(capacity)
                if capacity <= 0:
                    flash('Capacity must be a positive number', 'error')
                    return render_template('add_slot.html')
            except ValueError:
                flash('Capacity must be a valid number', 'error')
                return render_template('add_slot.html')
            
            # Ensure database connection is fresh
            db.disconnect()
            db.connect()
            
            slot_id = WarehouseSlot.create(slot_name, location, capacity)
            if slot_id:
                flash('Slot added successfully', 'success')
                return redirect(url_for('admin_slots'))
            else:
                flash('Failed to add slot. Please check the server logs.', 'error')
        except Exception as e:
            flash(f'Error adding slot: {str(e)}', 'error')
            print(f"Exception in add_slot: {e}")
    
    return render_template('add_slot.html')

@app.route('/admin/update_slot/<int:slot_id>', methods=['POST'])
@admin_required
def update_slot(slot_id):
    is_full = request.form.get('is_full') == 'true'
    status = request.form.get('status')
    
    result = WarehouseSlot.update_status(slot_id, is_full, status)
    if result:
        flash('Slot updated successfully', 'success')
    else:
        flash('Failed to update slot', 'error')
    
    return redirect(url_for('admin_slots'))

@app.route('/admin/update_capacity/<int:slot_id>', methods=['POST'])
@admin_required
def update_capacity(slot_id):
    try:
        capacity = request.form.get('capacity')
        
        # Validate capacity
        try:
            capacity = int(capacity)
            if capacity <= 0:
                flash('Capacity must be a positive number', 'error')
                return redirect(url_for('admin_slots'))
        except ValueError:
            flash('Capacity must be a valid number', 'error')
            return redirect(url_for('admin_slots'))
        
        # Update capacity
        result = WarehouseSlot.update_capacity(slot_id, capacity)
        if result:
            flash('Slot capacity updated successfully', 'success')
        else:
            flash('Failed to update slot capacity', 'error')
    except Exception as e:
        flash(f'Error updating slot capacity: {str(e)}', 'error')
        print(f"Exception in update_capacity: {e}")
    
    return redirect(url_for('admin_slots'))

@app.route('/admin/increase_capacity/<int:slot_id>', methods=['POST'])
@admin_required
def increase_capacity(slot_id):
    try:
        amount = request.form.get('amount', 1)
        
        # Validate amount
        try:
            amount = int(amount)
            if amount <= 0:
                flash('Amount must be a positive number', 'error')
                return redirect(url_for('admin_slots'))
        except ValueError:
            flash('Amount must be a valid number', 'error')
            return redirect(url_for('admin_slots'))
        
        # Increase capacity
        result = WarehouseSlot.increase_capacity(slot_id, amount)
        if result:
            flash(f'Slot capacity increased by {amount}', 'success')
        else:
            flash('Failed to increase slot capacity', 'error')
    except Exception as e:
        flash(f'Error increasing slot capacity: {str(e)}', 'error')
        print(f"Exception in increase_capacity: {e}")
    
    return redirect(url_for('admin_slots'))

@app.route('/admin/decrease_capacity/<int:slot_id>', methods=['POST'])
@admin_required
def decrease_capacity(slot_id):
    try:
        amount = request.form.get('amount', 1)
        
        # Validate amount
        try:
            amount = int(amount)
            if amount <= 0:
                flash('Amount must be a positive number', 'error')
                return redirect(url_for('admin_slots'))
        except ValueError:
            flash('Amount must be a valid number', 'error')
            return redirect(url_for('admin_slots'))
        
        # Decrease capacity
        result = WarehouseSlot.decrease_capacity(slot_id, amount)
        if result:
            flash(f'Slot capacity decreased by {amount}', 'success')
        else:
            flash('Failed to decrease slot capacity or would result in capacity less than 1', 'error')
    except Exception as e:
        flash(f'Error decreasing slot capacity: {str(e)}', 'error')
        print(f"Exception in decrease_capacity: {e}")
    
    return redirect(url_for('admin_slots'))

@app.route('/admin/delete_slot/<int:slot_id>', methods=['POST'])
@admin_required
def delete_slot(slot_id):
    try:
        # Check if there are any requests for this slot
        if SlotRequest.has_requests_for_slot(slot_id):
            flash('Cannot delete slot with existing requests', 'error')
            return redirect(url_for('admin_slots'))
        
        result = WarehouseSlot.delete(slot_id)
        if result:
            flash('Slot deleted successfully', 'success')
        else:
            flash('Failed to delete slot', 'error')
    except Exception as e:
        flash(f'Error deleting slot: {str(e)}', 'error')
        print(f"Exception in delete_slot: {e}")
    
    return redirect(url_for('admin_slots'))

@app.route('/admin/requests')
@admin_required
def admin_requests():
    all_requests = SlotRequest.get_all_requests()
    return render_template('admin_requests.html', requests=all_requests)

@app.route('/admin/update_request/<int:request_id>', methods=['POST'])
@admin_required
def update_request(request_id):
    try:
        status = request.form.get('status')
        
        result = SlotRequest.update_status(request_id, status)
        if result:
            # If approved, update the slot status
            if status == 'approved':
                slot_request = SlotRequest.get_by_id(request_id)
                if slot_request:
                    WarehouseSlot.update_status(slot_request['slot_id'], True, 'occupied')
            
            flash('Request updated successfully', 'success')
        else:
            flash('Failed to update request', 'error')
    except Exception as e:
        flash(f'Error updating request: {str(e)}', 'error')
        print(f"Exception in update_request: {e}")
    
    return redirect(url_for('admin_requests'))

@app.route('/admin/users')
@admin_required
def admin_users():
    all_users = User.get_all_users()
    return render_template('admin_users.html', users=all_users)

@app.route('/admin/toggle_user_role/<int:user_id>', methods=['POST'])
@admin_required
def toggle_user_role(user_id):
    try:
        # Don't allow changing own role
        if user_id == session['user_id']:
            flash('Cannot change your own role', 'error')
            return redirect(url_for('admin_users'))
        
        user = User.get_by_id(user_id)
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('admin_users'))
        
        new_role = 'admin' if user['role'] == 'user' else 'user'
        result = User.update_role(user_id, new_role)
        if result:
            flash(f"User role updated to {new_role}", 'success')
        else:
            flash('Failed to update user role', 'error')
    except Exception as e:
        flash(f'Error updating user role: {str(e)}', 'error')
        print(f"Exception in toggle_user_role: {e}")
    
    return redirect(url_for('admin_users'))

if __name__ == '__main__':
    # Database connection was already initialized at the top
    app.run(debug=True)