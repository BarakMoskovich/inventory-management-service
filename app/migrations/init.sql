-- Create database if not exists
SELECT 'CREATE DATABASE inventory'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'inventory')\gexec

-- Connect to the inventory database
\c inventory

-- Create schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS inventory;

-- Create table in the new schema
CREATE TABLE IF NOT EXISTS inventory.items (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT
);

-- Insert dump data
INSERT INTO inventory.items (name, description) VALUES
    ('Laptop', 'High-performance laptop'),
    ('Tablet', 'Professional tablet with stylus'),
    ('Smartphone', 'Latest model smartphone');
