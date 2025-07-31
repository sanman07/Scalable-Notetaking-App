import React, { useState, useRef, useEffect } from 'react';
import type { Note } from './NoteCard';
import ReactDOM from 'react-dom';

interface NoteFormProps {
  onSubmit: (note: { title: string; content: string; tags: string[]; color: string; folder_id?: number; id?: number }) => void;
  editingNote?: Note | null;
  folders: Array<{ id: number; name: string; color: string; icon?: string }>;
}

// Rich text formatting interface
interface RichTextSegment {
  text: string;
  style: {
    bold?: boolean;
    italic?: boolean;
    code?: boolean;
    heading?: 1 | 2 | 3;
    quote?: boolean;
    listType?: 'bullet' | 'numbered';
    color?: string;
  };
}

// Enhanced note content interface that tracks both text and formatting
interface RichContent {
  lines: RichTextSegment[];
}

// Slash command definitions
const SLASH_COMMANDS = [
  { label: 'Heading 1', description: 'Large section heading', action: 'h1', icon: 'H1' },
  { label: 'Heading 2', description: 'Medium section heading', action: 'h2', icon: 'H2' },
  { label: 'Heading 3', description: 'Small section heading', action: 'h3', icon: 'H3' },
  { label: 'Bold', description: 'Make text bold', action: 'bold', icon: 'B' },
  { label: 'Italic', description: 'Make text italic', action: 'italic', icon: 'I' },
  { label: 'Code', description: 'Inline code formatting', action: 'code', icon: '</>' },
  { label: 'Quote', description: 'Create a quote block', action: 'quote', icon: '❝' },
  { label: 'Bullet List', description: 'Create a bulleted list', action: 'bullet', icon: '•' },
  { label: 'Numbered List', description: 'Create a numbered list', action: 'numbered', icon: '1.' },
];

const NoteForm = ({ onSubmit, editingNote, folders }: NoteFormProps) => {
  const [title, setTitle] = useState(editingNote?.title || '');
  const [content, setContent] = useState(editingNote?.content || '');
  const [tags, setTags] = useState<string[]>(editingNote?.tags || []);
  const [color, setColor] = useState(editingNote?.color || '#6366f1');
  const [folderId, setFolderId] = useState<number | undefined>(editingNote?.folder_id);
  const [tagInput, setTagInput] = useState('');

  // Rich text editor state
  const [richContent, setRichContent] = useState<RichContent>({ lines: [] });
  const [showSlashMenu, setShowSlashMenu] = useState(false);
  const [slashMenuPosition, setSlashMenuPosition] = useState({ top: 0, left: 0 });
  const [selectedCommandIndex, setSelectedCommandIndex] = useState(0);
  const [isExecutingSlashCommand, setIsExecutingSlashCommand] = useState(false);
  const [preservedContent, setPreservedContent] = useState<string>('');

  const editorRef = useRef<HTMLDivElement>(null);

  // Convert plain text to rich content on edit
  useEffect(() => {
    if (editingNote && editingNote.content) {
      // Convert existing content to rich text segments
      const segments: RichTextSegment[] = editingNote.content.split('\n').map(line => ({
        text: line,
        style: {}
      }));
      setRichContent({ lines: segments });
    }
  }, [editingNote]);

  // Simplified inline formatting parser that doesn't interfere with display
  const parseInlineFormatting = (text: string): { displayText: string; hasFormatting: boolean; style: RichTextSegment['style'] } => {
    // Check for inline code first (highest priority)
    const codeMatch = text.match(/^`([^`]*)`$/);
    if (codeMatch) {
      return { displayText: codeMatch[1], hasFormatting: true, style: { code: true } };
    }
    
    // Check for bold formatting
    const boldMatch = text.match(/^\*\*([^*]*)\*\*$/);
    if (boldMatch) {
      return { displayText: boldMatch[1], hasFormatting: true, style: { bold: true } };
    }
    
    // Check for italic formatting
    const italicMatch = text.match(/^_([^_]*)_$/);
    if (italicMatch) {
      return { displayText: italicMatch[1], hasFormatting: true, style: { italic: true } };
    }
    
    return { displayText: text, hasFormatting: false, style: {} };
  };

  // Enhanced function to process text with inline formatting
  const processLineWithInlineFormatting = (lineText: string, existingStyle: RichTextSegment['style'] = {}): RichTextSegment => {
    // First check if line has block-level formatting
    if (existingStyle.heading || existingStyle.listType || existingStyle.quote) {
      return { text: lineText, style: existingStyle };
