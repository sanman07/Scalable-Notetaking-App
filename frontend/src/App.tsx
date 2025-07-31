import { useEffect, useState } from 'react';
import NoteForm from './components/NoteForm';
import SearchBar from './components/SearchBar';
import Toast from './components/Toast';
import ConfirmDialog from './components/ConfirmDialog';
import type { Note } from './components/NoteCard';
import './App.css';
import React from 'react';
import {
  DndContext,
  DragOverlay,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import { useDraggable, useDroppable } from '@dnd-kit/core';
import type { DragEndEvent, DragStartEvent } from '@dnd-kit/core';

interface Folder {
  id: number;
  name: string;
  color: string;
  icon?: string;
  parent_id?: number;
}

// Type for folder with children
interface HierarchicalFolder extends Folder {
  children: HierarchicalFolder[];
}

// Folder Edit Form Component
const FolderEditForm: React.FC<{
  folder: Folder;
  onSave: (folderId: number, name: string, color: string, icon: string) => void;
  onCancel: () => void;
}> = ({ folder, onSave, onCancel }) => {
  const [name, setName] = useState(folder.name);
  const [color] = useState(folder.color || '#6366f1');
  const [icon, setIcon] = useState(folder.icon || '📁');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) {
      onSave(folder.id, name.trim(), color, icon);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="folder-edit-form">
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        className="folder-edit-name-input"
        autoFocus
      />
      
      <div className="folder-edit-controls">
        <div className="folder-edit-icon-picker">
          <label>Icon:</label>
          <div className="icon-picker-mini">
            {FOLDER_ICONS.slice(0, 15).map(folderIcon => (
              <button
                key={folderIcon}
                type="button"
                className={`icon-picker-btn-mini ${icon === folderIcon ? 'selected' : ''}`}
                onClick={() => setIcon(folderIcon)}
              >
                <IconDisplay icon={folderIcon} />
              </button>
            ))}
          </div>
        </div>
        
        <div className="folder-edit-actions">
          <button type="submit" className="save-btn">Save</button>
          <button type="button" onClick={onCancel} className="cancel-btn">Cancel</button>
        </div>
      </div>
    </form>
  );
};

// Available folder icons - basic symbols for universal compatibility
const FOLDER_ICONS = [
  '📁', '📂', '*', '+', '-', '=', '#', '@', '%', '&',
  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
  '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'
];

// Icon Display Component - simplified approach
const IconDisplay: React.FC<{ icon: string; className?: string }> = ({ icon, className = '' }) => {
  return (
    <span 
      className={`icon-display ${className}`}
      style={{ 
        fontFamily: "'Apple Color Emoji', 'Segoe UI Emoji', 'Noto Color Emoji', 'Segoe UI Symbol', 'Android Emoji', 'EmojiSymbols', sans-serif",
        fontSize: 'inherit',
        lineHeight: '1',
        display: 'inline-block',
        fontVariantEmoji: 'emoji'
      }}
      role="img"
      aria-label={`Folder icon: ${icon}`}
    >
      {icon}
    </span>
  );
};

