import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import type { Note } from './NoteCard';

interface NoteFormProps {
  onSubmit: (note: { title: string; content: string; tags: string[]; color: string; folder_id?: number; id?: number }) => void;
  editingNote?: Note | null;
  folders: Array<{ id: number; name: string; color: string; icon?: string }>;
}

// Slash command definitions
const SLASH_COMMANDS = [
  { label: 'Heading 1', description: 'Large section heading', action: 'h1', icon: 'H1' },
  { label: 'Heading 2', description: 'Medium section heading', action: 'h2', icon: 'H2' },
  { label: 'Heading 3', description: 'Small section heading', action: 'h3', icon: 'H3' },
  { label: 'Bold', description: 'Make text bold', action: 'bold', icon: 'B' },
  { label: 'Italic', description: 'Make text italic', action: 'italic', icon: 'I' },
  { label: 'Inline Code', description: 'Inline code formatting', action: 'code', icon: '</>' },
  { label: 'Code Block', description: 'Multi-line code with syntax highlighting', action: 'codeblock', icon: '{}' },
  { label: 'Quote', description: 'Create a quote block', action: 'quote', icon: '❝' },
  { label: 'Bullet List', description: 'Create a bulleted list', action: 'bullet', icon: '•' },
  { label: 'Numbered List', description: 'Create a numbered list', action: 'numbered', icon: '1.' },
];

// Programming languages for code blocks
const PROGRAMMING_LANGUAGES = [
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'python', label: 'Python' },
  { value: 'java', label: 'Java' },
  { value: 'cpp', label: 'C++' },
  { value: 'c', label: 'C' },
  { value: 'csharp', label: 'C#' },
  { value: 'php', label: 'PHP' },
  { value: 'ruby', label: 'Ruby' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' },
  { value: 'html', label: 'HTML' },
  { value: 'css', label: 'CSS' },
  { value: 'sql', label: 'SQL' },
  { value: 'bash', label: 'Bash' },
  { value: 'json', label: 'JSON' },
  { value: 'xml', label: 'XML' },
  { value: 'yaml', label: 'YAML' },
  { value: 'markdown', label: 'Markdown' },
  { value: 'plaintext', label: 'Plain Text' },
];

