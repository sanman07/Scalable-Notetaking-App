import React from 'react';

interface ConfirmDialogProps {
  open: boolean;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

const ConfirmDialog: React.FC<ConfirmDialogProps> = ({ open, message, onConfirm, onCancel }) => {
  if (!open) return null;
  return (
    <div className="confirm-dialog-backdrop">
      <div className="confirm-dialog">
        <p>{message}</p>
        <button onClick={onConfirm} className="confirm-btn">Yes</button>
        <button onClick={onCancel} className="cancel-btn">No</button>
      </div>
    </div>
  );
};

export default ConfirmDialog; 