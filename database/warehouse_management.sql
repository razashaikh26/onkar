-- Warehouse Management System Database Schema
-- This file contains the complete database schema for the warehouse management system

-- Drop database if it exists (be careful with this in production)
DROP DATABASE IF EXISTS warehouse_management;

-- Create database
CREATE DATABASE warehouse_management;
USE warehouse_management;

-- Create users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create warehouse_slots table
CREATE TABLE warehouse_slots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slot_name VARCHAR(50) NOT NULL UNIQUE,
    location VARCHAR(100) NOT NULL,
    capacity INT NOT NULL DEFAULT 1,
    is_full BOOLEAN NOT NULL DEFAULT FALSE,
    status ENUM('available', 'occupied', 'maintenance') NOT NULL DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create slot_requests table
CREATE TABLE slot_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    slot_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    notes TEXT,
    status ENUM('pending', 'approved', 'rejected', 'cancelled') NOT NULL DEFAULT 'pending',
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (slot_id) REFERENCES warehouse_slots(id) ON DELETE CASCADE
);

-- Insert default admin user (username: onkar, password: onkar123)
-- Password is stored as SHA-256 hash
INSERT INTO users (username, password, email, role) VALUES 
('onkar', '399a6dd4d5753514ad747b64eb58c72a5a4e8962194a15ad6187d4c58a4c5637', 'admin@warehouse.com', 'admin');

-- Insert some sample warehouse slots
INSERT INTO warehouse_slots (slot_name, location, capacity, is_full, status) VALUES
('Slot-A1', 'Building A, Floor 1', 10, FALSE, 'available'),
('Slot-A2', 'Building A, Floor 1', 15, FALSE, 'available'),
('Slot-B1', 'Building B, Floor 1', 8, FALSE, 'available'),
('Slot-B2', 'Building B, Floor 2', 12, FALSE, 'available'),
('Slot-C1', 'Building C, Floor 1', 20, FALSE, 'available');

-- Create indexes for better performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_warehouse_slots_name ON warehouse_slots(slot_name);
CREATE INDEX idx_slot_requests_user_id ON slot_requests(user_id);
CREATE INDEX idx_slot_requests_slot_id ON slot_requests(slot_id);
CREATE INDEX idx_slot_requests_status ON slot_requests(status);

-- Create a view for available slots
CREATE VIEW available_slots AS
SELECT * FROM warehouse_slots
WHERE is_full = FALSE AND status = 'available';

-- Create a view for pending requests
CREATE VIEW pending_requests AS
SELECT sr.*, u.username, ws.slot_name
FROM slot_requests sr
JOIN users u ON sr.user_id = u.id
JOIN warehouse_slots ws ON sr.slot_id = ws.id
WHERE sr.status = 'pending'
ORDER BY sr.request_date DESC;

-- Create a trigger to update slot status when request is approved
DELIMITER //
CREATE TRIGGER update_slot_status_on_approve
AFTER UPDATE ON slot_requests
FOR EACH ROW
BEGIN
    IF NEW.status = 'approved' AND OLD.status != 'approved' THEN
        UPDATE warehouse_slots
        SET is_full = TRUE, status = 'occupied'
        WHERE id = NEW.slot_id;
    END IF;
END //
DELIMITER ;

-- Create a trigger to update slot status when request is cancelled or rejected
DELIMITER //
CREATE TRIGGER update_slot_status_on_cancel
AFTER UPDATE ON slot_requests
FOR EACH ROW
BEGIN
    IF (NEW.status = 'cancelled' OR NEW.status = 'rejected') AND OLD.status = 'approved' THEN
        UPDATE warehouse_slots
        SET is_full = FALSE, status = 'available'
        WHERE id = NEW.slot_id;
    END IF;
END //
DELIMITER ;

-- Create a stored procedure to get all slots with their request counts
DELIMITER //
CREATE PROCEDURE get_slots_with_request_counts()
BEGIN
    SELECT ws.*, 
           COUNT(sr.id) AS total_requests,
           SUM(CASE WHEN sr.status = 'pending' THEN 1 ELSE 0 END) AS pending_requests,
           SUM(CASE WHEN sr.status = 'approved' THEN 1 ELSE 0 END) AS approved_requests
    FROM warehouse_slots ws
    LEFT JOIN slot_requests sr ON ws.id = sr.slot_id
    GROUP BY ws.id;
END //
DELIMITER ;

-- Create a stored procedure to get user statistics
DELIMITER //
CREATE PROCEDURE get_user_stats(IN user_id INT)
BEGIN
    SELECT 
        COUNT(*) AS total_requests,
        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending_requests,
        SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) AS approved_requests,
        SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) AS rejected_requests,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_requests
    FROM slot_requests
    WHERE user_id = user_id;
END //
DELIMITER ;

-- Create a function to check if a slot is available
DELIMITER //
CREATE FUNCTION is_slot_available(slot_id INT) RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE slot_status VARCHAR(20);
    DECLARE slot_is_full BOOLEAN;
    
    SELECT status, is_full INTO slot_status, slot_is_full
    FROM warehouse_slots
    WHERE id = slot_id;
    
    RETURN (slot_status = 'available' AND slot_is_full = FALSE);
END //
DELIMITER ;

-- Create an event to clean up old cancelled requests (runs daily)
DELIMITER //
CREATE EVENT clean_old_cancelled_requests
ON SCHEDULE EVERY 1 DAY
DO
BEGIN
    DELETE FROM slot_requests
    WHERE status = 'cancelled' AND request_date < DATE_SUB(NOW(), INTERVAL 30 DAY);
END //
DELIMITER ;

-- Grant permissions (adjust as needed for your environment)
GRANT ALL PRIVILEGES ON warehouse_management.* TO 'root'@'localhost';
FLUSH PRIVILEGES; 