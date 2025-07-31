import React from 'react';
import NoteCard, { type Note } from './NoteCard';

interface NotesListProps {
  notes: Note[];
  onDelete: (id: number) => void;
  onEdit: (note: Note) => void;
  pinnedIds: number[];
  onTogglePin: (id: number) => void;
}

const NotesList: React.FC<NotesListProps> = ({ notes, onDelete, onEdit, pinnedIds, onTogglePin }) => {
  if (notes.length === 0) {
    return <p className="empty-state">No notes yet.</p>;
  }
  const pinned = notes.filter(n => pinnedIds.includes(n.id));
  const others = notes.filter(n => !pinnedIds.includes(n.id));
  return (
    <>
      {pinned.length > 0 && (
        <>
          <h4>Pinned</h4>
          <div className="notes-list">
            {pinned.map(note => (
              <NoteCard key={note.id} note={note} isPinned onDelete={onDelete} onEdit={onEdit} onTogglePin={onTogglePin} />
            ))}
          </div>
          <h4>Others</h4>
        </>
      )}
      <div className="notes-list">
        {others.map(note => (
          <NoteCard key={note.id} note={note} isPinned={false} onDelete={onDelete} onEdit={onEdit} onTogglePin={onTogglePin} />
        ))}
      </div>
    </>
  );
};

export default NotesList; 