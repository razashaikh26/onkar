-- Database Schema for Warehouse Management System

-- Create database
CREATE DATABASE IF NOT EXISTS warehouse_management;
USE warehouse_management;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    role ENUM('admin', 'user') NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Warehouse slots table
CREATE TABLE IF NOT EXISTS warehouse_slots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slot_name VARCHAR(50) NOT NULL,
    location VARCHAR(100),
    capacity INT NOT NULL,
    is_full BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'available' -- available, reserved, occupied
);

-- Slot requests table
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
);

-- Insert admin user
INSERT INTO users (username, password, email, role) 
VALUES ('admin', 'admin123', 'admin@warehouse.com', 'admin');

-- Insert some sample slots
INSERT INTO warehouse_slots (slot_name, location, capacity, is_full) VALUES
('A1', 'Section A, Floor 1', 1000, FALSE),
('A2', 'Section A, Floor 1', 1000, FALSE),
('B1', 'Section B, Floor 1', 1500, FALSE),
('B2', 'Section B, Floor 1', 1500, FALSE),
('C1', 'Section C, Floor 2', 2000, FALSE),
('C2', 'Section C, Floor 2', 2000, FALSE); 