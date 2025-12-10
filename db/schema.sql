-- Drop existing database if exists 
DROP DATABASE IF EXISTS delivery_box;
CREATE DATABASE delivery_box;
USE delivery_box;

-- Drop tables if they exist 
DROP TABLE IF EXISTS parcels;
DROP TABLE IF EXISTS boxes;
DROP TABLE IF EXISTS users;

-- Table for users
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

-- Table for delivery boxes
CREATE TABLE boxes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    box_name VARCHAR(100) NOT NULL, 
    location VARCHAR(255) NULL      
);

-- Table for parcels
CREATE TABLE parcels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    box_id INT NOT NULL,
    parcel_name VARCHAR(255) NOT NULL,
    is_delivered BOOLEAN DEFAULT FALSE,
    delivered_at TIMESTAMP NULL,
    collected_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (box_id) REFERENCES boxes(id) ON DELETE CASCADE
);
