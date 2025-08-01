-- Initialize PostgreSQL database for Notes Microservices Application

-- Create folders table
CREATE TABLE IF NOT EXISTS folders (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(20),
    icon VARCHAR(10) DEFAULT '📁',
    parent_id INTEGER REFERENCES folders(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create notes table
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    tags VARCHAR(500), -- JSON string or comma-separated
    color VARCHAR(20) DEFAULT '#6366f1',
    folder_id INTEGER REFERENCES folders(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_notes_folder_id ON notes(folder_id);
CREATE INDEX IF NOT EXISTS idx_notes_title ON notes(title);
CREATE INDEX IF NOT EXISTS idx_folders_parent_id ON folders(parent_id);
CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at);
CREATE INDEX IF NOT EXISTS idx_folders_created_at ON folders(created_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
DROP TRIGGER IF EXISTS update_folders_updated_at ON folders;
CREATE TRIGGER update_folders_updated_at
    BEFORE UPDATE ON folders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_notes_updated_at ON notes;
CREATE TRIGGER update_notes_updated_at
    BEFORE UPDATE ON notes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data
INSERT INTO folders (name, color, icon) VALUES 
    ('Work', '#6366f1', '💼'),
    ('Personal', '#ec4899', '🏠'),
    ('Projects', '#10b981', '🚀')
ON CONFLICT DO NOTHING;

INSERT INTO notes (title, content, tags, color, folder_id) VALUES 
    ('Welcome to Notes App', 'This is your first note! You can use <strong>rich text formatting</strong> and organize notes in folders.', '["welcome", "getting-started"]', '#6366f1', 1),
    ('Meeting Notes', 'Key points from today''s meeting:<br/>• Review project timeline<br/>• Discuss budget allocation<br/>• Plan next quarter', '["meeting", "work"]', '#ec4899', 1),
    ('Personal Todo', 'Things to do this weekend:<br/>• Grocery shopping<br/>• Clean the house<br/>• Call family', '["personal", "todo"]', '#10b981', 2)
ON CONFLICT DO NOTHING; 