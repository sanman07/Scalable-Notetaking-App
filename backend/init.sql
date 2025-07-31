-- Initialize PostgreSQL database for Notes Application

-- Create folders table
CREATE TABLE IF NOT EXISTS folders (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(20),
    icon VARCHAR(10) DEFAULT '📁',
    parent_id INTEGER REFERENCES folders(id) ON DELETE SET NULL
);

-- Create notes table
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    tags TEXT[], -- PostgreSQL array type for tags
    color VARCHAR(20) DEFAULT '#6366f1',
    folder_id INTEGER REFERENCES folders(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_notes_folder_id ON notes(folder_id);
CREATE INDEX IF NOT EXISTS idx_notes_title ON notes(title);
CREATE INDEX IF NOT EXISTS idx_folders_parent_id ON folders(parent_id);

-- Insert some sample data
INSERT INTO folders (name, color, icon) VALUES 
    ('Work', '#6366f1', '💼'),
    ('Personal', '#ec4899', '🏠'),
    ('Projects', '#10b981', '🚀')
ON CONFLICT DO NOTHING;

INSERT INTO notes (title, content, tags, color, folder_id) VALUES 
    ('Welcome to Notes App', 'This is your first note! You can use <strong>rich text formatting</strong> and organize notes in folders.', ARRAY['welcome', 'getting-started'], '#6366f1', 1),
    ('Meeting Notes', 'Key points from today''s meeting:<br/>• Review project timeline<br/>• Discuss budget allocation<br/>• Plan next quarter', ARRAY['meeting', 'work'], '#ec4899', 1)
ON CONFLICT DO NOTHING; 