// Component to render rich text summary safely
const RichTextSummary: React.FC<{ content: string; maxLength?: number }> = ({ content, maxLength = 120 }) => {
  // Process rich text content and create a clean summary
  const processContent = (text: string) => {
    const lines = text.split('\n');
    let processedContent = '';
    
    for (const line of lines) {
      let processedLine = line.trim();
      
      // Process different line types
      if (processedLine.startsWith('• ')) {
        // Bullet list items
        processedLine = processedLine.substring(2);
      } else if (processedLine.match(/^\d+\. /)) {
        // Numbered list items
        processedLine = processedLine.replace(/^\d+\. /, '');
      } else if (processedLine.startsWith('# ')) {
        // Heading 1
        processedLine = processedLine.substring(2);
      } else if (processedLine.startsWith('## ')) {
        // Heading 2  
        processedLine = processedLine.substring(3);
      } else if (processedLine.startsWith('### ')) {
        // Heading 3
        processedLine = processedLine.substring(4);
      }
      
      if (processedLine) {
        processedContent += (processedContent ? ' ' : '') + processedLine;
      }
    }
    
    return processedContent;
  };

  const cleanText = processContent(content);
  const shouldTruncate = cleanText.length > maxLength;

  return (
    <span>
      {content.split('\n').map((line, index) => {
        const trimmedLine = line.trim();
        if (!trimmedLine) return null;
        
        // Apply styling based on line type while keeping it inline
        if (trimmedLine.startsWith('• ')) {
          return <span key={index}><strong>•</strong> {trimmedLine.substring(2)} </span>;
        } else if (trimmedLine.match(/^\d+\. /)) {
          return <span key={index}><strong>{trimmedLine.match(/^\d+\./)?.[0]}</strong> {trimmedLine.replace(/^\d+\. /, '')} </span>;
        } else if (trimmedLine.startsWith('# ')) {
          return <strong key={index}>{trimmedLine.substring(2)} </strong>;
        } else if (trimmedLine.startsWith('## ')) {
          return <strong key={index}>{trimmedLine.substring(3)} </strong>;
        } else if (trimmedLine.startsWith('### ')) {
          return <strong key={index}>{trimmedLine.substring(4)} </strong>;
        } else {
          return <span key={index}>{trimmedLine} </span>;
        }
      }).filter(Boolean).slice(0, Math.ceil(maxLength / 20))}
      {shouldTruncate && '...'}
    </span>
  );
};

// Draggable Note Component
const DraggableNote: React.FC<{
  note: Note;
  onEdit: (note: Note) => void;
  onTogglePin: (id: number) => void;
  onDelete: (id: number) => void;
  isPinned: boolean;
}> = ({ note, onEdit, onTogglePin, onDelete, isPinned }) => {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: note.id.toString(),
  });

  const style = transform ? {
    transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
    opacity: isDragging ? 0.5 : 1,
  } : undefined;

  return (
    <div
      ref={setNodeRef}
      {...listeners}
      {...attributes}
      className="tree-note-card"
      onClick={() => onEdit(note)}
      style={{
        borderLeft: `3px solid ${note.color || '#6366f1'}`,
        ...style,
      }}
    >
      <div className="note-header">
        <h5>{note.title}</h5>
        <div className="note-actions">
          <button onClick={(e) => {e.stopPropagation(); onTogglePin(note.id);}} className="pin-btn" title="Pin">
            {isPinned ? '📌' : '📍'}
          </button>
          <button onClick={(e) => {e.stopPropagation(); onDelete(note.id);}} className="delete-btn">×</button>
        </div>
      </div>
      
      {/* Content summary */}
      {note.content && note.content.trim() && (
        <p className="note-summary">
          <RichTextSummary content={note.content} maxLength={120} />
        </p>
      )}
      
      {/* Tags */}
      {note.tags && note.tags.length > 0 && (
        <div className="note-tags">
          {note.tags.slice(0, 3).map(tag => (
            <span key={tag} className="tag-chip">{tag}</span>
          ))}
          {note.tags.length > 3 && <span className="tag-chip more">+{note.tags.length - 3}</span>}
        </div>
      )}
    </div>
  );
};

