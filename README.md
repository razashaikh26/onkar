# Warehouse Management System

A web-based warehouse management system built with Python Flask and MySQL. This system allows users to request warehouse slots and administrators to manage slots and approve requests.

## Features

- **User Side**:
  - Request warehouse slots
  - View request status
  - Track slot availability

- **Admin Side**:
  - Manage warehouse slots (add, update status)
  - Approve or reject user requests
  - View slot utilization statistics

## Prerequisites

- Python 3.6+
- MySQL Server
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd warehouse_management
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Configure MySQL:
   - Create a MySQL database
   - Update the database connection settings in `database/db_connection.py`
   - Import the schema from `database/schema.sql`

   ```sql
   mysql -u your_username -p < database/schema.sql
   ```

## Running the Application

1. Start the Flask application:
   ```
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Default Admin Credentials

- Username: admin
- Password: admin123

## Project Structure

```
warehouse_management/
├── app.py                  # Main Flask application
├── database/               # Database related files
│   ├── db_connection.py    # Database connection module
│   ├── models.py           # Data models
│   └── schema.sql          # Database schema
├── static/                 # Static files
│   ├── css/                # CSS files
│   │   └── style.css       # Custom styles
│   ├── js/                 # JavaScript files
│   │   └── script.js       # Custom scripts
│   └── images/             # Image files
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── index.html          # Homepage
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── user_dashboard.html # User dashboard
│   ├── admin_dashboard.html # Admin dashboard
│   └── ...                 # Other templates
└── requirements.txt        # Project dependencies
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 