const NoteForm: React.FC<NoteFormProps> = ({ onSubmit, editingNote, folders }) => {
  const [title, setTitle] = useState(editingNote?.title || '');
  const [content, setContent] = useState(editingNote?.content || '');
  const [tags, setTags] = useState<string[]>(editingNote?.tags || []);
  const [color, setColor] = useState(editingNote?.color || '#6366f1');
  const [folderId, setFolderId] = useState<number | undefined>(editingNote?.folder_id);
  const [tagInput, setTagInput] = useState('');

  // Slash menu state
  const [showSlashMenu, setShowSlashMenu] = useState(false);
  const [slashMenuPosition, setSlashMenuPosition] = useState({ top: 0, left: 0 });
  const [selectedCommandIndex, setSelectedCommandIndex] = useState(0);
  const [editorRef, setEditorRef] = useState<HTMLDivElement | null>(null);
  const [showLanguageSelector, setShowLanguageSelector] = useState(false);
  const [languageSelectorPosition, setLanguageSelectorPosition] = useState({ top: 0, left: 0 });
  const [selectedLanguageIndex, setSelectedLanguageIndex] = useState(0);
  const [pendingCodeBlock, setPendingCodeBlock] = useState<HTMLElement | null>(null);

  // Initialize editor content
  useEffect(() => {
    if (editorRef) {
      if (content) {
        editorRef.innerHTML = content;
      } else {
        editorRef.innerHTML = '';
      }
    }
  }, [editorRef]);

  // Update content when editingNote changes
  useEffect(() => {
    if (editingNote) {
      setTitle(editingNote.title || '');
      setContent(editingNote.content || '');
      setTags(editingNote.tags || []);
      setColor(editingNote.color || '#6366f1');
      setFolderId(editingNote.folder_id);
    } else {
      setTitle('');
      setContent('');
      setTags([]);
      setColor('#6366f1');
      setFolderId(undefined);
    }
  }, [editingNote]);

  // Update editor content when content state changes
  useEffect(() => {
    if (editorRef && editorRef.innerHTML !== content) {
      const selection = window.getSelection();
      const range = selection?.rangeCount ? selection.getRangeAt(0) : null;
      const startOffset = range?.startOffset || 0;
      const endOffset = range?.endOffset || 0;
      
      editorRef.innerHTML = content || '';
      
      // Restore cursor position
      if (range && editorRef.firstChild) {
        try {
          const newRange = document.createRange();
          const textNode = editorRef.firstChild;
          const maxOffset = textNode.textContent?.length || 0;
          newRange.setStart(textNode, Math.min(startOffset, maxOffset));
          newRange.setEnd(textNode, Math.min(endOffset, maxOffset));
          selection?.removeAllRanges();
          selection?.addRange(newRange);
        } catch (e) {
          // Ignore range errors
        }
      }
    }
  }, [content, editorRef]);

  const getCaretPosition = () => {
    const selection = window.getSelection();
    if (!selection || !selection.rangeCount) return { x: 0, y: 0 };
    
    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();
    
    return {
      x: rect.left + window.scrollX,
      y: rect.bottom + window.scrollY + 4
    };
  };

  const handleInput = (e: React.FormEvent<HTMLDivElement>) => {
    const element = e.currentTarget;
    const htmlContent = element.innerHTML;
    
    // Remove placeholder if content exists
    if (htmlContent && htmlContent !== '<br>' && !htmlContent.includes('Start typing your note')) {
      setContent(htmlContent);
    } else if (!htmlContent || htmlContent === '<br>') {
      setContent('');
    }
  };

  const handleFocus = (e: React.FocusEvent<HTMLDivElement>) => {
    const element = e.currentTarget;
    // Clear placeholder on focus
    if (element.innerHTML.includes('Start typing your note')) {
      element.innerHTML = '';
      setContent('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    const element = e.currentTarget;
    
    // Clear placeholder if user starts typing
    if (element.innerHTML.includes('Start typing your note')) {
      element.innerHTML = '';
      setContent('');
    }

    // Check if cursor is in a code block
    const selection = window.getSelection();
    if (selection && selection.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      let currentNode = range.startContainer;
      
      // Find if we're inside a code block
      let codeBlock: HTMLElement | null = null;
      let preBlock: HTMLElement | null = null;
      
      while (currentNode && currentNode !== element) {
        if (currentNode.nodeType === Node.ELEMENT_NODE) {
          const elem = currentNode as HTMLElement;
          if (elem.tagName === 'CODE' && elem.parentElement?.tagName === 'PRE') {
            codeBlock = elem;
            preBlock = elem.parentElement;
            break;
          }
          if (elem.tagName === 'PRE') {
            preBlock = elem;
            codeBlock = elem.querySelector('code');
            break;
          }
        }
        currentNode = currentNode.parentNode as Node;
      }

      // Handle escape from code block
      if (codeBlock && preBlock && (e.key === 'Enter' && (e.ctrlKey || e.metaKey))) {
        e.preventDefault();
        exitCodeBlock(preBlock);
        return;
      }
      
      // Handle double Enter to exit code block
      if (codeBlock && preBlock && e.key === 'Enter') {
        const cursorPosition = range.startOffset;
        const textContent = codeBlock.textContent || '';
        const beforeCursor = textContent.substring(0, cursorPosition);
        const afterCursor = textContent.substring(cursorPosition);
        
        // If user presses Enter on an empty line at the end, exit code block
        if (beforeCursor.endsWith('\n') && afterCursor.trim() === '') {
          e.preventDefault();
          exitCodeBlock(preBlock);
          return;
        }
      }

      // Handle arrow down at end of code block
      if (codeBlock && preBlock && e.key === 'ArrowDown') {
        const cursorPosition = range.startOffset;
        const textContent = codeBlock.textContent || '';
        const beforeCursor = textContent.substring(0, cursorPosition);
        
        // If at the very end of the code block
        if (cursorPosition >= textContent.length - 1) {
          const lines = textContent.split('\n');
          const currentLineIndex = beforeCursor.split('\n').length - 1;
          
          // If on the last line, exit code block
          if (currentLineIndex >= lines.length - 1) {
            e.preventDefault();
            exitCodeBlock(preBlock);
            return;
          }
        }
      }
    }
    
    if (showLanguageSelector) {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedLanguageIndex(prev => prev < PROGRAMMING_LANGUAGES.length - 1 ? prev + 1 : 0);
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedLanguageIndex(prev => prev > 0 ? prev - 1 : PROGRAMMING_LANGUAGES.length - 1);
          break;
        case 'Enter':
          e.preventDefault();
          selectLanguage(PROGRAMMING_LANGUAGES[selectedLanguageIndex].value);
          break;
        case 'Escape':
          e.preventDefault();
          setShowLanguageSelector(false);
          setPendingCodeBlock(null);
          break;
      }
    } else if (showSlashMenu) {
      const filteredCommands = getFilteredCommands();
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedCommandIndex(prev => prev < filteredCommands.length - 1 ? prev + 1 : 0);
          // Scroll selected item into view
          setTimeout(() => {
            const menuElement = document.querySelector('.slash-menu');
            const selectedElement = document.querySelector('.slash-menu button:nth-child(' + (selectedCommandIndex + 1) + ')');
            if (menuElement && selectedElement) {
              selectedElement.scrollIntoView({ block: 'nearest' });
            }
          }, 0);
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedCommandIndex(prev => prev > 0 ? prev - 1 : filteredCommands.length - 1);
          // Scroll selected item into view
          setTimeout(() => {
            const menuElement = document.querySelector('.slash-menu');
            const selectedElement = document.querySelector('.slash-menu button:nth-child(' + (selectedCommandIndex + 1) + ')');
            if (menuElement && selectedElement) {
              selectedElement.scrollIntoView({ block: 'nearest' });
            }
          }, 0);
          break;
        case 'Enter':
          e.preventDefault();
          if (filteredCommands.length > 0) {
            executeSlashCommand(filteredCommands[selectedCommandIndex].action);
          }
          break;
        case 'Escape':
          e.preventDefault();
          setShowSlashMenu(false);
          break;
      }
    } else if (e.key === '/') {
      // Show menu after the slash is typed
      setTimeout(() => {
        const position = getCaretPosition();
        setSlashMenuPosition({
          top: position.y,
          left: position.x
        });
        setShowSlashMenu(true);
        setSelectedCommandIndex(0);
      }, 10);
    } else if (e.key === 'Escape') {
      setShowSlashMenu(false);
      setShowLanguageSelector(false);
      setPendingCodeBlock(null);
    }
  };

  const exitCodeBlock = (preBlock: HTMLElement) => {
    if (!editorRef) return;
    
    // Create a new paragraph after the code block
    const newParagraph = document.createElement('p');
    newParagraph.innerHTML = '<br>'; // Empty paragraph with line break
    
    // Insert after the pre block
    if (preBlock.nextSibling) {
      preBlock.parentNode?.insertBefore(newParagraph, preBlock.nextSibling);
    } else {
      preBlock.parentNode?.appendChild(newParagraph);
    }
    
    // Position cursor in the new paragraph
    const selection = window.getSelection();
    if (selection) {
      const range = document.createRange();
      range.setStart(newParagraph, 0);
      range.collapse(true);
      selection.removeAllRanges();
      selection.addRange(range);
    }
    
    // Update content
    setContent(editorRef.innerHTML);
  };

  const getFilteredCommands = () => {
    if (!editorRef) return SLASH_COMMANDS;
    
    const selection = window.getSelection();
    if (!selection || !selection.rangeCount) return SLASH_COMMANDS;
    
    const range = selection.getRangeAt(0);
    const container = range.startContainer;
    
    if (container.nodeType === Node.TEXT_NODE && container.textContent) {
      const text = container.textContent;
      const slashIndex = text.lastIndexOf('/');
      if (slashIndex !== -1) {
        const searchTerm = text.substring(slashIndex + 1, range.startOffset).toLowerCase();
        if (searchTerm) {
          return SLASH_COMMANDS.filter(cmd => 
            cmd.label.toLowerCase().includes(searchTerm) ||
            cmd.description.toLowerCase().includes(searchTerm)
          );
        }
      }
    }
    
    return SLASH_COMMANDS;
  };

  const executeSlashCommand = (action: string) => {
    if (!editorRef) return;
    
    const selection = window.getSelection();
    if (!selection || !selection.rangeCount) return;
    
    const range = selection.getRangeAt(0);
    
    // Find and remove the slash and any text after it
    const container = range.startContainer;
    if (container.nodeType === Node.TEXT_NODE && container.textContent) {
      const text = container.textContent;
      const slashIndex = text.lastIndexOf('/');
      if (slashIndex !== -1) {
        // Create a new range to select and delete the slash and search term
        const deleteRange = document.createRange();
        deleteRange.setStart(container, slashIndex);
        deleteRange.setEnd(container, range.startOffset);
        deleteRange.deleteContents();
        
        // Position cursor where slash was
        range.setStart(container, slashIndex);
        range.collapse(true);
      }
    }

    // Check for existing formatting on the current line/element
    let currentElement = range.startContainer;
    let existingFormatElement: HTMLElement | null = null;
    let listParent: HTMLElement | null = null;
    
    // Traverse up to find existing formatting
    while (currentElement && currentElement !== editorRef) {
      if (currentElement.nodeType === Node.ELEMENT_NODE) {
        const elem = currentElement as HTMLElement;
        const tagName = elem.tagName.toLowerCase();
        
        // Check for list items
        if (tagName === 'li') {
          existingFormatElement = elem;
          listParent = elem.parentElement as HTMLElement;
          break;
        }
        // Check for headings, blockquotes, etc.
        if (['h1', 'h2', 'h3', 'blockquote', 'pre'].includes(tagName)) {
          existingFormatElement = elem;
          break;
        }
      }
      currentElement = currentElement.parentNode as Node;
    }

    // Handle existing formatting removal
    if (existingFormatElement) {
      const textContent = existingFormatElement.textContent || '';
      
      // If we're switching from one list type to another
      if (existingFormatElement.tagName === 'LI' && (action === 'bullet' || action === 'numbered')) {
        const currentListType = listParent?.tagName.toLowerCase();
        const newListType = action === 'bullet' ? 'ul' : 'ol';
        
        // If switching to the same type, do nothing
        if (currentListType === newListType) {
          setShowSlashMenu(false);
          return;
        }
        
        // Create new list with just this item
        const newList = document.createElement(newListType);
        newList.style.margin = '8px 0';
        newList.style.paddingLeft = '20px';
        
        const newLi = document.createElement('li');
        newLi.textContent = textContent;
        newList.appendChild(newLi);
        
        // Replace only the current list item with the new list
        existingFormatElement.parentNode?.replaceChild(newList, existingFormatElement);
        
        // Position cursor in the new list item
        const selection = window.getSelection();
        if (selection) {
          const range = document.createRange();
          range.selectNodeContents(newLi);
          selection.removeAllRanges();
          selection.addRange(range);
        }
        
        setContent(editorRef.innerHTML);
        setShowSlashMenu(false);
        return;
      }
      
      // For other format changes (e.g., heading to list, blockquote to heading)
      if (['h1', 'h2', 'h3', 'blockquote', 'li'].includes(existingFormatElement.tagName.toLowerCase())) {
        // Create text node with the content
        const textNode = document.createTextNode(textContent);
        
        // Replace the formatted element with plain text
        existingFormatElement.parentNode?.replaceChild(textNode, existingFormatElement);
        
        // Position cursor after the text
        const newRange = document.createRange();
        newRange.setStartAfter(textNode);
        newRange.collapse(true);
        selection.removeAllRanges();
        selection.addRange(newRange);
        
        // Now apply the new formatting to this text
        range.setStart(textNode, 0);
        range.setEnd(textNode, textContent.length);
      }
    }
    
    // Apply formatting based on action
    let element: HTMLElement;
    
    switch (action) {
      case 'h1':
        element = document.createElement('h1');
        element.style.fontSize = '24px';
        element.style.fontWeight = 'bold';
        element.style.margin = '16px 0 8px 0';
        element.textContent = existingFormatElement ? (existingFormatElement.textContent || 'Type your heading here') : 'Type your heading here';
        break;
      case 'h2':
        element = document.createElement('h2');
        element.style.fontSize = '20px';
        element.style.fontWeight = 'bold';
        element.style.margin = '14px 0 6px 0';
        element.textContent = existingFormatElement ? (existingFormatElement.textContent || 'Type your heading here') : 'Type your heading here';
        break;
      case 'h3':
        element = document.createElement('h3');
        element.style.fontSize = '18px';
        element.style.fontWeight = 'bold';
        element.style.margin = '12px 0 4px 0';
        element.textContent = existingFormatElement ? (existingFormatElement.textContent || 'Type your heading here') : 'Type your heading here';
        break;
      case 'bold':
        element = document.createElement('strong');
        element.textContent = 'bold text';
        break;
      case 'italic':
        element = document.createElement('em');
        element.textContent = 'italic text';
        break;
      case 'code':
        element = document.createElement('code');
        element.style.fontFamily = 'monospace';
        element.style.backgroundColor = '#f3f4f6';
        element.style.padding = '2px 4px';
        element.style.borderRadius = '3px';
        element.style.border = '1px solid #e5e7eb';
        element.textContent = 'code';
        break;
      case 'codeblock':
        element = document.createElement('pre');
        element.style.backgroundColor = '#f3f4f6';
        element.style.padding = '1rem';
        element.style.borderRadius = '8px';
        element.style.border = '1px solid #e5e7eb';
        element.style.overflowX = 'auto';
        element.style.margin = '16px 0';
        element.style.position = 'relative';
        
        // Insert the pre element first
        range.insertNode(element);
        setPendingCodeBlock(element);
        
        // Show language selector
        const rect = element.getBoundingClientRect();
        setLanguageSelectorPosition({
          top: rect.bottom + window.scrollY + 4,
          left: rect.left + window.scrollX
        });
        setShowLanguageSelector(true);
        setSelectedLanguageIndex(0);
        setShowSlashMenu(false);
        
        // Update content and return early
        setContent(editorRef.innerHTML);
        return;
      case 'quote':
        element = document.createElement('blockquote');
        element.style.fontStyle = 'italic';
        element.style.borderLeft = '4px solid #d1d5db';
        element.style.paddingLeft = '1rem';
        element.style.color = '#6b7280';
        element.style.margin = '8px 0';
        element.textContent = existingFormatElement ? (existingFormatElement.textContent || 'Type your quote here') : 'Type your quote here';
        break;
      case 'bullet':
        element = document.createElement('ul');
        const li1 = document.createElement('li');
        li1.textContent = existingFormatElement ? (existingFormatElement.textContent || 'List item') : 'List item';
        element.appendChild(li1);
        element.style.margin = '8px 0';
        element.style.paddingLeft = '20px';
        break;
      case 'numbered':
        element = document.createElement('ol');
        const li2 = document.createElement('li');
        li2.textContent = existingFormatElement ? (existingFormatElement.textContent || 'List item') : 'List item';
        element.appendChild(li2);
        element.style.margin = '8px 0';
        element.style.paddingLeft = '20px';
        break;
      default:
        return;
    }
    
    if (element) {
      range.insertNode(element);
      
      // Select the text content for easy replacement
      const newRange = document.createRange();
      if (element.tagName === 'UL' || element.tagName === 'OL') {
        // For lists, select the text in the first li element
        const firstLi = element.querySelector('li');
        if (firstLi && firstLi.firstChild) {
          newRange.selectNodeContents(firstLi);
        }
      } else {
        // For other elements, select all text content
        newRange.selectNodeContents(element);
      }
      
      selection.removeAllRanges();
      selection.addRange(newRange);
    }
    
    // Update content
    setContent(editorRef.innerHTML);
    setShowSlashMenu(false);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    onSubmit({
      id: editingNote?.id,
      title: title.trim(),
      content: content,
      tags,
      color,
      folder_id: folderId,
    });

    if (!editingNote) {
      setTitle('');
      setContent('');
      setTags([]);
      setColor('#6366f1');
      setFolderId(undefined);
      setTagInput('');
    }
  };

  const handleBlur = () => {
    setTimeout(() => {
      setShowSlashMenu(false);
    }, 150);
  };

  const handleTagInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      e.preventDefault();
      if (!tags.includes(tagInput.trim())) {
        setTags([...tags, tagInput.trim()]);
      }
      setTagInput('');
    } else if (e.key === 'Backspace' && !tagInput && tags.length > 0) {
      setTags(tags.slice(0, -1));
    }
  };

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const selectLanguage = (language: string) => {
    if (!pendingCodeBlock || !editorRef) return;
    
    // Create the code block with language
    const codeElement = document.createElement('code');
    codeElement.style.fontFamily = '"JetBrains Mono", "SF Mono", "Consolas", monospace';
    codeElement.style.fontSize = '14px';
    codeElement.style.lineHeight = '1.4';
    codeElement.style.display = 'block';
    codeElement.style.whiteSpace = 'pre';
    codeElement.style.tabSize = '2';
    codeElement.setAttribute('data-language', language);
    codeElement.textContent = `// ${PROGRAMMING_LANGUAGES.find(l => l.value === language)?.label || 'Code'}\n\n`;
    
    // Add language header
    const languageHeader = document.createElement('div');
    languageHeader.style.backgroundColor = '#e5e7eb';
    languageHeader.style.color = '#374151';
    languageHeader.style.padding = '0.5rem 1rem';
    languageHeader.style.fontSize = '12px';
    languageHeader.style.fontWeight = '500';
    languageHeader.style.borderBottom = '1px solid #d1d5db';
    languageHeader.style.fontFamily = 'Inter, system-ui, sans-serif';
    languageHeader.textContent = PROGRAMMING_LANGUAGES.find(l => l.value === language)?.label || 'Code';
    
    // Insert header before code
    pendingCodeBlock.insertBefore(languageHeader, pendingCodeBlock.firstChild);
    pendingCodeBlock.appendChild(codeElement);
    
    // Position cursor in the code block
    const selection = window.getSelection();
    if (selection) {
      const range = document.createRange();
      range.setStart(codeElement.firstChild!, codeElement.textContent!.length);
      range.collapse(true);
      selection.removeAllRanges();
      selection.addRange(range);
    }
    
    // Update content and clean up
    setContent(editorRef.innerHTML);
    setShowLanguageSelector(false);
    setPendingCodeBlock(null);
  };

  return (
    <form onSubmit={handleSubmit} className="note-form vertical">
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Note title..."
        required
      />

      <div className="rich-text-editor">
        <div
          ref={setEditorRef}
          contentEditable
          suppressContentEditableWarning={true}
          onInput={handleInput}
          onFocus={handleFocus}
          onKeyDown={handleKeyDown}
          onBlur={handleBlur}
          className="rich-text-editor-content"
          style={{
            width: '100%',
            minHeight: '300px',
            padding: '1rem',
            margin: 0,
            border: '2px solid #e2e8f0',
            borderRadius: '8px',
            outline: 'none',
            fontFamily: '"JetBrains Mono", "SF Mono", "Consolas", "DejaVu Sans Mono", monospace',
            fontSize: '15px',
            fontWeight: '400',
            lineHeight: '1.6',
            color: '#374151',
            background: 'white',
            boxSizing: 'border-box',
            letterSpacing: 'normal',
            wordSpacing: 'normal',
            textAlign: 'left',
            verticalAlign: 'baseline',
            overflow: 'auto',
            whiteSpace: 'pre-wrap',
            wordWrap: 'break-word'
          }}
          data-placeholder={content ? '' : "Start typing your note or use '/' for formatting..."}
        />

        {showSlashMenu && typeof document !== 'undefined' && 
          ReactDOM.createPortal(
            <div 
              className="slash-menu" 
              style={{
              position: 'fixed',
              top: slashMenuPosition.top,
              left: slashMenuPosition.left,
              zIndex: 99999,
              backgroundColor: 'white',
              border: '1px solid #e2e8f0',
                borderRadius: '8px',
                boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                minWidth: '200px',
                maxWidth: '250px',
                maxHeight: '200px',
                overflow: 'auto',
              fontFamily: 'Inter, system-ui, sans-serif'
              }}
            >
              {(() => {
                const filteredCommands = getFilteredCommands();
                return filteredCommands.length > 0 ? filteredCommands.map((command, index) => (
                  <button
                    key={command.action}
                    type="button"
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      width: '100%',
                      padding: '8px 12px',
                      border: 'none',
                      backgroundColor: index === selectedCommandIndex ? '#f0f9ff' : 'white',
                      cursor: 'pointer',
                      fontSize: '13px',
                      textAlign: 'left',
                      transition: 'background-color 0.15s ease',
                    }}
                    onMouseDown={(e) => e.preventDefault()}
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      executeSlashCommand(command.action);
                    }}
                    onMouseEnter={() => setSelectedCommandIndex(index)}
                  >
                    <div style={{ 
                      marginRight: '8px', 
                      fontSize: '14px',
                      minWidth: '20px',
                      textAlign: 'center'
                    }}>
                      {command.icon}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ 
                        fontWeight: '500', 
                        color: '#111827',
                        fontSize: '13px'
                      }}>
                        {command.label}
                      </div>
                      <div style={{ 
                        fontSize: '11px', 
                        color: '#6b7280',
                        lineHeight: '1.3'
                      }}>
                        {command.description}
                      </div>
                    </div>
                  </button>
                )) : (
                  <div style={{
                    padding: '12px',
                    textAlign: 'center',
                    color: '#6b7280',
                    fontSize: '12px',
                    fontStyle: 'italic'
                  }}>
                    No commands found
                  </div>
                );
              })()}
            </div>,
            document.body
          )
        }

        {showLanguageSelector && typeof document !== 'undefined' && 
          ReactDOM.createPortal(
            <div 
              className="language-selector" 
              style={{
                position: 'fixed',
                top: languageSelectorPosition.top,
                left: languageSelectorPosition.left,
                zIndex: 99999,
                backgroundColor: 'white',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                minWidth: '200px',
                maxWidth: '250px',
                maxHeight: '300px',
                overflow: 'auto',
                fontFamily: 'Inter, system-ui, sans-serif'
              }}
            >
              <div style={{
                padding: '8px 12px',
                borderBottom: '1px solid #e5e7eb',
                fontSize: '12px',
                fontWeight: '600',
                color: '#6b7280',
                backgroundColor: '#f8fafc'
              }}>
                Select Language
              </div>
              {PROGRAMMING_LANGUAGES.map((language, index) => (
                <button
                  key={language.value}
                  type="button"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    width: '100%',
                    padding: '8px 12px',
                    border: 'none',
                    backgroundColor: index === selectedLanguageIndex ? '#f0f9ff' : 'white',
                    cursor: 'pointer',
                    fontSize: '13px',
                    textAlign: 'left',
                    transition: 'background-color 0.15s ease',
                  }}
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    selectLanguage(language.value);
                  }}
                  onMouseEnter={() => setSelectedLanguageIndex(index)}
                >
                  <div style={{ 
                    marginRight: '8px', 
                    fontSize: '14px',
                    minWidth: '20px',
                    textAlign: 'center'
                  }}>
                    📄
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ 
                      fontWeight: '500', 
                      color: '#111827',
                      fontSize: '13px'
                    }}>
                      {language.label}
                    </div>
                  </div>
                </button>
              ))}
            </div>,
            document.body
          )
        }
      </div>

      <div className="form-controls">
        <div className="tag-input-container">
          <div className="tags-display">
            {tags.map(tag => (
              <span key={tag} className="tag-chip">
                {tag}
                <button type="button" onClick={() => removeTag(tag)} className="tag-remove">×</button>
              </span>
            ))}
          </div>
          <input
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={handleTagInputKeyDown}
            placeholder="Add tags (press Enter)..."
          />
        </div>

        <div className="color-picker">
          {['#6366f1', '#ec4899', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#f97316', '#06b6d4'].map(c => (
            <span
              key={c}
              style={{ 
                backgroundColor: c, 
                border: color === c ? '3px solid #374151' : '3px solid transparent',
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                cursor: 'pointer',
                display: 'inline-block',
                margin: '0 4px'
              }}
              onClick={() => setColor(c)}
            />
          ))}
        </div>

        <select 
          value={folderId || ''} 
          onChange={(e) => setFolderId(e.target.value ? Number(e.target.value) : undefined)}
          className="folder-select"
        >
          <option value="">No Folder</option>
          {folders.map(folder => (
            <option key={folder.id} value={folder.id}>{folder.icon || '📁'} {folder.name}</option>
          ))}
        </select>

        <button type="submit">
          {editingNote ? 'Update Note' : 'Save Note'}
        </button>
      </div>
    </form>
  );
};

export default NoteForm;
