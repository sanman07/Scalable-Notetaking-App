import React from 'react';
import ReactMarkdown from 'react-markdown';

export interface Note {
  id: number;
  title: string;
  content: string;
  tags?: string[];
  color?: string;
  folder_id?: number;
  createdAt?: string;
  updatedAt?: string;
}

interface NoteCardProps {
  note: Note;
  onDelete: (id: number) => void;
  onEdit: (note: Note) => void;
  isPinned?: boolean;
  onTogglePin?: (id: number) => void;
}

const NoteCard: React.FC<NoteCardProps> = ({ note, onDelete, onEdit, isPinned, onTogglePin }) => {
  const handleCardClick = () => {
    onEdit(note);
  };

  const handleActionClick = (e: React.MouseEvent, action: () => void) => {
    e.stopPropagation(); // Prevent card click when clicking action buttons
    action();
  };

  return (
    <div 
      className="note-card" 
      style={{borderLeft:`6px solid ${note.color||'transparent'}`}}
      onClick={handleCardClick}
    >
      <div className="note-header">
        <div style={{display:'flex',alignItems:'center',gap:4}}>
          {note.color && <span className="color-dot" style={{background: note.color}} />}
          <h3>{note.title}</h3>
        </div>
        <div className="note-actions">
          <button 
            onClick={(e) => handleActionClick(e, () => onTogglePin?.(note.id))} 
            className="pin-btn" 
            title="Pin"
          >
            {isPinned ? '📌' : '📍'}
          </button>
          <button 
            onClick={(e) => handleActionClick(e, () => onEdit(note))} 
            className="edit-btn"
          >
            Edit
          </button>
          <button 
            onClick={(e) => handleActionClick(e, () => onDelete(note.id))} 
            className="delete-btn"
          >
            Delete
          </button>
        </div>
      </div>
      <div className="note-content">
        <ReactMarkdown>{note.content}</ReactMarkdown>
      </div>
      {note.tags && note.tags.length > 0 && (
        <div className="tags-row">
          {note.tags.map(t => (<span key={t} className="tag-chip">{t}</span>))}
        </div>
      )}
      {note.createdAt && <small>Created: {new Date(note.createdAt).toLocaleString()}</small>}
      {note.updatedAt && <small> | Updated: {new Date(note.updatedAt).toLocaleString()}</small>}
    </div>
  );
};

export default NoteCard; 