// Droppable Hierarchical Folder Section Component
const HierarchicalFolderSection: React.FC<{
  folder: HierarchicalFolder;
  notes: Note[];
  isExpanded: boolean;
  onToggle: () => void;
  onEditNote: (note: Note) => void;
  onTogglePin: (id: number) => void;
  onDeleteNote: (id: number) => void;
  pinnedIds: number[];
  onEditFolder: (folder: Folder) => void;
  onDeleteFolder: (folderId: number) => void;
  onCreateSubfolder: (parentId: number) => void;
  expandedFolders: number[];
  onToggleFolder: (folderId: number) => void;
  depth?: number;
}> = ({ 
  folder, 
  notes, 
  isExpanded, 
  onToggle, 
  onEditNote, 
  onTogglePin, 
  onDeleteNote, 
  pinnedIds, 
  onEditFolder, 
  onDeleteFolder,
  onCreateSubfolder,
  expandedFolders,
  onToggleFolder,
  depth = 0 
}) => {
  const { isOver, setNodeRef } = useDroppable({
    id: `folder-${folder.id}`,
  });

  const folderNotes = notes.filter(n => n.folder_id === folder.id);

  return (
    <div className="folder-section" style={{ marginLeft: `${depth * 1.5}rem` }}>
      <div 
        ref={setNodeRef}
        className={`folder-header ${isOver ? 'drag-over' : ''}`}
        style={{borderLeft: `3px solid ${folder.color || '#6366f1'}`}}
      >
        <div className="folder-main" onClick={onToggle}>
          <span className="folder-toggle">
            <IconDisplay icon={isExpanded ? (folder.icon || '📂') : (folder.icon || '📁')} />
          </span>
          <span className="folder-name">{folder.name} ({folderNotes.length})</span>
        </div>
        <div className="folder-actions">
          <button 
            onClick={(e) => {e.stopPropagation(); onCreateSubfolder(folder.id);}} 
            className="folder-add-sub-btn" 
            title="Add Subfolder"
          >
            📂+
          </button>
          <button 
            onClick={(e) => {e.stopPropagation(); onEditFolder(folder);}} 
            className="folder-edit-btn" 
            title="Edit Folder"
          >
            ✏️
          </button>
          <button 
            onClick={(e) => {e.stopPropagation(); onDeleteFolder(folder.id);}} 
            className="folder-delete-btn" 
            title="Delete Folder"
          >
            🗑️
          </button>
        </div>
      </div>
      
      {isExpanded && (
        <div>
          {/* Subfolders */}
          {folder.children.map(subfolder => (
            <HierarchicalFolderSection
              key={subfolder.id}
              folder={subfolder}
              notes={notes}
              isExpanded={expandedFolders.includes(subfolder.id)}
              onToggle={() => onToggleFolder(subfolder.id)}
              onEditNote={onEditNote}
              onTogglePin={onTogglePin}
              onDeleteNote={onDeleteNote}
              pinnedIds={pinnedIds}
              onEditFolder={onEditFolder}
              onDeleteFolder={onDeleteFolder}
              onCreateSubfolder={onCreateSubfolder}
              expandedFolders={expandedFolders}
              onToggleFolder={onToggleFolder}
              depth={depth + 1}
            />
          ))}
          
          {/* Notes in this folder */}
          <div ref={setNodeRef} className={`folder-notes ${isOver ? 'drop-zone-active' : ''}`}>
            {folderNotes.map(note => (
              <DraggableNote
                key={note.id}
                note={note}
                onEdit={onEditNote}
                onTogglePin={onTogglePin}
                onDelete={onDeleteNote}
                isPinned={pinnedIds.includes(note.id)}
              />
            ))}
            {folderNotes.length === 0 && folder.children.length === 0 && (
              <div className="empty-folder">No notes or subfolders</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// Droppable Unfiled Notes Section Component
const UnfiledNotesSection: React.FC<{
  notes: Note[];
  isExpanded: boolean;
  onToggle: () => void;
  onEditNote: (note: Note) => void;
  onTogglePin: (id: number) => void;
  onDeleteNote: (id: number) => void;
  pinnedIds: number[];
}> = ({ notes, isExpanded, onToggle, onEditNote, onTogglePin, onDeleteNote, pinnedIds }) => {
  const { isOver, setNodeRef } = useDroppable({
    id: 'unfiled',
  });

  return (
    <div className="folder-section">
      <div 
        className={`folder-header root-folder ${isOver ? 'drag-over' : ''}`}
        onClick={onToggle}
      >
        <span className="folder-toggle">
          <IconDisplay icon={isExpanded ? '📂' : '📁'} />
        </span>
        <span className="folder-name">Unfiled Notes ({notes.length})</span>
      </div>
      
      {isExpanded && (
        <div ref={setNodeRef} className={`folder-notes ${isOver ? 'drop-zone-active' : ''}`}>
          {notes.map(note => (
            <DraggableNote
              key={note.id}
              note={note}
              onEdit={onEditNote}
              onTogglePin={onTogglePin}
              onDelete={onDeleteNote}
              isPinned={pinnedIds.includes(note.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const API_BASE = '/api';

function App() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<{ message: string; type?: 'success' | 'error' } | null>(null);
  const [search, setSearch] = useState('');
  const [editingNote, setEditingNote] = useState<Note | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<{ open: boolean; noteId: number | null }>({ open: false, noteId: null });
  const [darkMode, setDarkMode] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [pinnedIds, setPinnedIds] = useState<number[]>(() => {
    const saved = localStorage.getItem('pinned');
    return saved ? JSON.parse(saved) : [];
  });
  const [activeTag,setActiveTag]=useState<string|undefined>();
  const [showCreateFolder, setShowCreateFolder] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [newFolderIcon, setNewFolderIcon] = useState('📁');
  const [expandedFolders, setExpandedFolders] = useState<number[]>([]);
  const [isUnfiledExpanded, setIsUnfiledExpanded] = useState(false);
  const [draggedNote, setDraggedNote] = useState<Note | null>(null);
  const [editingFolder, setEditingFolder] = useState<Folder | null>(null);
  const [confirmDeleteFolder, setConfirmDeleteFolder] = useState<{ open: boolean; folderId: number | null }>({ open: false, folderId: null });

  // DnD Kit sensors
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  // Debug log
  console.log('App rendering, notes:', notes.length, 'loading:', loading);

  useEffect(() => {
    document.body.classList.toggle('dark', darkMode);
  }, [darkMode]);

  useEffect(() => {
    localStorage.setItem('pinned', JSON.stringify(pinnedIds));
  }, [pinnedIds]);

  const togglePin = (id: number) => {
    setPinnedIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };

  const fetchNotes = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/notes`);
      if (!res.ok) throw new Error('Failed to fetch notes');
      const data = await res.json();
      setNotes(data);
    } catch (err: any) {
      setToast({ message: err.message, type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const fetchFolders = async () => {
    try {
      const res = await fetch(`${API_BASE}/folders`);
      if (!res.ok) throw new Error('Failed to fetch folders');
      const data = await res.json();
      setFolders(data);
    } catch (err: any) {
      setToast({ message: err.message, type: 'error' });
    }
  };

  const createFolder = async (name: string, color: string = '#6366f1', icon: string = '📁', parent_id?: number) => {
    try {
      const res = await fetch(`${API_BASE}/folders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, color, icon, parent_id }),
      });
      if (!res.ok) throw new Error('Failed to create folder');
      fetchFolders();
    } catch (err: any) {
      setToast({ message: err.message, type: 'error' });
    }
  };

  const updateFolder = async (folderId: number, name: string, color: string, icon: string, parent_id?: number) => {
    try {
      const res = await fetch(`${API_BASE}/folders/${folderId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, color, icon, parent_id }),
      });
      if (!res.ok) throw new Error('Failed to update folder');
      fetchFolders();
      setEditingFolder(null);
    } catch (err: any) {
      setToast({ message: err.message, type: 'error' });
    }
  };

  const deleteFolder = async (folderId: number) => {
    try {
      const res = await fetch(`${API_BASE}/folders/${folderId}`, {
        method: 'DELETE',
      });
      if (!res.ok) throw new Error('Failed to delete folder');
      fetchFolders();
      fetchNotes(); // Refresh notes to show updated folder assignments
    } catch (err: any) {
      setToast({ message: err.message, type: 'error' });
    }
  };

  const handleDeleteFolder = (folderId: number) => {
    setConfirmDeleteFolder({ open: true, folderId });
  };

  const confirmFolderDelete = async () => {
    if (!confirmDeleteFolder.folderId) return;
    await deleteFolder(confirmDeleteFolder.folderId);
    setConfirmDeleteFolder({ open: false, folderId: null });
  };

  useEffect(() => {
    fetchNotes();
    fetchFolders();
  }, []);

  const handleAddOrEdit = async (note: {title:string;content:string;tags:string[];color:string;folder_id?:number;id?:number})=>{
    setToast(null);
    try {
      if (editingNote) {
        // Edit
        const res = await fetch(`${API_BASE}/notes/${note.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: note.title, content: note.content, tags: note.tags, color: note.color, folder_id: note.folder_id }),
        });
        if (!res.ok) throw new Error('Failed to update note');
        setToast({ message: 'Note updated!', type: 'success' });
        setEditingNote(null);
      } else {
        // Add
      const res = await fetch(`${API_BASE}/notes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: note.title, content: note.content, tags: note.tags, color: note.color, folder_id: note.folder_id }),
      });
      if (!res.ok) throw new Error('Failed to add note');
        setToast({ message: 'Note added!', type: 'success' });
      }
      fetchNotes();
    } catch (err: any) {
      setToast({ message: err.message, type: 'error' });
    }
  };

  const handleDelete = (id: number) => {
    setConfirmDelete({ open: true, noteId: id });
  };

  const confirmDeleteNote = async () => {
    if (!confirmDelete.noteId) return;
    setToast(null);
    try {
      const res = await fetch(`${API_BASE}/notes/${confirmDelete.noteId}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Failed to delete note');
      setToast({ message: 'Note deleted!', type: 'success' });
      fetchNotes();
    } catch (err: any) {
      setToast({ message: err.message, type: 'error' });
    } finally {
      setConfirmDelete({ open: false, noteId: null });
    }
  };

  const allTags=Array.from(new Set(notes.flatMap(n=>n.tags||[]))).sort();

  // Filter notes by search and tags only (not by folder - we'll show all in structure)
  const searchAndTagFilteredNotes = notes.filter(n=> 
    (activeTag? (n.tags||[]).includes(activeTag):true) && 
    ( n.title.toLowerCase().includes(search.toLowerCase()) || n.content.toLowerCase().includes(search.toLowerCase()))
  );

  // Organize folders hierarchically
  const organizeHierarchically = (folders: Folder[]): HierarchicalFolder[] => {
    const folderMap = new Map<number, HierarchicalFolder>();
    const rootFolders: HierarchicalFolder[] = [];
    
    // Initialize all folders with children array
    folders.forEach(folder => {
      folderMap.set(folder.id, { ...folder, children: [] });
    });
    
    // Build hierarchy
    folders.forEach(folder => {
      const folderWithChildren = folderMap.get(folder.id)!;
      if (folder.parent_id && folderMap.has(folder.parent_id)) {
        folderMap.get(folder.parent_id)!.children.push(folderWithChildren);
      } else {
        rootFolders.push(folderWithChildren);
      }
    });
    
    return rootFolders;
  };

  const hierarchicalFolders = organizeHierarchically(folders);
  
  // State for creating subfolder
  const [creatingSubfolderFor, setCreatingSubfolderFor] = useState<number | null>(null);

  const handleCreateSubfolder = (parentId: number) => {
    setCreatingSubfolderFor(parentId);
    setShowCreateFolder(true);
  };

  const handleCreateFolder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newFolderName.trim()) {
      await createFolder(newFolderName.trim(), '#6366f1', newFolderIcon, creatingSubfolderFor || undefined);
      setNewFolderName('');
      setNewFolderIcon('📁');
      setShowCreateFolder(false);
      setCreatingSubfolderFor(null);
    }
  };

  // Group notes by folder for hierarchical display
  const notesWithoutFolder = searchAndTagFilteredNotes.filter(n => n.folder_id === null || n.folder_id === undefined);

  const toggleFolder = (folderId: number) => {
    setExpandedFolders(prev => 
      prev.includes(folderId) 
        ? prev.filter(id => id !== folderId)
        : [...prev, folderId]
    );
  };

  const handleDragStart = (event: DragStartEvent) => {
    const noteId = parseInt(event.active.id as string);
    const note = notes.find(n => n.id === noteId);
    setDraggedNote(note || null);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setDraggedNote(null);

    if (!over) return;

    const noteId = parseInt(active.id as string);
    const note = notes.find(n => n.id === noteId);
    if (!note) return;

    // Extract folder ID from droppable ID
    let targetFolderId: number | null = null;
    const dropId = over.id as string;
    
    if (dropId === 'unfiled') {
      targetFolderId = null;
    } else if (dropId.startsWith('folder-')) {
      targetFolderId = parseInt(dropId.replace('folder-', ''));
    }

    // Don't update if dropping in the same folder
    if (note.folder_id === targetFolderId) return;

    try {
      // Update note's folder
      const res = await fetch(`${API_BASE}/notes/${noteId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          title: note.title, 
          content: note.content, 
          tags: note.tags, 
          color: note.color, 
          folder_id: targetFolderId 
        }),
      });
      
      if (!res.ok) throw new Error('Failed to move note');
      
      // Update local state immediately for snappy UI
      setNotes(prev => prev.map(n => 
        n.id === noteId ? { ...n, folder_id: targetFolderId || undefined } : n
      ));
      
      setToast({ 
        message: targetFolderId 
          ? `Note moved to ${folders.find(f => f.id === targetFolderId)?.name || 'folder'}!`
          : 'Note moved to unfiled!', 
        type: 'success' 
      });
    } catch (err: any) {
      setToast({ message: err.message, type: 'error' });
    }
  };

  return (
    <div className={`layout${darkMode ? ' dark' : ''}`}>
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        {/* Sidebar */}
        <aside className={`sidebar${sidebarOpen ? ' open' : ''}`}>
          <SearchBar value={search} onChange={setSearch} />
          
          {/* Tags */}
          {allTags.length > 0 && (
            <div className="chip-bar">
              {allTags.map(t => (
                <span
                  key={t}
                  className={`chip ${activeTag === t ? 'active' : ''}`}
                  onClick={() => setActiveTag(prev => prev === t ? undefined : t)}
                >
                  {t}
                </span>
              ))}
              {activeTag && (
                <span className="chip clear" onClick={() => setActiveTag(undefined)}>
                  Clear
                </span>
              )}
            </div>
          )}

          {/* Notes structure */}
          <div className="notes-structure">
            <div className="section-header">
              <h4>Notes</h4>
              <button 
                className="add-folder-btn"
                onClick={() => setShowCreateFolder(!showCreateFolder)}
                title="Add Folder"
              >
                +
              </button>
            </div>

            {showCreateFolder && (
              <form onSubmit={handleCreateFolder} className="create-folder-form">
                <h4>{creatingSubfolderFor ? 'Create Subfolder' : 'Create Folder'}</h4>
                <input
                  type="text"
                  value={newFolderName}
                  onChange={(e) => setNewFolderName(e.target.value)}
                  placeholder={creatingSubfolderFor ? 'Subfolder name' : 'Folder name'}
                  className="folder-name-input"
                  autoFocus
                />
                
                <div className="icon-picker-section">
                  <label className="icon-picker-label">Choose Icon:</label>
                  <div className="icon-picker-grid">
                    {FOLDER_ICONS.map(icon => (
                      <button
                        key={icon}
                        type="button"
                        className={`icon-picker-btn ${newFolderIcon === icon ? 'selected' : ''}`}
                        onClick={() => setNewFolderIcon(icon)}
                        style={{
                          backgroundColor: newFolderIcon === icon ? '#eff6ff' : '#f8f9fa',
                          border: newFolderIcon === icon ? '2px solid #6366f1' : '2px solid #e5e7eb',
                          minHeight: '40px',
                          minWidth: '40px',
                          fontSize: '16px',
                          fontWeight: 'bold',
                          color: '#374151'
                        }}
                        title={`Icon: ${icon}`}
                      >
                        <IconDisplay icon={icon} />
                      </button>
                    ))}
                  </div>
                </div>
                
                <div className="folder-form-actions">
                  <button type="submit" className="create-btn">Create</button>
                  <button 
                    type="button" 
                    onClick={() => {
                      setShowCreateFolder(false);
                      setNewFolderName('');
                      setNewFolderIcon('📁');
                      setCreatingSubfolderFor(null);
                    }} 
                    className="cancel-btn"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}

            <div className="notes-tree">
              {/* Unfiled notes */}
              {notesWithoutFolder.length > 0 && (
                <UnfiledNotesSection 
                  notes={notesWithoutFolder}
                  isExpanded={isUnfiledExpanded}
                  onToggle={() => setIsUnfiledExpanded(!isUnfiledExpanded)}
                  onEditNote={setEditingNote}
                  onTogglePin={togglePin}
                  onDeleteNote={handleDelete}
                  pinnedIds={pinnedIds}
                />
              )}

              {/* Folders */}
              {hierarchicalFolders.map(folder => (
                <div key={folder.id}>
                  {editingFolder && editingFolder.id === folder.id ? (
                    <FolderEditForm
                      folder={folder}
                      onSave={updateFolder}
                      onCancel={() => setEditingFolder(null)}
                    />
                  ) : (
                    <HierarchicalFolderSection
                      folder={folder}
                      notes={notes}
                      isExpanded={expandedFolders.includes(folder.id)}
                      onToggle={() => toggleFolder(folder.id)}
                      onEditNote={setEditingNote}
                      onTogglePin={togglePin}
                      onDeleteNote={handleDelete}
                      pinnedIds={pinnedIds}
                      onEditFolder={setEditingFolder}
                      onDeleteFolder={handleDeleteFolder}
                      onCreateSubfolder={handleCreateSubfolder}
                      expandedFolders={expandedFolders}
                      onToggleFolder={toggleFolder}
                      depth={0}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        </aside>

        <DragOverlay>
          {draggedNote ? (
            <div className="drag-overlay-note">
              <h5>{draggedNote.title}</h5>
              <p>{draggedNote.content.substring(0, 50)}...</p>
            </div>
          ) : null}
        </DragOverlay>
      </DndContext>

      {/* Hamburger for mobile */}
      <button className="hamburger" onClick={()=>setSidebarOpen(o=>!o)} aria-label="Toggle sidebar">☰</button>

      {/* Main content */}
      <main className="editor">
        <div className="page-content">
          {editingNote ? (
            <>
              <div className="editor-header">
                <h1>Edit Note</h1>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <button 
                    onClick={() => setDarkMode(!darkMode)}
                    className="dark-mode-toggle"
                    title="Toggle dark mode"
                    style={{
                      background: 'none',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      padding: '0.5rem',
                      cursor: 'pointer',
                      fontSize: '1.2rem'
                    }}
                  >
                    {darkMode ? '☀️' : '🌙'}
                  </button>
                  <button 
                    className="cancel-edit-btn" 
                    onClick={() => setEditingNote(null)}
                    aria-label="Cancel editing"
                  >
                    ✕
                  </button>
                </div>
              </div>
              
              <NoteForm 
                onSubmit={handleAddOrEdit} 
                editingNote={editingNote}
                folders={folders}
                key={editingNote?.id || 'new'} 
              />
            </>
          ) : (
            <>
              <div className="editor-header">
                <h1>Create New Note</h1>
                <button 
                  onClick={() => setDarkMode(!darkMode)}
                  className="dark-mode-toggle"
                  title="Toggle dark mode"
                  style={{
                    background: 'none',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    padding: '0.5rem',
                    cursor: 'pointer',
                    fontSize: '1.2rem'
                  }}
                >
                  {darkMode ? '☀️' : '🌙'}
                </button>
              </div>
              
              <NoteForm 
                onSubmit={handleAddOrEdit} 
                editingNote={null}
                folders={folders}
                key="new" 
              />
              
              {notes.length > 0 && (
                <div className="recent-notes-section">
                  <h3>Recent Notes</h3>
                  <div className="recent-notes-grid">
                    {notes.slice(0, 6).map(note => (
                      <div 
                        key={note.id}
                        className="recent-note-card"
                        onClick={() => setEditingNote(note)}
                        style={{borderLeft: `4px solid ${note.color || '#6366f1'}`}}
                      >
                        <h4>{note.title}</h4>
                        <p>{note.content.substring(0, 100)}{note.content.length > 100 ? '...' : ''}</p>
                        {note.tags && note.tags.length > 0 && (
                          <div className="recent-note-tags">
                            {note.tags.slice(0, 3).map(tag => (
                              <span key={tag} className="recent-tag">{tag}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      {/* Toast and dialogs */}
      <Toast message={toast?.message || ''} type={toast?.type} onClose={()=>setToast(null)} />
      <ConfirmDialog 
        open={confirmDelete.open} 
        message="Are you sure you want to delete this note?" 
        onConfirm={confirmDeleteNote} 
        onCancel={()=>setConfirmDelete({open:false,noteId:null})} 
      />
      <ConfirmDialog 
        open={confirmDeleteFolder.open} 
        message="Are you sure you want to delete this folder? All notes will be moved to unfiled." 
        onConfirm={confirmFolderDelete} 
        onCancel={()=>setConfirmDeleteFolder({open:false,folderId:null})} 
      />
    </div>
  );
}

export default App;
