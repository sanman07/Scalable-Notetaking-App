import React, { useEffect, useState } from "react";
import { BlockNoteViewRaw as BlockNoteView, useBlockNote } from "@blocknote/react";
import { blocksToMarkdown, markdownToBlocks } from "@blocknote/core";
import "@blocknote/core/style.css";

type Props = {
  markdown: string;
  onChange: (markdown: string) => void;
};

const BlockNoteEditor: React.FC<Props> = ({ markdown, onChange }) => {
  const [error, setError] = useState<string | null>(null);
  
  // Fallback to textarea if BlockNote fails
  if (error) {
    return (
      <div>
        <textarea
          value={markdown}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Content (supports Markdown)"
          rows={6}
          style={{
            width: '100%',
            padding: '0.75rem',
            borderRadius: '8px',
            border: '1.5px solid #e0e0e0',
            fontFamily: 'inherit',
            fontSize: '14px',
            resize: 'vertical'
          }}
        />
        <small style={{ color: '#999', fontSize: '12px' }}>
          BlockNote editor failed to load. Using fallback textarea. Error: {error}
        </small>
      </div>
    );
  }

  try {
    const editor = useBlockNote({ 
      initialContent: [],
      // Add more conservative options
      animations: false
    });

    /* Fire on every change */
    useEffect(() => {
      try {
        return editor.onChange(async () => {
          const blocks = editor.document;
          const markdownOutput = await blocksToMarkdown(blocks, editor.pmSchema, editor, {});
          onChange(markdownOutput);
        });
      } catch (err) {
        console.error('BlockNote onChange error:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      }
    }, [editor, onChange]);

    /* Import markdown you pass in (edit-note case) */
    useEffect(() => {
      try {
        if (markdown && markdown.trim()) {
          markdownToBlocks(markdown, editor.pmSchema).then((blocks) => {
            // Use any type to bypass the complex type mismatch
            editor.replaceBlocks(editor.document, blocks as any);
          }).catch(err => {
            console.error('BlockNote markdown import error:', err);
            // Don't set error here, just log it
          });
        }
      } catch (err) {
        console.error('BlockNote useEffect error:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      }
    }, [markdown, editor]);

    return (
      <div className="blocknote-wrapper">
        <BlockNoteView editor={editor} />
      </div>
    );
  } catch (err) {
    console.error('BlockNote initialization error:', err);
    setError(err instanceof Error ? err.message : 'Failed to initialize BlockNote');
    return null; // Will trigger re-render with error fallback
  }
};

export default BlockNoteEditor;
