-- Create the 'notes' database (run this as a superuser, e.g., in psql)
-- CREATE DATABASE notes;

-- Connect to the 'notes' database before running the rest of this script
-- \c notes

-- Create the 'notes' table
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    content TEXT
);
