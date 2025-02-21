-- Create database
CREATE DATABASE IF NOT EXISTS urban_gardening;
USE urban_gardening;

-- Users table
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Gardeners table
CREATE TABLE gardeners (
    gardener_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    specialization VARCHAR(100),
    years_experience INT,
    hourly_rate DECIMAL(10,2),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Services table
CREATE TABLE services (
    service_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    base_price DECIMAL(10,2)
);

-- Bookings table
CREATE TABLE bookings (
    booking_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    gardener_id INT,
    service_id INT,
    booking_date DATE,
    booking_time TIME,
    status VARCHAR(20),
    total_price DECIMAL(10,2),
    address TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (gardener_id) REFERENCES gardeners(gardener_id),
    FOREIGN KEY (service_id) REFERENCES services(service_id)
);

-- Products table
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    stock_quantity INT,
    category VARCHAR(50)
);

-- Orders table
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2),
    status VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Order items table
CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    product_id INT,
    quantity INT,
    price_per_unit DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Plant diagnosis table
CREATE TABLE plant_diagnoses (
    diagnosis_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    image_url VARCHAR(255),
    disease_name VARCHAR(100),
    confidence_score DECIMAL(5,2),
    diagnosis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Insert dummy data
INSERT INTO users (username, email, password_hash, first_name, last_name) VALUES
('john_doe', 'john@example.com', 'hashed_password_1', 'John', 'Doe'),
('jane_smith', 'jane@example.com', 'hashed_password_2', 'Jane', 'Smith'),
('bob_wilson', 'bob@example.com', 'hashed_password_3', 'Bob', 'Wilson');

INSERT INTO gardeners (user_id, specialization, years_experience, hourly_rate) VALUES
(1, 'Landscape Design', 5, 45.00),
(2, 'Organic Gardening', 3, 35.00),
(3, 'Urban Farming', 7, 50.00);

INSERT INTO services (name, description, base_price) VALUES
('Garden Maintenance', 'Regular maintenance and upkeep of gardens', 75.00),
('Planting Service', 'Professional planting of new gardens', 100.00),
('Garden Design', 'Custom garden design and planning', 150.00),
('Consultation', 'Expert gardening advice and consultation', 50.00);

INSERT INTO products (name, description, price, stock_quantity, category) VALUES
('Garden Trowel', 'High-quality steel garden trowel', 15.99, 50, 'Tools'),
('Organic Soil', '20L bag of premium organic soil', 24.99, 100, 'Soil'),
('Tomato Seeds', 'Heirloom tomato seed packet', 4.99, 200, 'Seeds'),
('Watering Can', '2-gallon plastic watering can', 19.99, 75, 'Tools');

INSERT INTO bookings (user_id, gardener_id, service_id, booking_date, booking_time, status, total_price, address) VALUES
(1, 2, 1, '2024-03-15', '10:00:00', 'Confirmed', 75.00, '123 Garden St, City'),
(2, 1, 3, '2024-03-16', '14:00:00', 'Pending', 150.00, '456 Park Ave, Town'),
(3, 3, 2, '2024-03-17', '09:00:00', 'Confirmed', 100.00, '789 Green Rd, Village');

INSERT INTO orders (user_id, total_amount, status) VALUES
(1, 44.97, 'Completed'),
(2, 15.99, 'Processing'),
(3, 29.98, 'Completed');

INSERT INTO order_items (order_id, product_id, quantity, price_per_unit) VALUES
(1, 1, 1, 15.99),
(1, 3, 2, 4.99),
(2, 1, 1, 15.99),
(3, 2, 1, 24.99);

INSERT INTO plant_diagnoses (user_id, image_url, disease_name, confidence_score) VALUES
(1, 'plant1.jpg', 'Apple Scab', 0.92),
(2, 'plant2.jpg', 'Powdery Mildew', 0.88),
(3, 'plant3.jpg', 'Healthy', 0.95);
 