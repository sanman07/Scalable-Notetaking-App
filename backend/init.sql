-- Initialize PostgreSQL database for Notes Application with Authentication

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Create folders table with user ownership
CREATE TABLE IF NOT EXISTS folders (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(20),
    icon VARCHAR(10) DEFAULT '📁',
    parent_id INTEGER REFERENCES folders(id) ON DELETE SET NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create notes table with user ownership
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    tags TEXT[], -- PostgreSQL array type for tags
    color VARCHAR(20) DEFAULT '#6366f1',
    folder_id INTEGER REFERENCES folders(id) ON DELETE SET NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);
CREATE INDEX IF NOT EXISTS idx_notes_folder_id ON notes(folder_id);
CREATE INDEX IF NOT EXISTS idx_notes_title ON notes(title);
CREATE INDEX IF NOT EXISTS idx_folders_user_id ON folders(user_id);
CREATE INDEX IF NOT EXISTS idx_folders_parent_id ON folders(parent_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_notes_updated_at BEFORE UPDATE ON notes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_folders_updated_at BEFORE UPDATE ON folders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin123)
-- In production, this should be created through the API
INSERT INTO users (username, email, hashed_password, full_name) VALUES 
    ('admin', 'admin@notesapp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK6.', 'Administrator')
ON CONFLICT DO NOTHING;

-- Insert sample data for admin user
INSERT INTO folders (name, color, icon, user_id) VALUES 
    ('Work', '#6366f1', '💼', 1),
    ('Personal', '#ec4899', '🏠', 1),
    ('Projects', '#10b981', '🚀', 1)
ON CONFLICT DO NOTHING;

INSERT INTO notes (title, content, tags, color, folder_id, user_id) VALUES 
    ('Welcome to Notes App', 'This is your first note! You can use <strong>rich text formatting</strong> and organize notes in folders.', ARRAY['welcome', 'getting-started'], '#6366f1', 1, 1),
    ('Meeting Notes', 'Key points from today''s meeting:<br/>• Review project timeline<br/>• Discuss budget allocation<br/>• Plan next quarter', ARRAY['meeting', 'work'], '#ec4899', 1, 1)
ON CONFLICT DO NOTHING; 